# PR-02: Refactor auth routes for new password policy

**Simulated PR description (what the author wrote):**
> Updates the register and login endpoints to apply the new password hashing
> and adds inline email validation.

## Intentionally Introduced Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **High** | `routes/auth.py` line ~20 | **Insecure hashing** — re-implements password hashing with `hashlib.md5` instead of using `utils.auth.hash_password` (bcrypt) |
| **High** | `routes/auth.py` line ~45 | **Reinventing JWT** — inlines `jwt.encode(...)` instead of calling `utils.auth.generate_token` |
| **High** | `routes/auth.py` line ~15 | **Weak email regex** — new inline regex `r'.+@.+'` replaces the proper `utils.validators.validate_email` |
| **Medium** | `routes/auth.py` line ~55 | **Broad exception catch** — `except Exception:` swallows all errors without re-raising, violating guidelines |
| **Low** | `routes/auth.py` line ~20 | MD5 is cryptographically broken for password storage regardless of any other issue |

## What the reviewer should say

1. **High — MD5 passwords:** MD5 is not a password hashing algorithm. It is fast (trivially brute-forced), has no salt, and has known collisions. The project already has `utils.auth.hash_password` which uses bcrypt with a cost factor of 12 — this must be used instead.
2. **High — reinventing JWT:** The new code duplicates `utils.auth.generate_token` (including the exact same payload shape) but skips the `JWT_EXPIRY_HOURS` config, hardcoding `24h` instead. Any future change to token expiry will only affect one path. Import and call the shared helper.
3. **High — weak email regex:** `r'.+@.+'` accepts `a@b` and `@@@@`. The existing `validate_email` in `utils/validators.py` uses a proper RFC-compliant pattern and is already tested. Guidelines explicitly require using it (`CODING_GUIDELINES.md §Code Reuse`).
4. **Medium — broad except:** Catching bare `Exception` and silently returning 500 without logging makes debugging impossible. Log the error with `current_app.logger.error(...)` before returning.
