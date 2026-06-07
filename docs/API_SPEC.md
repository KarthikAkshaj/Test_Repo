# TaskFlow API Specification

**Base URL:** `/api/v1`

All responses use `application/json`. All error responses follow this envelope:

```json
{ "error": "<human-readable message>" }
```

**Authentication:** Bearer token in `Authorization` header.

---

## Tasks

### GET /tasks

Returns a paginated list of tasks.

**Query parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number (1-based) |
| `per_page` | integer | 20 | Results per page (max 100) |
| `project_id` | integer | — | Filter by project |
| `status` | string | — | `todo`, `in_progress`, `review`, or `done` |
| `assignee_id` | integer | — | Filter by assignee user ID |

**Response 200**

```json
{
  "items": [
    {
      "id": 1,
      "title": "string",
      "description": "string | null",
      "status": "todo | in_progress | review | done",
      "priority": "low | medium | high | critical",
      "assignee_id": "integer | null",
      "project_id": "integer",
      "due_date": "ISO 8601 datetime string | null",
      "created_at": "ISO 8601 datetime string",
      "updated_at": "ISO 8601 datetime string"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

### POST /tasks

Create a new task. Returns **201 Created**.

**Request body**

```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (optional, max 5000 chars)",
  "project_id": "integer (required)",
  "assignee_id": "integer (optional)",
  "priority": "low | medium | high | critical  (default: medium)",
  "due_date": "ISO 8601 datetime string (optional)"
}
```

**Response 201** — returns the created task object (same shape as a GET /tasks item).

### PATCH /tasks/:id

Partial update of a task. All fields optional.

**Request body**

```json
{
  "title": "string",
  "description": "string",
  "status": "todo | in_progress | review | done",
  "priority": "low | medium | high | critical",
  "assignee_id": "integer | null",
  "due_date": "ISO 8601 datetime string | null"
}
```

**Response 200** — returns the updated task object.

### DELETE /tasks/:id

**Response 204** — no body.

---

## Projects

### GET /projects

Returns all projects the authenticated user has access to.

**Response 200**

```json
{
  "items": [
    {
      "id": 1,
      "name": "string",
      "description": "string | null",
      "owner_id": "integer",
      "created_at": "ISO 8601 datetime string"
    }
  ]
}
```

### POST /projects

Create a new project. Returns **201 Created**.

---

## Analytics

### GET /analytics/reports/summary

Returns a project summary report.

**Query parameters**

| Param | Type | Required | Description |
|---|---|---|---|
| `project_id` | integer | yes | Project to report on |
| `start_date` | string | yes | ISO 8601 date (inclusive) |
| `end_date` | string | yes | ISO 8601 date (inclusive) |

**Response 200**

```json
{
  "project_id": "integer",
  "period": {
    "start_date": "ISO 8601 date string",
    "end_date": "ISO 8601 date string"
  },
  "total_tasks": "integer",
  "completed_tasks": "integer",
  "completion_rate": "float (0.0 – 1.0)",
  "tasks_by_priority": {
    "low": "integer",
    "medium": "integer",
    "high": "integer",
    "critical": "integer"
  },
  "average_completion_days": "float | null"
}
```

---

## Notifications

### GET /notifications

**Response 200**

```json
{
  "notifications": [
    {
      "id": "string (UUID)",
      "user_id": "integer",
      "type": "task_assigned | task_updated | comment_added | due_soon",
      "message": "string",
      "read": "boolean",
      "created_at": "ISO 8601 datetime string"
    }
  ],
  "unread_count": "integer"
}
```

### PATCH /notifications/:id/read

Mark a notification as read.

**Response 200**

```json
{ "id": "string", "read": true }
```
