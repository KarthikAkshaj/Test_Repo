import { formatDate, formatDateTime, truncateText, slugify, relativeTime } from '../src/utils/format';
import { validateEmail, validatePassword, validateTaskTitle } from '../src/utils/validation';

// ── format.ts ────────────────────────────────────────────────────────────────

describe('formatDate', () => {
  it('formats a valid ISO date string', () => {
    expect(formatDate('2024-06-01T12:00:00Z')).toBe('Jun 1, 2024');
  });

  it('returns "N/A" for null', () => {
    expect(formatDate(null)).toBe('N/A');
  });

  it('returns "N/A" for undefined', () => {
    expect(formatDate(undefined)).toBe('N/A');
  });

  it('returns "N/A" for an empty string', () => {
    expect(formatDate('')).toBe('N/A');
  });

  it('returns "N/A" for an invalid date string', () => {
    expect(formatDate('not-a-date')).toBe('N/A');
  });
});

describe('truncateText', () => {
  const MAX = 10;

  it('returns text unchanged when within limit', () => {
    expect(truncateText('Hello', MAX)).toBe('Hello');
  });

  it('truncates and appends ellipsis when over limit', () => {
    expect(truncateText('Hello World!!!', MAX)).toBe('Hello Worl…');
  });

  it('returns text unchanged when exactly at the limit', () => {
    expect(truncateText('1234567890', MAX)).toBe('1234567890');
  });

  it('handles an empty string', () => {
    expect(truncateText('', MAX)).toBe('');
  });
});

describe('slugify', () => {
  it('converts to lowercase kebab-case', () => {
    expect(slugify('My Task Title')).toBe('my-task-title');
  });

  it('removes special characters', () => {
    expect(slugify('Hello, World!')).toBe('hello-world');
  });

  it('handles leading and trailing whitespace', () => {
    expect(slugify('  spaced  ')).toBe('spaced');
  });
});

// ── validation.ts ─────────────────────────────────────────────────────────────

describe('validateEmail', () => {
  it('returns null for a valid email', () => {
    expect(validateEmail('user@example.com')).toBeNull();
  });

  it('returns an error for an email without @', () => {
    expect(validateEmail('notanemail')).not.toBeNull();
  });

  it('returns an error for an email without domain', () => {
    expect(validateEmail('user@')).not.toBeNull();
  });

  it('returns an error for null', () => {
    expect(validateEmail(null)).not.toBeNull();
  });

  it('returns an error for an empty string', () => {
    expect(validateEmail('')).not.toBeNull();
  });
});

describe('validatePassword', () => {
  it('returns null for a strong password', () => {
    expect(validatePassword('Secure123')).toBeNull();
  });

  it('returns an error for a password that is too short', () => {
    expect(validatePassword('Ab1')).not.toBeNull();
  });

  it('returns an error for a password without uppercase', () => {
    expect(validatePassword('secure123')).not.toBeNull();
  });

  it('returns an error for a password without digits', () => {
    expect(validatePassword('SecurePass')).not.toBeNull();
  });

  it('returns an error for null', () => {
    expect(validatePassword(null)).not.toBeNull();
  });
});

describe('validateTaskTitle', () => {
  it('returns null for a valid title', () => {
    expect(validateTaskTitle('Fix login bug')).toBeNull();
  });

  it('returns an error for an empty string', () => {
    expect(validateTaskTitle('')).not.toBeNull();
  });

  it('returns an error for null', () => {
    expect(validateTaskTitle(null)).not.toBeNull();
  });

  it('returns an error for a title exceeding 200 chars', () => {
    expect(validateTaskTitle('x'.repeat(201))).not.toBeNull();
  });

  it('returns null for a title of exactly 200 chars', () => {
    expect(validateTaskTitle('x'.repeat(200))).toBeNull();
  });
});
