# Contributing to TaskFlow

## Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/<short-description>` | `feat/task-labels` |
| Bug fix | `fix/<short-description>` | `fix/token-expiry` |
| Refactor | `refactor/<short-description>` | `refactor/pagination-util` |

## Pull Request Rules

1. All PRs require at least one approval before merging.
2. CI must pass (tests + lint + type-check).
3. Every new public function or route **must** have a docstring or JSDoc comment.
4. **Do not** duplicate logic that already exists in `utils/` — extend or import instead.
5. New routes must be documented in `docs/API_SPEC.md`.
6. Secrets and credentials must **never** appear in source code — use environment variables.
7. Functions longer than 50 lines must be broken into smaller helpers.
8. All error responses must use the standard envelope: `{"error": "<message>"}`.

## Python Conventions

- Follow PEP 8. Max line length 100.
- Use `snake_case` for variables/functions, `PascalCase` for classes.
- All functions must have type annotations.
- Raise specific exceptions; never catch bare `Exception` unless re-raised.
- Use `app.logger` for logging — **never** `print()`.
- Prefer f-strings over `.format()`.

## TypeScript Conventions

- Strict mode enabled (`"strict": true` in `tsconfig.json`).
- No `any` types without an inline justification comment.
- All exported functions must have JSDoc.
- Handle all promise rejections explicitly; never leave floating promises.
- File names: `kebab-case.ts`.

## Go Conventions

- Follow `gofmt` / `golangci-lint` rules.
- Always handle returned errors — never assign to `_` without a comment explaining why.
- Use structured logging (`log/slog`).
- Context must be propagated to all I/O calls; never use `context.Background()` inside a handler.

## Java Conventions

- Follow Google Java Style Guide.
- Javadoc required on all public methods.
- Use `SLF4J` for logging; no `System.out.println`.
- All checked exceptions must be handled or declared in the method signature.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(tasks): add bulk status update endpoint
fix(auth): correct token expiry comparison
docs(api): document new project archive endpoint
```
