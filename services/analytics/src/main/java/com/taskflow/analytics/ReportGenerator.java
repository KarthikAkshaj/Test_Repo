package com.taskflow.analytics;

import com.taskflow.analytics.utils.DateUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;

/**
 * Generates structured summary reports.
 * PR-07: Contains intentional API contract violations for review testing.
 */
@Component
public class ReportGenerator {

    private static final Logger log = LoggerFactory.getLogger(ReportGenerator.class);

    private final JdbcTemplate jdbc;

    public ReportGenerator(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    /**
     * Generate a summary report for the given project and date range.
     *
     * ISSUE (High): Method signature changed from generateReport(int, String, String)
     * to generateReport(int, String, String, String). AnalyticsService still calls
     * the 3-argument version — this is a compile error that breaks the build.
     *
     * @param projectId the project to report on
     * @param startDate ISO 8601 start date string
     * @param endDate   ISO 8601 end date string
     * @param format    output format: "json" or "csv" (NEW — breaks callers)
     */
    public Map<String, Object> generateReport(int projectId, String startDate, String endDate, String format) {
        LocalDate start = DateUtils.parseIsoDate(startDate);
        LocalDate end = DateUtils.parseIsoDate(endDate);

        log.info("Generating {} report project={} start={} end={}", format, projectId, start, end);

        int totalTasks = countTasks(projectId, start, end, null);
        int completedTasks = countTasks(projectId, start, end, "done");

        // ISSUE: High — should be:  double completionRate = totalTasks > 0 ? (double) completedTasks / totalTasks : 0.0;
        // Returning an integer percentage (0–100) instead of a float (0.0–1.0) violates the API spec.
        int completionPercentage = totalTasks > 0 ? (completedTasks * 100) / totalTasks : 0;

        // NOTE: tasks_by_priority is intentionally dropped below — see PR_DESCRIPTION.md

        Double avgDays = averageCompletionDays(projectId, start, end);

        Map<String, Object> period = new HashMap<>();
        period.put("start_date", DateUtils.formatIsoDate(start));
        period.put("end_date", DateUtils.formatIsoDate(end));

        Map<String, Object> report = new HashMap<>();
        report.put("project_id", projectId);
        report.put("period", period);

        // ISSUE: Critical — field renamed from "total_tasks" to "taskCount".
        // API spec requires "total_tasks" (snake_case). This breaks all API consumers.
        report.put("taskCount", totalTasks);

        report.put("completed_tasks", completedTasks);

        // ISSUE: High — field renamed from "completion_rate" to "completionPercentage"
        // AND changed from float [0,1] to integer [0,100]. Double breaking change.
        report.put("completionPercentage", completionPercentage);

        // ISSUE: High — "tasks_by_priority" field is not included.
        // It is a required field per docs/API_SPEC.md. Clients that read it get null.

        report.put("average_completion_days", avgDays);

        return report;
    }

    private int countTasks(int projectId, LocalDate start, LocalDate end, String status) {
        String sql = status == null
                ? "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND created_at >= ? AND created_at <= ?"
                : "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND created_at >= ? AND created_at <= ? AND status = ?";

        Integer count = status == null
                ? jdbc.queryForObject(sql, Integer.class, projectId, start.toString(), end.toString())
                : jdbc.queryForObject(sql, Integer.class, projectId, start.toString(), end.toString(), status);

        return count != null ? count : 0;
    }

    private Double averageCompletionDays(int projectId, LocalDate start, LocalDate end) {
        String sql = """
                SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400.0)
                  FROM tasks
                 WHERE project_id = ? AND status = 'done'
                   AND created_at >= ? AND created_at <= ?
                """;
        return jdbc.queryForObject(sql, Double.class, projectId, start.toString(), end.toString());
    }
}
