/**
 * Client-side form validation utilities.
 * All functions return an error string or null (valid).
 * Import from here rather than re-implementing per-component.
 */

const EMAIL_REGEX = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
const PASSWORD_MIN_LENGTH = 8;
const TASK_TITLE_MAX_LENGTH = 200;

/** Return an error message if the email is invalid, null if valid. */
export function validateEmail(email: string | null | undefined): string | null {
  if (!email || !email.trim()) return 'Email is required';
  if (!EMAIL_REGEX.test(email.trim())) return 'Invalid email format';
  return null;
}

/** Return an error message if the password fails strength requirements. */
export function validatePassword(password: string | null | undefined): string | null {
  if (!password) return 'Password is required';
  if (password.length < PASSWORD_MIN_LENGTH)
    return `Password must be at least ${PASSWORD_MIN_LENGTH} characters`;
  if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter';
  if (!/[0-9]/.test(password)) return 'Password must contain at least one digit';
  return null;
}

/** Return an error message if the task title is invalid. */
export function validateTaskTitle(title: string | null | undefined): string | null {
  if (!title || !title.trim()) return 'Task title is required';
  if (title.length > TASK_TITLE_MAX_LENGTH)
    return `Task title must not exceed ${TASK_TITLE_MAX_LENGTH} characters`;
  return null;
}

/** Return an error message if the value is required but empty. */
export function validateRequired(value: unknown, fieldName: string): string | null {
  if (value === null || value === undefined || value === '') return `${fieldName} is required`;
  return null;
}

/** Return an error message if the date string is not a valid ISO 8601 date. */
export function validateIsoDate(value: string | null | undefined): string | null {
  if (!value) return null; // optional field — caller validates presence separately
  const d = new Date(value);
  if (isNaN(d.getTime())) return 'Must be a valid date';
  return null;
}
