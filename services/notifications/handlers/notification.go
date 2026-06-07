package handlers

import (
	"database/sql"
	"encoding/json"
	"log/slog"
	"net/http"
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
// Query params: user_id (required), page (default 1), per_page (default 20).
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

	cacheKey := "notifications:" + userIDStr
	if cached, ok := utils.CacheGet(cacheKey); ok {
		writeJSON(w, http.StatusOK, cached)
		return
	}

	rows, err := h.db.QueryContext(r.Context(),
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
	}
	defer func() {
		if closeErr := rows.Close(); closeErr != nil {
			slog.Warn("rows.Close failed", "err", closeErr)
		}
	}()

	var allNotifications []*models.Notification
	for rows.Next() {
		n := &models.Notification{}
		if err := rows.Scan(&n.ID, &n.UserID, &n.Type, &n.Message, &n.Read, &n.CreatedAt); err != nil {
			slog.Error("scan notification failed", "err", err)
			writeError(w, http.StatusInternalServerError, "could not read notifications")
			return
		}
		allNotifications = append(allNotifications, n)
	}
	if err := rows.Err(); err != nil {
		slog.Error("rows iteration error", "err", err)
		writeError(w, http.StatusInternalServerError, "could not read notifications")
		return
	}

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

	utils.CacheSet(cacheKey, resp)
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
		`UPDATE notifications SET read = true WHERE id = $1`,
		notifID,
	)
	if err != nil {
		slog.Error("mark read failed", "id", notifID, "err", err)
		writeError(w, http.StatusInternalServerError, "could not update notification")
		return
	}

	utils.CacheDelete("notifications:" + r.URL.Query().Get("user_id"))
	writeJSON(w, http.StatusOK, map[string]interface{}{"id": notifID, "read": true})
}

// ── helpers ───────────────────────────────────────────────────────────────────

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
