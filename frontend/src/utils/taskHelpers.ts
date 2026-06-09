/**
 * Task-specific helper utilities.
 * PR-03: Contains intentional issues for review testing.
 */

// ISSUE: Medium — duplicates format.ts::formatDate() exactly.
// Should import: import { formatDate } from './format';
// then call formatDate(isoString) directly.
export function formatTaskDate(isoString: string | null): string {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return 'N/A';
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

// ISSUE: Medium — duplicates validation.ts::validateEmail() but with a weaker regex.
// /\S+@\S+\.\S+/ accepts "@@.a" and "not valid@x.y" — far less strict than the
// existing validated pattern in validation.ts. Should import validateEmail instead.
export function isValidEmail(email: string): boolean {
  return /\S+@\S+\.\S+/.test(email);
}

/** Return the CSS class name for a task priority badge. */
export function priorityClass(priority: string): string {
  const map: Record<string, string> = {
    low: 'badge-low',
    medium: 'badge-medium',
    high: 'badge-high',
    critical: 'badge-critical',
  };
  return map[priority] ?? 'badge-default';
}

/** Return a human-readable label for a task status. */
export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    todo: 'To Do',
    in_progress: 'In Progress',
    review: 'In Review',
    done: 'Done',
  };
  return map[status] ?? status;
}
