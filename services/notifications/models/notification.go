package models

import "time"

// NotificationType enumerates valid notification categories.
type NotificationType string

const (
	TypeTaskAssigned  NotificationType = "task_assigned"
	TypeTaskUpdated   NotificationType = "task_updated"
	TypeCommentAdded  NotificationType = "comment_added"
	TypeDueSoon       NotificationType = "due_soon"
)

// Notification represents an in-app notification record.
type Notification struct {
	ID        string           `json:"id" db:"id"`
	UserID    int              `json:"user_id" db:"user_id"`
	Type      NotificationType `json:"type" db:"type"`
	Message   string           `json:"message" db:"message"`
	Read      bool             `json:"read" db:"read"`
	CreatedAt time.Time        `json:"created_at" db:"created_at"`
}

// ListResponse is the shape returned by GET /notifications.
type ListResponse struct {
	Notifications []*Notification `json:"notifications"`
	UnreadCount   int             `json:"unread_count"`
}
