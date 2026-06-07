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
 * Generates structured summary reports matching the API contract defined in docs/API_SPEC.md.
 *
 * <p>The report shape must be:
 * <pre>
 * {
 *   "project_id": integer,
 *   "period": { "start_date": string, "end_date": string },
 *   "total_tasks": integer,
 *   "completed_tasks": integer,
 *   "completion_rate": float (0.0–1.0),
 *   "tasks_by_priority": { "low": int, "medium": int, "high": int, "critical": int },
 *   "average_completion_days": float | null
 * }
 * </pre>
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
     * @param projectId the project to report on
     * @param startDate ISO 8601 start date string
     * @param endDate   ISO 8601 end date string
     * @return map matching the API spec response shape
     */
    public Map<String, Object> generateReport(int projectId, String startDate, String endDate) {
        LocalDate start = DateUtils.parseIsoDate(startDate);
        LocalDate end = DateUtils.parseIsoDate(endDate);

        log.info("Generating summary report project={} start={} end={}", projectId, start, end);

        int totalTasks = countTasks(projectId, start, end, null);
        int completedTasks = countTasks(projectId, start, end, "done");
        double completionRate = totalTasks > 0 ? (double) completedTasks / totalTasks : 0.0;

        Map<String, Integer> byPriority = countByPriority(projectId, start, end);
        Double avgDays = averageCompletionDays(projectId, start, end);

        Map<String, Object> period = new HashMap<>();
        period.put("start_date", DateUtils.formatIsoDate(start));
        period.put("end_date", DateUtils.formatIsoDate(end));

        Map<String, Object> report = new HashMap<>();
        report.put("project_id", projectId);
        report.put("period", period);
        report.put("total_tasks", totalTasks);
        report.put("completed_tasks", completedTasks);
        report.put("completion_rate", completionRate);
        report.put("tasks_by_priority", byPriority);
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

    private Map<String, Integer> countByPriority(int projectId, LocalDate start, LocalDate end) {
        String sql = """
                SELECT priority, COUNT(*) AS cnt
                  FROM tasks
                 WHERE project_id = ? AND created_at >= ? AND created_at <= ?
                 GROUP BY priority
                """;

        Map<String, Integer> result = new HashMap<>(Map.of("low", 0, "medium", 0, "high", 0, "critical", 0));
        jdbc.query(sql,
                rs -> result.put(rs.getString("priority"), rs.getInt("cnt")),
                projectId, start.toString(), end.toString()
        );
        return result;
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
