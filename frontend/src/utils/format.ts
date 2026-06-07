/**
 * String and date formatting utilities.
 * Import from here rather than re-implementing in feature modules.
 */

/**
 * Format an ISO 8601 date string for display.
 * Returns "N/A" for null/undefined inputs.
 *
 * @example formatDate("2024-06-01T12:00:00Z") // "Jun 1, 2024"
 */
export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return 'N/A';
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

/**
 * Format an ISO 8601 datetime string with time component.
 * Returns "N/A" for null/undefined inputs.
 *
 * @example formatDateTime("2024-06-01T14:30:00Z") // "Jun 1, 2024, 2:30 PM"
 */
export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return 'N/A';
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Truncate a string to maxLength, appending "…" if truncated.
 *
 * @example truncateText("Hello World", 5) // "Hello…"
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '…';
}

/**
 * Convert a string to a URL-friendly slug.
 *
 * @example slugify("My Task Title!") // "my-task-title"
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Return a human-readable relative time string ("2 hours ago", "in 3 days").
 */
export function relativeTime(isoString: string): string {
  const diffMs = new Date(isoString).getTime() - Date.now();
  const diffSec = Math.round(diffMs / 1000);
  const abs = Math.abs(diffSec);

  if (abs < 60) return diffSec >= 0 ? 'in a moment' : 'just now';
  if (abs < 3600) {
    const m = Math.round(abs / 60);
    return diffSec >= 0 ? `in ${m} minute${m > 1 ? 's' : ''}` : `${m} minute${m > 1 ? 's' : ''} ago`;
  }
  if (abs < 86400) {
    const h = Math.round(abs / 3600);
    return diffSec >= 0 ? `in ${h} hour${h > 1 ? 's' : ''}` : `${h} hour${h > 1 ? 's' : ''} ago`;
  }
  const d = Math.round(abs / 86400);
  return diffSec >= 0 ? `in ${d} day${d > 1 ? 's' : ''}` : `${d} day${d > 1 ? 's' : ''} ago`;
}
