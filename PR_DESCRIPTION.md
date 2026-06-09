# PR-03: Add task helper utilities and bulk-create endpoint

**Simulated PR description (what the author wrote):**
> Adds a new taskHelpers utility file with date formatting and email validation
> helpers for the task views. Also updates the tasks API module to support
> direct HTTP calls with a hardcoded base URL for faster local testing.

## Intentionally Introduced Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **Medium** | `utils/taskHelpers.ts` lines 8–15 | **Duplicate function** — `formatTaskDate()` reimplements `format.ts::formatDate()` identically |
| **Medium** | `utils/taskHelpers.ts` lines 18–24 | **Duplicate function** — `isValidEmail()` reimplements `validation.ts::validateEmail()` with a weaker regex |
| **Medium** | `api/tasks.ts` line ~10 | **Hard-coded base URL** — bypasses the configured `apiClient` from `utils/http.ts`, ignoring auth headers and timeout settings |
| **Low** | `utils/taskHelpers.ts` (filename) | **Naming convention violation** — file should be `task-helpers.ts` (kebab-case), per CONTRIBUTING.md §TypeScript Conventions |

## What the reviewer should say

1. **Medium — formatTaskDate duplicates formatDate:** `format.ts` already exports `formatDate(isoString)` with identical logic and the same "N/A" fallback. Import from there instead. Creating a second copy means any future fix (timezone handling, locale change) must be made in two places.
2. **Medium — isValidEmail duplicates validateEmail:** `validation.ts::validateEmail` already handles null/undefined and uses a stricter regex. The new `isValidEmail` uses `/\S+@\S+\.\S+/` which accepts `@@.a` and rejects nothing with spaces. Import `validateEmail` instead.
3. **Medium — hard-coded base URL:** Using `axios.create({ baseURL: 'http://localhost:5000' })` bypasses the `apiClient` from `utils/http.ts`. That client carries the `Authorization` header (set via `setAuthToken`) and a 10-second timeout. Any request through this raw instance will be unauthenticated.
4. **Low — filename:** CONTRIBUTING.md specifies kebab-case for TypeScript files. `taskHelpers.ts` should be `task-helpers.ts`.
