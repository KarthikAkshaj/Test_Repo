# PR-04: Expand utility test coverage

**Simulated PR description (what the author wrote):**
> Adds more tests for the format and validation utilities to improve coverage.

## Intentionally Introduced Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **Critical** | `tests/utils.test.ts` line ~12 | **Wrong expected value** — `expect(formatDate(null)).toBe("")` but the function returns `"N/A"`; test passes only if someone breaks the implementation |
| **High** | `tests/utils.test.ts` lines ~30–40 | **Missing invalid cases** — `validateEmail` tests only check valid input; no test for malformed emails, no `@`, missing domain |
| **High** | `tests/utils.test.ts` lines ~50–55 | **Stale mock data** — `truncateText` test uses magic number `8` with no explanation; the boundary case (exactly at limit) is untested |
| **Medium** | `tests/utils.test.ts` lines ~60–70 | **Vague test descriptions** — "works correctly" and "handles input" are not descriptive; a failing test produces an unintelligible message |
| **Low** | `tests/utils.test.ts` line ~18 | **Missing edge case** — `formatDate` is never tested with an invalid date string (e.g. `"not-a-date"`) |

## What the reviewer should say

1. **Critical — wrong assertion:** `toBe("")` will pass today only if the implementation is changed to return `""` instead of `"N/A"`. This test is a false guarantee: it tests the wrong contract. The correct assertion is `toBe("N/A")` per the JSDoc on `formatDate`.
2. **High — incomplete email validation tests:** The test suite verifies the happy path but never checks that invalid inputs are rejected. A broken regex that accepts everything would still pass all current tests. Add cases for `"notanemail"`, `"user@"`, `""`, and `null`.
3. **High — unexplained magic number:** `truncateText('Hello World', 8)` — why 8? The test is checking a specific boundary but doesn't explain it, making it fragile when the function is refactored. The boundary case (exactly `maxLength` chars) is not tested at all.
4. **Medium — vague descriptions:** Jest failure output will show "● utils › works correctly" with no indication of what broke. Follow the pattern: `'returns "N/A" for null input'`.
