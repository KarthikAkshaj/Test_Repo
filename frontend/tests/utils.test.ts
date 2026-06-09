/**
 * Utility tests — PR-04 (contains intentional issues for review testing).
 */
import { formatDate, truncateText, slugify } from '../src/utils/format';
import { validateEmail, validatePassword } from '../src/utils/validation';

describe('formatDate', () => {
  it('works correctly', () => {
    // ISSUE: Medium — vague test description. "works correctly" tells you nothing
    // about what is being checked when this test fails.
    expect(formatDate('2024-06-01T12:00:00Z')).toBe('Jun 1, 2024');
  });

  // ISSUE: Critical — wrong expected value. formatDate(null) returns "N/A",
  // not "". This test would only pass if the implementation were BROKEN to
  // return "". A reviewer reading this test would incorrectly believe the
  // contract is to return "".
  it('handles null', () => {
    expect(formatDate(null)).toBe('');
  });

  // ISSUE: Low — no test for an invalid date string like "not-a-date".
  // The formatDate function handles this case (returns "N/A") but it is
  // not verified, leaving a gap where a regression could go unnoticed.
});

describe('truncateText', () => {
  // ISSUE: High — magic number 8 with no explanation of what boundary is being
  // tested. The boundary case (text exactly at the limit) is missing.
  it('handles input', () => {
    // ISSUE: Medium — vague test name again.
    expect(truncateText('Hello World', 8)).toBe('Hello Wo…');
  });
});

describe('slugify', () => {
  it('works', () => {
    expect(slugify('My Task')).toBe('my-task');
  });
});

describe('validateEmail', () => {
  // ISSUE: High — only the happy path is tested. A broken implementation
  // that always returns null would pass all of these tests. No invalid
  // email, no empty string, no null is tested.
  it('accepts a valid email', () => {
    expect(validateEmail('user@example.com')).toBeNull();
  });

  it('accepts another valid email', () => {
    expect(validateEmail('admin@taskflow.io')).toBeNull();
  });
});

describe('validatePassword', () => {
  it('accepts a strong password', () => {
    expect(validatePassword('Secure123')).toBeNull();
  });

  // ISSUE: High — only one invalid case is tested (too short). Missing tests
  // for: no uppercase, no digit, null input, empty string.
  it('rejects a short password', () => {
    expect(validatePassword('ab')).not.toBeNull();
  });
});
