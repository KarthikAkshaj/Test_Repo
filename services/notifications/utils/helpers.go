package utils

import (
	"context"
	"log/slog"
	"math"
	"sync"
	"time"
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

// RetryWithBackoff runs fn up to cfg.MaxAttempts times, sleeping with exponential back-off
// between failures. It respects ctx cancellation and returns the last error on exhaustion.
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

// PaginationParams holds page/size values after validation.
type PaginationParams struct {
	Page    int
	PerPage int
}

// BuildPaginatedSlice returns the sub-slice of items for the given page and the total count.
// page is 1-based. Returns an empty slice (not nil) if the page is out of range.
func BuildPaginatedSlice[T any](items []T, page, perPage int) ([]T, int) {
	total := len(items)
	if total == 0 || page < 1 || perPage < 1 {
		return []T{}, total
	}
	start := (page - 1) * perPage
	if start >= total {
		return []T{}, total
	}
	end := start + perPage
	if end > total {
		end = total
	}
	return items[start:end], total
}

// notificationCache is an in-process read-through cache for notification objects.
// All access must hold cacheMu.
var (
	notificationCache = make(map[string]cacheEntry)
	cacheMu           sync.RWMutex
	cacheTTL          = 5 * time.Minute
)

type cacheEntry struct {
	value     interface{}
	expiresAt time.Time
}

// CacheGet returns (value, true) if a non-expired entry exists for key.
func CacheGet(key string) (interface{}, bool) {
	cacheMu.RLock()
	defer cacheMu.RUnlock()
	entry, ok := notificationCache[key]
	if !ok || time.Now().After(entry.expiresAt) {
		return nil, false
	}
	return entry.value, true
}

// CacheSet stores value under key with the default TTL.
func CacheSet(key string, value interface{}) {
	cacheMu.Lock()
	defer cacheMu.Unlock()
	notificationCache[key] = cacheEntry{value: value, expiresAt: time.Now().Add(cacheTTL)}
}

// CacheDelete removes a key from the cache.
func CacheDelete(key string) {
	cacheMu.Lock()
	defer cacheMu.Unlock()
	delete(notificationCache, key)
}

// CompletionRate returns completed/total as a float64 in [0, 1].
// Returns 0 if total is 0 to avoid division by zero.
func CompletionRate(completed, total int64) float64 {
	if total == 0 {
		return 0
	}
	return float64(completed) / float64(total)
}
