# PR-07: Refactor report generator to support multiple output formats

**Simulated PR description (what the author wrote):**
> Refactors ReportGenerator to support JSON and CSV output formats.
> Renames some fields for clarity and simplifies the completion metric.

## Intentionally Introduced Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **Critical** | `ReportGenerator.java` line ~52 | **Wrong field name** — returns `taskCount` instead of `total_tasks` as required by `docs/API_SPEC.md` |
| **High** | `ReportGenerator.java` line ~55 | **Wrong type + name** — returns `completionPercentage` (int 0–100) instead of `completion_rate` (float 0.0–1.0) |
| **High** | `ReportGenerator.java` line ~58 | **Missing field** — `tasks_by_priority` is dropped entirely from the response, breaking API consumers |
| **High** | `ReportGenerator.java` line ~35 | **Broken method signature** — adds a `format` parameter without updating `AnalyticsService.getSummaryReport` which calls `generateReport(projectId, start, end)` — compile error |
| **Medium** | (no new test file) | **Zero test coverage** — the new format-routing logic has no unit tests |

## What the reviewer should say

1. **Critical — field name mismatch:** The API spec (`docs/API_SPEC.md §Analytics`) defines `total_tasks` (snake_case). Returning `taskCount` (camelCase) breaks every existing API consumer and any client generated from the spec. The field name must match exactly.
2. **High — wrong type for completion_rate:** The spec defines `completion_rate` as `float (0.0–1.0)`. Returning `completionPercentage` as an integer 0–100 changes the semantic meaning, breaks comparisons (`0.9 > 0.5` vs `90 > 50`), and breaks clients that multiply by 100 for display.
3. **High — missing tasks_by_priority:** Silently dropping a required field from the response is a breaking API change. Any client that reads `tasks_by_priority` will receive undefined/null and likely throw a NullPointerException or TypeError.
4. **High — broken signature:** `AnalyticsService.getSummaryReport` calls `reportGenerator.generateReport(projectId, startDate, endDate)` (3 args). Adding a 4th `format` parameter without updating the call site is a compile error that breaks the build.
5. **Medium — no tests:** New branching logic (JSON vs CSV routing) with zero test coverage means regressions cannot be detected.
