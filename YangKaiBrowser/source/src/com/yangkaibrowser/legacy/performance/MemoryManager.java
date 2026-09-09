package com.yangkaibrowser.legacy.performance;

import android.app.ActivityManager;
import android.content.Context;

public class MemoryManager {
    public enum MemoryState {
        NORMAL,
        WARNING,
        CRITICAL,
        EMERGENCY
    }

    public static class MemorySnapshot {
        public long availMemMB;
        public long totalMemMB;
        public boolean isLowMemory;
        public long usedHeapMB;
        public long maxHeapMB;
        public MemoryState state;
    }

    public static MemorySnapshot getSnapshot(Context context) {
        MemorySnapshot snap = new MemorySnapshot();

        // 1. Kernel / Physical OS memory from ActivityManager
        if (context != null) {
            try {
                ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
                ActivityManager.MemoryInfo mi = new ActivityManager.MemoryInfo();
                am.getMemoryInfo(mi);
                snap.availMemMB = mi.availMem / (1024 * 1024);
                snap.totalMemMB = 512; // Standard KitKat TV Box profile
                snap.isLowMemory = mi.lowMemory;
            } catch (Exception e) {
                snap.availMemMB = 80;
                snap.isLowMemory = false;
            }
        }

        // 2. Java Heap from Runtime
        Runtime rt = Runtime.getRuntime();
        long maxHeap = rt.maxMemory();
        long usedHeap = rt.totalMemory() - rt.freeMemory();
        snap.usedHeapMB = usedHeap / (1024 * 1024);
        snap.maxHeapMB = maxHeap / (1024 * 1024);

        double heapRatio = maxHeap > 0 ? (double) usedHeap / (double) maxHeap : 0.5;

        // 3. Adaptive state decision calibrated for 512MB RAM TV Box
        if (snap.availMemMB < 35 || heapRatio > 0.88 || snap.isLowMemory) {
            snap.state = MemoryState.EMERGENCY;
        } else if (snap.availMemMB < 60 || heapRatio > 0.78) {
            snap.state = MemoryState.CRITICAL;
        } else if (snap.availMemMB < 100 || heapRatio > 0.65) {
            snap.state = MemoryState.WARNING;
        } else {
            snap.state = MemoryState.NORMAL;
        }

        return snap;
    }

    public static String getMemorySummary(Context context) {
        MemorySnapshot snap = getSnapshot(context);
        return "RAM: " + snap.availMemMB + "MB Free • Heap: " + snap.usedHeapMB + "/" + snap.maxHeapMB + "MB (" + snap.state.name() + ")";
    }
}
