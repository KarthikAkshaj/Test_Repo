# Coding Guidelines

These guidelines supplement the rules in [CONTRIBUTING.md](../CONTRIBUTING.md) with more detailed rationale and examples.

## Security

- **Never hard-code credentials.** Passwords, API keys, and secrets belong in environment variables or a secrets manager, not in source files.
- **Parameterize all database queries.** String interpolation in SQL queries opens SQL injection vulnerabilities. Always use ORM methods or parameterized queries (`?` / `:param` placeholders).
- **Hash passwords with bcrypt.** MD5, SHA-1, and plain SHA-256 are not acceptable for password storage. Use the provided `utils.auth.hash_password` / `utils.auth.verify_password` helpers.
- **Validate all user input** before it reaches business logic. Use the validators in `backend/app/utils/validators.py` and `frontend/src/utils/validation.ts`.

## Error Handling

- Return structured error responses using the standard envelope `{"error": "..."}`.
- Log the full exception server-side; expose only a safe message to the client.
- In Go, always check `err != nil` immediately after every call that returns an error.
- In Python, catch the narrowest applicable exception class, not bare `Exception`.

## Code Reuse

- Before writing a new utility function, check `utils/` in the relevant service. If a helper already exists, **import it** rather than copying it.
- The following shared helpers are available and must be used:

| Helper | Location | Purpose |
|---|---|---|
| `hash_password` / `verify_password` | `backend/app/utils/auth.py` | Password hashing with bcrypt |
| `generate_token` / `decode_token` | `backend/app/utils/auth.py` | JWT creation and validation |
| `require_auth` | `backend/app/utils/auth.py` | Route-level authentication decorator |
| `validate_email`, `validate_password`, `validate_task_title`, `validate_status`, `validate_priority` | `backend/app/utils/validators.py` | Input validation |
| `get_pagination_params`, `paginate_query` | `backend/app/utils/pagination.py` | Cursor/page-based pagination |
| `get_or_404`, `safe_commit` | `backend/app/utils/db.py` | DB access helpers |
| `formatDate`, `truncateText`, `slugify` | `frontend/src/utils/format.ts` | String and date formatting |
| `validateEmail`, `validatePassword`, `validateTaskTitle` | `frontend/src/utils/validation.ts` | Client-side validation |
| `apiClient` | `frontend/src/utils/http.ts` | Configured Axios instance with auth headers |
| `RetryWithBackoff`, `BuildPaginatedResponse` | `services/notifications/utils/helpers.go` | Go utility helpers |
| `DateUtils` | `services/analytics/src/main/java/com/taskflow/analytics/utils/DateUtils.java` | Date parsing/formatting |

## Testing

- Every new function must have at least one test covering the happy path and one covering an error/edge case.
- Tests must not pass for the wrong reason — always assert on actual return values, not just that no exception was thrown.
- Test data must match the real API contract (field names, types, enums). Using stale mocks is a common source of false-positive test suites.

## Performance

- Never open a database connection inside a loop. Acquire the connection once before the loop, reuse it.
- Avoid N+1 query patterns. Prefer JOINs or batch fetches.
- For Go services: always pass `context.Context` through the call chain and respect cancellation.

## Maintainability

- Max function length: **50 lines**. Extract helpers liberally.
- No magic numbers — use named constants with explanatory names.
- No `TODO` or `FIXME` comments in merged code; file a ticket instead.
- No dead code or commented-out blocks.
