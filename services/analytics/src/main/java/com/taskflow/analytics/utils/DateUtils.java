package com.taskflow.analytics.utils;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;

/**
 * Utility methods for date parsing and formatting used across the analytics service.
 * Use these rather than constructing DateTimeFormatter instances ad-hoc.
 */
public final class DateUtils {

    private static final DateTimeFormatter ISO_DATE = DateTimeFormatter.ISO_LOCAL_DATE;

    private DateUtils() {}

    /**
     * Parse an ISO 8601 date string (e.g. "2024-06-01") into a {@link LocalDate}.
     *
     * @param dateStr the ISO 8601 date string
     * @return the parsed LocalDate
     * @throws IllegalArgumentException if the string is null, blank, or not a valid ISO date
     */
    public static LocalDate parseIsoDate(String dateStr) {
        if (dateStr == null || dateStr.isBlank()) {
            throw new IllegalArgumentException("Date string must not be null or blank");
        }
        try {
            return LocalDate.parse(dateStr.trim(), ISO_DATE);
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("Invalid ISO 8601 date: " + dateStr, e);
        }
    }

    /**
     * Format a {@link LocalDate} as an ISO 8601 date string.
     *
     * @param date the date to format
     * @return an ISO 8601 date string
     */
    public static String formatIsoDate(LocalDate date) {
        if (date == null) {
            throw new IllegalArgumentException("date must not be null");
        }
        return date.format(ISO_DATE);
    }

    /**
     * Return the number of calendar days between startDate (inclusive) and endDate (inclusive).
     * Returns 0 if start equals end.
     *
     * @throws IllegalArgumentException if endDate is before startDate
     */
    public static long daysBetween(LocalDate startDate, LocalDate endDate) {
        if (endDate.isBefore(startDate)) {
            throw new IllegalArgumentException(
                "endDate must not be before startDate: " + startDate + " > " + endDate);
        }
        return ChronoUnit.DAYS.between(startDate, endDate);
    }
}
