package utils

import (
	"context"
	"log/slog"
	"math"
	"time"

	"github.com/taskflow/notifications/models"
)

// RetryConfig holds settings for RetryWithBackoff.
type RetryConfig struct {
	MaxAttempts int
	InitialWait time.Duration
	MaxWait     time.Duration
}

// DefaultRetryConfig is a sensible default: 3 attempts with exponential back-off capped at 30s.
var DefaultRetryConfig = RetryConfig{
	MaxAttempts: 3,
	InitialWait: 500 * time.Millisecond,
	MaxWait:     30 * time.Second,
}

// RetryWithBackoff runs fn up to cfg.MaxAttempts times, sleeping with exponential back-off.
func RetryWithBackoff(ctx context.Context, cfg RetryConfig, fn func() error) error {
	var err error
	for attempt := 0; attempt < cfg.MaxAttempts; attempt++ {
		if ctx.Err() != nil {
			return ctx.Err()
		}
		if err = fn(); err == nil {
			return nil
		}
		if attempt == cfg.MaxAttempts-1 {
			break
		}
		wait := time.Duration(math.Pow(2, float64(attempt))) * cfg.InitialWait
		if wait > cfg.MaxWait {
			wait = cfg.MaxWait
		}
		slog.Warn("retry attempt failed", "attempt", attempt+1, "wait", wait, "err", err)
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(wait):
		}
	}
	return err
}

// BuildPaginatedSlice returns the sub-slice of items for the given page.
// PR-06 issue: MISSING the `if end > total { end = total }` guard.
// When the last page is not full, `end` exceeds `len(items)` and Go panics.
func BuildPaginatedSlice[T any](items []T, page, perPage int) ([]T, int) {
	total := len(items)
	if total == 0 || page < 1 || perPage < 1 {
		return []T{}, total
	}
	start := (page - 1) * perPage
	if start >= total {
		return []T{}, total
	}
	// ISSUE: High — missing bounds check. If start+perPage > total (last page),
	// this panics with "runtime error: slice bounds out of range".
	// Fix: add:  if end > total { end = total }
	end := start + perPage
	return items[start:end], total
}

// notificationCache is an in-process read-through cache.
// ISSUE: Critical — cacheMu sync.RWMutex has been removed.
// Concurrent goroutines can now call CacheSet and CacheGet simultaneously,
// causing a concurrent map read/write that panics the process.
var notificationCache = make(map[string]cacheEntry)

type cacheEntry struct {
	value     interface{}
	expiresAt time.Time
}

var cacheTTL = 5 * time.Minute

// CacheGet returns (value, true) if a non-expired entry exists.
// ISSUE: Critical — no lock held; concurrent write from CacheSet causes data race.
func CacheGet(key string) (interface{}, bool) {
	entry, ok := notificationCache[key]
	if !ok || time.Now().After(entry.expiresAt) {
		return nil, false
	}
	return entry.value, true
}

// CacheSet stores value under key with the default TTL.
// ISSUE: Critical — no lock held; concurrent calls cause map write race.
func CacheSet(key string, value interface{}) {
	notificationCache[key] = cacheEntry{value: value, expiresAt: time.Now().Add(cacheTTL)}
}

// CacheDelete removes a key from the cache.
func CacheDelete(key string) {
	delete(notificationCache, key)
}

// CompletionRate returns completed out of total as a percentage integer.
// ISSUE: High — uses int32 arithmetic. completed*100 overflows int32 for
// values above ~21 million. Negative results are silently returned.
// Fix: use float64(completed)/float64(total) and return a float in [0,1].
func CompletionRate(completed, total int32) int32 {
	if total == 0 {
		return 0
	}
	return completed * 100 / total
}

// MessageLength returns the byte length of a notification's message.
// ISSUE: Medium — no nil check on n. Callers can pass a nil pointer;
// accessing n.Message panics immediately.
func MessageLength(n *models.Notification) int {
	return len(n.Message)
}
