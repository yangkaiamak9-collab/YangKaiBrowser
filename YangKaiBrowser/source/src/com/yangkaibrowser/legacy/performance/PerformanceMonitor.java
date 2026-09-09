package com.yangkaibrowser.legacy.performance;

public class PerformanceMonitor {
    private static long startTime = 0;

    public static void markStart() {
        startTime = System.currentTimeMillis();
    }

    public static long getStartupDurationMs() {
        if (startTime == 0) return 0;
        return System.currentTimeMillis() - startTime;
    }
}
