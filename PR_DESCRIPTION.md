# PR-06: Improve cache and pagination performance in notification utils

**Simulated PR description (what the author wrote):**
> Optimizes the in-process cache by removing lock contention.
> Also improves pagination and adds a completion percentage helper.

## Intentionally Introduced Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **Critical** | `utils/helpers.go` lines ~60–75 | **Data race** — `cacheMu` mutex removed; concurrent map read/write causes undefined behavior and possible panic |
| **High** | `utils/helpers.go` line ~90 | **Integer overflow** — `int32(completed) * 100 / int32(total)` overflows for values > 21 million |
| **High** | `utils/helpers.go` lines ~38–42 | **Off-by-one / panic** — `BuildPaginatedSlice` can set `end = start + perPage` beyond `len(items)`, causing an index-out-of-range panic |
| **Medium** | `utils/helpers.go` line ~105 | **Nil pointer dereference** — caller passes a `*Notification` that could be nil; no nil guard before dereferencing |

## What the reviewer should say

1. **Critical — data race:** The original code protects all map accesses with `cacheMu.RLock`/`cacheMu.Lock`. Removing these locks means concurrent goroutines can write to the map simultaneously. Go's map type is not safe for concurrent writes — this causes a panic at runtime. The mutex must be restored.
2. **High — integer overflow:** `int32` overflows at ~2.1 billion, but `completed * 100` can overflow at 21 million. The result wraps to a negative number. Use `float64(completed) / float64(total)` and multiply at the call site, or use `int64`.
3. **High — slice bounds panic:** If `start + perPage > len(items)`, Go panics with "index out of range". The original code had `if end > total { end = total }` — this guard was removed. It must be restored.
4. **Medium — nil dereference:** The new `MessageLength` helper accesses `n.Message` without checking `n != nil`. If the caller passes a nil pointer (a valid zero-value `*Notification`), this panics immediately.
