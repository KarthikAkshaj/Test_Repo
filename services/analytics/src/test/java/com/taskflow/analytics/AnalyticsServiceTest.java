package com.taskflow.analytics;

import com.taskflow.analytics.utils.DateUtils;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalyticsServiceTest {

    @Mock
    private JdbcTemplate jdbc;

    @Mock
    private ReportGenerator reportGenerator;

    @InjectMocks
    private AnalyticsService analyticsService;

    @Test
    void getSummaryReport_delegatesToReportGenerator() {
        Map<String, Object> expected = Map.of("project_id", 1, "total_tasks", 5);
        when(reportGenerator.generateReport(1, "2024-01-01", "2024-01-31")).thenReturn(expected);

        Map<String, Object> result = analyticsService.getSummaryReport(1, "2024-01-01", "2024-01-31");

        assertSame(expected, result);
        verify(reportGenerator).generateReport(1, "2024-01-01", "2024-01-31");
    }

    @Test
    void countByStatus_returnsEmptyMapWhenNoResults() {
        doNothing().when(jdbc).query(anyString(), any(RowCallbackHandler.class), any(), any(), any());

        Map<String, Integer> result = analyticsService.countByStatus(1, "2024-01-01", "2024-01-31");

        assertNotNull(result);
        assertTrue(result.isEmpty());
    }
}

// ── DateUtils unit tests ───────────────────────────────────────────────────────

class DateUtilsTest {

    @Test
    void parseIsoDate_validDate() {
        assertEquals(java.time.LocalDate.of(2024, 6, 1), DateUtils.parseIsoDate("2024-06-01"));
    }

    @Test
    void parseIsoDate_nullThrows() {
        assertThrows(IllegalArgumentException.class, () -> DateUtils.parseIsoDate(null));
    }

    @Test
    void parseIsoDate_invalidFormatThrows() {
        assertThrows(IllegalArgumentException.class, () -> DateUtils.parseIsoDate("01-06-2024"));
    }

    @Test
    void daysBetween_sameDate_returnsZero() {
        var d = java.time.LocalDate.of(2024, 1, 1);
        assertEquals(0, DateUtils.daysBetween(d, d));
    }

    @Test
    void daysBetween_endBeforeStart_throws() {
        var start = java.time.LocalDate.of(2024, 6, 1);
        var end = java.time.LocalDate.of(2024, 1, 1);
        assertThrows(IllegalArgumentException.class, () -> DateUtils.daysBetween(start, end));
    }
}
