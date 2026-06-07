package com.taskflow.analytics;

import com.taskflow.analytics.utils.DateUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;

/**
 * Provides analytics aggregation queries over the TaskFlow database.
 */
@Service
public class AnalyticsService {

    private static final Logger log = LoggerFactory.getLogger(AnalyticsService.class);

    private final JdbcTemplate jdbc;
    private final ReportGenerator reportGenerator;

    public AnalyticsService(JdbcTemplate jdbc, ReportGenerator reportGenerator) {
        this.jdbc = jdbc;
        this.reportGenerator = reportGenerator;
    }

    /**
     * Count tasks grouped by status for a given project and date range.
     *
     * @param projectId the project to aggregate
     * @param startDate ISO 8601 start date (inclusive)
     * @param endDate   ISO 8601 end date (inclusive)
     * @return map of status → count
     */
    public Map<String, Integer> countByStatus(int projectId, String startDate, String endDate) {
        LocalDate start = DateUtils.parseIsoDate(startDate);
        LocalDate end = DateUtils.parseIsoDate(endDate);

        log.info("Counting tasks by status for project={} from={} to={}", projectId, start, end);

        String sql = """
                SELECT status, COUNT(*) AS cnt
                  FROM tasks
                 WHERE project_id = ?
                   AND created_at >= ?
                   AND created_at <= ?
                 GROUP BY status
                """;

        Map<String, Integer> result = new HashMap<>();
        jdbc.query(sql,
                rs -> {
                    result.put(rs.getString("status"), rs.getInt("cnt"));
                },
                projectId, start.toString(), end.toString()
        );
        return result;
    }

    /**
     * Generate the full summary report for a project.
     *
     * @param projectId the project to report on
     * @param startDate ISO 8601 start date
     * @param endDate   ISO 8601 end date
     * @return the report as a map matching the API spec shape
     */
    public Map<String, Object> getSummaryReport(int projectId, String startDate, String endDate) {
        return reportGenerator.generateReport(projectId, startDate, endDate);
    }
}
