package handlers

import (
	"context"
	"database/sql"
	"encoding/json"
	"log/slog"
	"net/http"
	"os"
	"strconv"

	"github.com/taskflow/notifications/models"
	"github.com/taskflow/notifications/utils"
)

// NotificationHandler handles HTTP requests for notifications.
type NotificationHandler struct {
	db *sql.DB
}

// NewNotificationHandler creates a handler with an open database connection.
func NewNotificationHandler(db *sql.DB) *NotificationHandler {
	return &NotificationHandler{db: db}
}

// ListNotifications handles GET /notifications.
// PR-05: Contains intentional issues for review testing.
func (h *NotificationHandler) ListNotifications(w http.ResponseWriter, r *http.Request) {
	userIDStr := r.URL.Query().Get("user_id")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil || userID <= 0 {
		writeError(w, http.StatusBadRequest, "user_id must be a positive integer")
		return
	}

	page := queryInt(r, "page", 1)
	perPage := queryInt(r, "per_page", 20)
	if perPage > 100 {
		perPage = 100
	}

	// ISSUE: High — uses context.Background() instead of r.Context().
	// When the HTTP client disconnects, this query will keep running.
	// Fix: replace context.Background() with r.Context() throughout.
	rows, err := h.db.QueryContext(context.Background(),
		`SELECT id, user_id, type, message, read, created_at
		   FROM notifications
		  WHERE user_id = $1
		  ORDER BY created_at DESC`,
		userID,
	)
	if err != nil {
		slog.Error("query notifications failed", "user_id", userID, "err", err)
		writeError(w, http.StatusInternalServerError, "could not fetch notifications")
		return
		// ISSUE: Medium — rows is nil here so there is nothing to close, but
		// in the success branch below, rows is never closed on early error returns
		// because defer was not used.
	}

	var allNotifications []*models.Notification
	for rows.Next() {
		n := &models.Notification{}
		if err := rows.Scan(&n.ID, &n.UserID, &n.Type, &n.Message, &n.Read, &n.CreatedAt); err != nil {
			writeError(w, http.StatusInternalServerError, "could not read notifications")
			return
			// ISSUE: Medium — rows is not closed here; the cursor leaks.
			// Fix: add defer rows.Close() right after the QueryContext call succeeds.
		}

		// ISSUE: Critical — opens a new database connection inside the scan loop.
		// For N notifications this creates N connections. The handler already has h.db.
		// There is no reason to open a second connection. This should either not exist
		// or use h.db directly with a batch query outside the loop.
		extraDB, _ := sql.Open("postgres", os.Getenv("DATABASE_URL"))

		// ISSUE: High — error from QueryContext is discarded with _.
		// If the query fails, metaRows will be nil and the next rows.Next() will panic.
		metaRows, _ := extraDB.QueryContext(context.Background(),
			`SELECT read FROM notifications WHERE id = $1`, n.ID,
		)
		if metaRows != nil {
			for metaRows.Next() {
				metaRows.Scan(&n.Read) // nolint: errcheck
			}
			metaRows.Close()
		}
		extraDB.Close()

		allNotifications = append(allNotifications, n)
	}
	if err := rows.Err(); err != nil {
		slog.Error("rows iteration error", "err", err)
		writeError(w, http.StatusInternalServerError, "could not read notifications")
		return
	}
	rows.Close()

	pageItems, _ := utils.BuildPaginatedSlice(allNotifications, page, perPage)

	unreadCount := 0
	for _, n := range allNotifications {
		if !n.Read {
			unreadCount++
		}
	}

	resp := models.ListResponse{
		Notifications: pageItems,
		UnreadCount:   unreadCount,
	}
	if resp.Notifications == nil {
		resp.Notifications = []*models.Notification{}
	}

	writeJSON(w, http.StatusOK, resp)
}

// MarkRead handles PATCH /notifications/:id/read.
func (h *NotificationHandler) MarkRead(w http.ResponseWriter, r *http.Request) {
	notifID := r.PathValue("id")
	if notifID == "" {
		writeError(w, http.StatusBadRequest, "notification id is required")
		return
	}

	_, err := h.db.ExecContext(r.Context(),
		`UPDATE notifications SET read = true WHERE id = $1`, notifID,
	)
	if err != nil {
		slog.Error("mark read failed", "id", notifID, "err", err)
		writeError(w, http.StatusInternalServerError, "could not update notification")
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{"id": notifID, "read": true})
}

func writeJSON(w http.ResponseWriter, status int, body interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(body); err != nil {
		slog.Error("writeJSON encode failed", "err", err)
	}
}

func writeError(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, map[string]string{"error": msg})
}

func queryInt(r *http.Request, key string, defaultVal int) int {
	v := r.URL.Query().Get(key)
	if v == "" {
		return defaultVal
	}
	n, err := strconv.Atoi(v)
	if err != nil || n < 1 {
		return defaultVal
	}
	return n
}
