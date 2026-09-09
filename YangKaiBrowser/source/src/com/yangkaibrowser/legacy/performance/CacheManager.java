package com.yangkaibrowser.legacy.performance;

import android.content.Context;
import android.webkit.CookieManager;
import android.webkit.CookieSyncManager;
import com.yangkaibrowser.legacy.data.HistoryManager;
import java.io.File;

public class CacheManager {

    public static void clearAppCache(Context context) {
        if (context == null) return;
        try {
            File cacheDir = context.getCacheDir();
            deleteDir(cacheDir);
            File extCacheDir = context.getExternalCacheDir();
            if (extCacheDir != null) {
                deleteDir(extCacheDir);
            }
        } catch (Exception ignored) {}
    }

    public static void clearCookies(Context context) {
        if (context == null) return;
        try {
            CookieSyncManager.createInstance(context);
            CookieManager cookieManager = CookieManager.getInstance();
            cookieManager.removeAllCookie();
            CookieSyncManager.getInstance().sync();
        } catch (Exception ignored) {}
    }

    public static void clearEverything(Context context, HistoryManager historyManager) {
        clearAppCache(context);
        clearCookies(context);
        if (historyManager != null) {
            historyManager.clearAll();
        }
        System.gc();
    }

    private static boolean deleteDir(File dir) {
        if (dir != null && dir.isDirectory()) {
            String[] children = dir.list();
            if (children != null) {
                for (String child : children) {
                    boolean success = deleteDir(new File(dir, child));
                    if (!success) return false;
                }
            }
            return dir.delete();
        } else if (dir != null && dir.isFile()) {
            return dir.delete();
        }
        return false;
    }
}
