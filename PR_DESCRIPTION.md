# PR-05: Add batch notification delivery

**Simulated PR description (what the author wrote):**
> Rewrites the notification handler to support bulk delivery. Fetches each
> notification's metadata and delivers them in a loop.

## Intentionally Introduced Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **Critical** | `handlers/notification.go` line ~55 | **N+1 DB connections** — opens a new `sql.Open(...)` inside the scan loop for every notification row |
| **High** | `handlers/notification.go` line ~70 | **Ignored error** — assigns `db.QueryContext(...)` result to `_` discarding any error |
| **High** | `handlers/notification.go` line ~40 | **context.Background() in handler** — ignores request cancellation; long queries will not be cancelled when the client disconnects |
| **Medium** | `handlers/notification.go` line ~52 | **Missing defer rows.Close()** — rows is never closed in the error path, leaking the cursor |

## What the reviewer should say

1. **Critical — N+1 connections:** `sql.Open` (or a new `db.Query` per row) inside a loop opens a fresh connection for each notification. For 100 notifications this creates 100 connections. The handler already has `h.db` — use it. Open one query outside the loop.
2. **High — ignored error:** Assigning a `(rows, err)` tuple to `(rows, _)` silently ignores database errors. Any query failure causes a nil-rows panic on the next line. Always check `err != nil` immediately.
3. **High — context.Background():** Handlers must propagate `r.Context()` to all I/O operations. Using `context.Background()` means a cancelled or timed-out HTTP request will keep the database query running, wasting connections. See CONTRIBUTING.md §Go Conventions.
4. **Medium — rows not closed:** In the early-return error paths, `rows.Close()` is never called. The database cursor stays open until GC. Use `defer rows.Close()` immediately after checking the query error.
