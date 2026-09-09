#!/usr/bin/env python3
import os

WORKSPACE_DIR = os.path.abspath(os.getcwd())
PROJECT_DIR = os.path.join(WORKSPACE_DIR, "YangKaiBrowser")
SRC_BASE = os.path.join(PROJECT_DIR, "source", "src", "com", "yangkaibrowser", "legacy")

def write_java(rel_path, content):
    full_path = os.path.join(SRC_BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    print(f"[+] Wrote {rel_path}")

# 1. BrowserEngine.java
write_java("browser/BrowserEngine.java", """package com.yangkaibrowser.legacy.browser;

import android.view.View;

public interface BrowserEngine {
    void loadUrl(String url);
    void reload();
    void stopLoading();
    void goBack();
    void goForward();
    boolean canGoBack();
    boolean canGoForward();
    void destroy();
    void clearCache(boolean includeDiskFiles);
    void setJavaScriptEnabled(boolean enabled);
    void setImagesEnabled(boolean enabled);
    void setZoom(int percent);
    String getTitle();
    String getUrl();
    View getView();
    void setEngineCallback(EngineCallback callback);

    interface EngineCallback {
        void onProgress(int progress);
        void onTitleReceived(String title);
        void onUrlChanged(String url);
        void onLoadingStateChanged(boolean isLoading);
        void onError(int errorCode, String description, String failingUrl);
        void onSslError(String failingUrl);
    }
}
""")

# 2. LegacyWebViewEngine.java
write_java("browser/LegacyWebViewEngine.java", """package com.yangkaibrowser.legacy.browser;

import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.Bitmap;
import android.net.http.SslError;
import android.view.View;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class LegacyWebViewEngine implements BrowserEngine {
    private final WebView webView;
    private EngineCallback callback;
    private String currentTitle = "";

    @SuppressLint("SetJavaScriptEnabled")
    public LegacyWebViewEngine(Context context) {
        this.webView = new WebView(context);
        initSettings();
        initClients();
    }

    private void initSettings() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setLoadsImagesAutomatically(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAppCacheEnabled(true);
        settings.setAppCacheMaxSize(8 * 1024 * 1024); // 8MB cache
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setAllowFileAccess(true);
        settings.setSaveFormData(false);
        settings.setSavePassword(false);

        // Hardware TV friendly default styling
        webView.setBackgroundColor(0xFF121214);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
    }

    private void initClients() {
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url != null && (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("file:///"))) {
                    view.loadUrl(url);
                    return true;
                }
                return false;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                if (callback != null) {
                    callback.onLoadingStateChanged(true);
                    callback.onUrlChanged(url);
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                currentTitle = view.getTitle();
                if (callback != null) {
                    callback.onLoadingStateChanged(false);
                    callback.onTitleReceived(currentTitle);
                    callback.onUrlChanged(url);
                }
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                if (callback != null) {
                    callback.onError(errorCode, description, failingUrl);
                }
            }

            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                // SSL Security Rule: Never blindly call handler.proceed()
                // Safely cancel to protect legacy TV from compromised connections
                handler.cancel();
                if (callback != null) {
                    callback.onSslError(error != null ? error.getUrl() : "");
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (callback != null) {
                    callback.onProgress(newProgress);
                }
            }

            @Override
            public void onReceivedTitle(WebView view, String title) {
                currentTitle = title;
                if (callback != null) {
                    callback.onTitleReceived(title);
                }
            }
        });
    }

    @Override
    public void loadUrl(String url) {
        if (url != null && !url.trim().isEmpty()) {
            webView.loadUrl(url.trim());
        }
    }

    @Override
    public void reload() {
        webView.reload();
    }

    @Override
    public void stopLoading() {
        webView.stopLoading();
    }

    @Override
    public void goBack() {
        if (webView.canGoBack()) {
            webView.goBack();
        }
    }

    @Override
    public void goForward() {
        if (webView.canGoForward()) {
            webView.goForward();
        }
    }

    @Override
    public boolean canGoBack() {
        return webView.canGoBack();
    }

    @Override
    public boolean canGoForward() {
        return webView.canGoForward();
    }

    @Override
    public void destroy() {
        try {
            webView.stopLoading();
            webView.clearHistory();
            webView.removeAllViews();
            webView.destroy();
        } catch (Exception ignored) {}
    }

    @Override
    public void clearCache(boolean includeDiskFiles) {
        webView.clearCache(includeDiskFiles);
    }

    @Override
    public void setJavaScriptEnabled(boolean enabled) {
        webView.getSettings().setJavaScriptEnabled(enabled);
    }

    @Override
    public void setImagesEnabled(boolean enabled) {
        webView.getSettings().setLoadsImagesAutomatically(enabled);
        webView.getSettings().setBlockNetworkImage(!enabled);
    }

    @Override
    public void setZoom(int percent) {
        if (percent > 0) {
            webView.setInitialScale(percent);
        }
    }

    @Override
    public String getTitle() {
        return currentTitle != null ? currentTitle : webView.getTitle();
    }

    @Override
    public String getUrl() {
        return webView.getUrl();
    }

    @Override
    public View getView() {
        return webView;
    }

    @Override
    public void setEngineCallback(EngineCallback callback) {
        this.callback = callback;
    }
}
""")

# 3. NavigationManager.java
write_java("browser/NavigationManager.java", """package com.yangkaibrowser.legacy.browser;

import java.util.regex.Pattern;

public class NavigationManager {
    public static final String HOMEPAGE_URL = "file:///android_asset/homepage.html";
    private static final Pattern URL_PATTERN = Pattern.compile("^(https?://|file:///|ftp://)?[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}(/.*)?$");

    public static String resolveInput(String input, String searchEngineUrl) {
        if (input == null || input.trim().isEmpty()) {
            return HOMEPAGE_URL;
        }
        String clean = input.trim();
        if (clean.equalsIgnoreCase("about:blank") || clean.equalsIgnoreCase("yangkai://home")) {
            return HOMEPAGE_URL;
        }
        if (clean.startsWith("http://") || clean.startsWith("https://") || clean.startsWith("file:///")) {
            return clean;
        }
        if (URL_PATTERN.matcher(clean).matches() || clean.contains("localhost") || clean.contains("192.168.")) {
            return "http://" + clean;
        }
        // Search query
        try {
            return searchEngineUrl + java.net.URLEncoder.encode(clean, "UTF-8");
        } catch (Exception e) {
            return searchEngineUrl + clean;
        }
    }
}
""")

# 4. BrowserController.java
write_java("browser/BrowserController.java", """package com.yangkaibrowser.legacy.browser;

import android.content.Context;
import android.widget.FrameLayout;

public class BrowserController {
    private final Context context;
    private final FrameLayout container;
    private BrowserEngine activeEngine;

    public BrowserController(Context context, FrameLayout container) {
        this.context = context;
        this.container = container;
    }

    public void attachEngine(BrowserEngine engine) {
        this.activeEngine = engine;
        container.removeAllViews();
        if (engine != null && engine.getView() != null) {
            container.addView(engine.getView(), new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            ));
        }
    }

    public BrowserEngine getActiveEngine() {
        return activeEngine;
    }
}
""")

# 5. RemoteManager.java
write_java("tv/RemoteManager.java", """package com.yangkaibrowser.legacy.tv;

import android.view.KeyEvent;

public class RemoteManager {
    private KeyEventListener listener;
    private String lastKeyName = "None";
    private int lastKeyCode = 0;
    private int lastAction = 0;
    private int repeatCount = 0;

    public interface KeyEventListener {
        boolean onDpadUp();
        boolean onDpadDown();
        boolean onDpadLeft();
        boolean onDpadRight();
        boolean onDpadCenter();
        boolean onBackKey();
        boolean onMenuKey();
    }

    public void setListener(KeyEventListener listener) {
        this.listener = listener;
    }

    public boolean dispatchKeyEvent(KeyEvent event) {
        if (event == null) return false;

        this.lastKeyCode = event.getKeyCode();
        this.lastAction = event.getAction();
        this.repeatCount = event.getRepeatCount();
        this.lastKeyName = KeyEvent.keyCodeToString(lastKeyCode);

        if (event.getAction() != KeyEvent.ACTION_DOWN) {
            return false;
        }

        if (listener == null) return false;

        switch (event.getKeyCode()) {
            case KeyEvent.KEYCODE_DPAD_UP:
                return listener.onDpadUp();
            case KeyEvent.KEYCODE_DPAD_DOWN:
                return listener.onDpadDown();
            case KeyEvent.KEYCODE_DPAD_LEFT:
                return listener.onDpadLeft();
            case KeyEvent.KEYCODE_DPAD_RIGHT:
                return listener.onDpadRight();
            case KeyEvent.KEYCODE_DPAD_CENTER:
            case KeyEvent.KEYCODE_ENTER:
                return listener.onDpadCenter();
            case KeyEvent.KEYCODE_BACK:
                return listener.onBackKey();
            case KeyEvent.KEYCODE_MENU:
                return listener.onMenuKey();
            default:
                return false;
        }
    }

    public String getLastKeyName() {
        return lastKeyName;
    }

    public int getLastKeyCode() {
        return lastKeyCode;
    }

    public int getLastAction() {
        return lastAction;
    }

    public int getRepeatCount() {
        return repeatCount;
    }
}
""")

# 6. FocusManager.java
write_java("tv/FocusManager.java", """package com.yangkaibrowser.legacy.tv;

import android.view.View;

public class FocusManager {
    public static void requestInitialFocus(View view) {
        if (view != null) {
            view.setFocusable(true);
            view.requestFocus();
        }
    }
}
""")

# 7. CursorManager.java
write_java("tv/CursorManager.java", """package com.yangkaibrowser.legacy.tv;

import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ImageView;

public class CursorManager {
    private final ImageView cursorView;
    private final View targetContainer;
    private boolean isCursorMode = false;
    private float cursorX = 300f;
    private float cursorY = 200f;
    private int speedStep = 18;

    public CursorManager(ImageView cursorView, View targetContainer) {
        this.cursorView = cursorView;
        this.targetContainer = targetContainer;
    }

    public void setCursorMode(boolean enabled) {
        this.isCursorMode = enabled;
        if (cursorView != null) {
            cursorView.setVisibility(enabled ? View.VISIBLE : View.GONE);
            if (enabled) {
                updatePosition();
            }
        }
    }

    public boolean isCursorMode() {
        return isCursorMode;
    }

    public void setSpeed(int speed) {
        if (speed > 0) this.speedStep = speed;
    }

    public void move(int dx, int dy) {
        if (!isCursorMode) return;
        cursorX += dx * speedStep;
        cursorY += dy * speedStep;

        if (targetContainer != null) {
            int maxX = targetContainer.getWidth() - 20;
            int maxY = targetContainer.getHeight() - 20;
            if (cursorX < 0) cursorX = 0;
            if (cursorY < 0) cursorY = 0;
            if (maxX > 0 && cursorX > maxX) cursorX = maxX;
            if (maxY > 0 && cursorY > maxY) cursorY = maxY;
        }
        updatePosition();
    }

    private void updatePosition() {
        if (cursorView != null) {
            cursorView.setX(cursorX);
            cursorView.setY(cursorY);
        }
    }

    public void click() {
        if (!isCursorMode || targetContainer == null) return;
        long downTime = SystemClock.uptimeMillis();
        long eventTime = SystemClock.uptimeMillis();
        MotionEvent downEvent = MotionEvent.obtain(downTime, eventTime, MotionEvent.ACTION_DOWN, cursorX, cursorY, 0);
        MotionEvent upEvent = MotionEvent.obtain(downTime, eventTime + 50, MotionEvent.ACTION_UP, cursorX, cursorY, 0);
        targetContainer.dispatchTouchEvent(downEvent);
        targetContainer.dispatchTouchEvent(upEvent);
        downEvent.recycle();
        upEvent.recycle();
    }
}
""")

# 8. TabManager.java
write_java("tabs/TabManager.java", """package com.yangkaibrowser.legacy.tabs;

import android.content.Context;
import com.yangkaibrowser.legacy.browser.BrowserEngine;
import com.yangkaibrowser.legacy.browser.LegacyWebViewEngine;
import com.yangkaibrowser.legacy.browser.NavigationManager;
import java.util.ArrayList;
import java.util.List;

public class TabManager {
    public static final int MAX_TABS = 3;
    private final Context context;
    private final List<TabItem> tabs = new ArrayList<TabItem>();
    private int activeIndex = 0;

    public static class TabItem {
        public String url;
        public String title;
        public BrowserEngine engine;

        public TabItem(String url, String title, BrowserEngine engine) {
            this.url = url;
            this.title = title;
            this.engine = engine;
        }
    }

    public TabManager(Context context) {
        this.context = context;
        // Start with default Tab 1
        BrowserEngine engine = new LegacyWebViewEngine(context);
        tabs.add(new TabItem(NavigationManager.HOMEPAGE_URL, "Home", engine));
    }

    public TabItem getActiveTab() {
        if (tabs.isEmpty()) return null;
        if (activeIndex < 0 || activeIndex >= tabs.size()) activeIndex = 0;
        return tabs.get(activeIndex);
    }

    public int getActiveIndex() {
        return activeIndex;
    }

    public List<TabItem> getTabs() {
        return tabs;
    }

    public boolean addTab(String url) {
        if (tabs.size() >= MAX_TABS) {
            return false; // RAM protection policy: Max 3 tabs
        }
        BrowserEngine engine = new LegacyWebViewEngine(context);
        engine.loadUrl(url != null ? url : NavigationManager.HOMEPAGE_URL);
        tabs.add(new TabItem(url, "New Tab", engine));
        activeIndex = tabs.size() - 1;
        return true;
    }

    public void selectTab(int index) {
        if (index >= 0 && index < tabs.size()) {
            activeIndex = index;
            TabItem current = tabs.get(index);
            if (current.engine == null) {
                // Rehydrate evicted WebView
                current.engine = new LegacyWebViewEngine(context);
                current.engine.loadUrl(current.url);
            }
        }
    }

    public void closeTab(int index) {
        if (tabs.size() <= 1) return; // Keep at least one tab
        if (index >= 0 && index < tabs.size()) {
            TabItem item = tabs.remove(index);
            if (item.engine != null) {
                item.engine.destroy();
            }
            if (activeIndex >= tabs.size()) {
                activeIndex = tabs.size() - 1;
            }
        }
    }

    public void evictInactiveWebViews() {
        for (int i = 0; i < tabs.size(); i++) {
            if (i != activeIndex) {
                TabItem item = tabs.get(i);
                if (item.engine != null) {
                    item.url = item.engine.getUrl();
                    item.title = item.engine.getTitle();
                    item.engine.destroy();
                    item.engine = null;
                }
            }
        }
    }
}
""")

# 9. BrowserDatabaseHelper.java
write_java("data/BrowserDatabaseHelper.java", """package com.yangkaibrowser.legacy.data;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class BrowserDatabaseHelper extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "yangkai_browser.db";
    private static final int DATABASE_VERSION = 1;

    public static final String TABLE_HISTORY = "history";
    public static final String TABLE_BOOKMARKS = "bookmarks";
    public static final String TABLE_DOWNLOADS = "downloads";

    public BrowserDatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE " + TABLE_HISTORY + " ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "url TEXT NOT NULL, "
                + "title TEXT, "
                + "timestamp INTEGER NOT NULL);");

        db.execSQL("CREATE TABLE " + TABLE_BOOKMARKS + " ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "title TEXT NOT NULL, "
                + "url TEXT NOT NULL, "
                + "created_at INTEGER NOT NULL);");

        db.execSQL("CREATE TABLE " + TABLE_DOWNLOADS + " ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "filename TEXT NOT NULL, "
                + "url TEXT, "
                + "status TEXT, "
                + "timestamp INTEGER NOT NULL);");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_HISTORY);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_BOOKMARKS);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_DOWNLOADS);
        onCreate(db);
    }
}
""")

# 10. HistoryManager.java
write_java("data/HistoryManager.java", """package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.ArrayList;
import java.util.List;

public class HistoryManager {
    private static final int MAX_HISTORY_ITEMS = 300;
    private final BrowserDatabaseHelper dbHelper;

    public static class HistoryEntry {
        public long id;
        public String url;
        public String title;
        public long timestamp;

        public HistoryEntry(long id, String url, String title, long timestamp) {
            this.id = id;
            this.url = url;
            this.title = title;
            this.timestamp = timestamp;
        }
    }

    public HistoryManager(Context context) {
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public void addEntry(String url, String title) {
        if (url == null || url.startsWith("file:///android_asset/")) return;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            ContentValues cv = new ContentValues();
            cv.put("url", url);
            cv.put("title", title != null ? title : url);
            cv.put("timestamp", System.currentTimeMillis());
            db.insert(BrowserDatabaseHelper.TABLE_HISTORY, null, cv);

            // Maintain max 300 items limit
            db.execSQL("DELETE FROM " + BrowserDatabaseHelper.TABLE_HISTORY +
                       " WHERE id NOT IN (SELECT id FROM " + BrowserDatabaseHelper.TABLE_HISTORY +
                       " ORDER BY timestamp DESC LIMIT " + MAX_HISTORY_ITEMS + ")");
        } catch (Exception ignored) {}
    }

    public List<HistoryEntry> getRecentEntries(int limit) {
        List<HistoryEntry> list = new ArrayList<HistoryEntry>();
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            Cursor c = db.rawQuery("SELECT id, url, title, timestamp FROM " +
                    BrowserDatabaseHelper.TABLE_HISTORY + " ORDER BY timestamp DESC LIMIT " + limit, null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new HistoryEntry(c.getLong(0), c.getString(1), c.getString(2), c.getLong(3)));
                }
                c.close();
            }
        } catch (Exception ignored) {}
        return list;
    }

    public void clearAll() {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_HISTORY, null, null);
        } catch (Exception ignored) {}
    }
}
""")

# 11. BookmarkManager.java
write_java("data/BookmarkManager.java", """package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.ArrayList;
import java.util.List;

public class BookmarkManager {
    private final BrowserDatabaseHelper dbHelper;

    public static class BookmarkItem {
        public long id;
        public String title;
        public String url;

        public BookmarkItem(long id, String title, String url) {
            this.id = id;
            this.title = title;
            this.url = url;
        }
    }

    public BookmarkManager(Context context) {
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public void addBookmark(String title, String url) {
        if (url == null || url.isEmpty()) return;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            ContentValues cv = new ContentValues();
            cv.put("title", (title != null && !title.isEmpty()) ? title : url);
            cv.put("url", url);
            cv.put("created_at", System.currentTimeMillis());
            db.insert(BrowserDatabaseHelper.TABLE_BOOKMARKS, null, cv);
        } catch (Exception ignored) {}
    }

    public List<BookmarkItem> getAllBookmarks() {
        List<BookmarkItem> list = new ArrayList<BookmarkItem>();
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            Cursor c = db.rawQuery("SELECT id, title, url FROM " + BrowserDatabaseHelper.TABLE_BOOKMARKS + " ORDER BY id DESC", null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new BookmarkItem(c.getLong(0), c.getString(1), c.getString(2)));
                }
                c.close();
            }
        } catch (Exception ignored) {}
        return list;
    }

    public void deleteBookmark(long id) {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_BOOKMARKS, "id = ?", new String[]{String.valueOf(id)});
        } catch (Exception ignored) {}
    }
}
""")

# 12. DownloadManager.java
write_java("data/DownloadManager.java", """package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;

public class DownloadManager {
    private final BrowserDatabaseHelper dbHelper;

    public DownloadManager(Context context) {
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public void recordDownload(String filename, String url, String status) {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            ContentValues cv = new ContentValues();
            cv.put("filename", filename);
            cv.put("url", url);
            cv.put("status", status);
            cv.put("timestamp", System.currentTimeMillis());
            db.insert(BrowserDatabaseHelper.TABLE_DOWNLOADS, null, cv);
        } catch (Exception ignored) {}
    }
}
""")

# 13. MemoryManager.java
write_java("performance/MemoryManager.java", """package com.yangkaibrowser.legacy.performance;

public class MemoryManager {
    public enum MemoryState {
        NORMAL,
        WARNING,
        CRITICAL,
        EMERGENCY
    }

    public static MemoryState evaluateMemory() {
        Runtime rt = Runtime.getRuntime();
        long maxMemory = rt.maxMemory();
        long totalMemory = rt.totalMemory();
        long freeMemory = rt.freeMemory();
        long usedMemory = totalMemory - freeMemory;

        if (maxMemory <= 0) return MemoryState.NORMAL;
        double ratio = (double) usedMemory / (double) maxMemory;

        if (ratio > 0.88) {
            return MemoryState.EMERGENCY;
        } else if (ratio > 0.78) {
            return MemoryState.CRITICAL;
        } else if (ratio > 0.65) {
            return MemoryState.WARNING;
        } else {
            return MemoryState.NORMAL;
        }
    }

    public static String getMemorySummary() {
        Runtime rt = Runtime.getRuntime();
        long usedMB = (rt.totalMemory() - rt.freeMemory()) / (1024 * 1024);
        long maxMB = rt.maxMemory() / (1024 * 1024);
        MemoryState state = evaluateMemory();
        return "MEM: " + state.name() + " (" + usedMB + "MB / " + maxMB + "MB)";
    }
}
""")

# 14. CacheManager.java
write_java("performance/CacheManager.java", """package com.yangkaibrowser.legacy.performance;

import android.content.Context;
import java.io.File;

public class CacheManager {
    public static void clearAppCache(Context context) {
        try {
            File cacheDir = context.getCacheDir();
            deleteDir(cacheDir);
        } catch (Exception ignored) {}
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
""")

# 15. PerformanceMonitor.java
write_java("performance/PerformanceMonitor.java", """package com.yangkaibrowser.legacy.performance;

public class PerformanceMonitor {
    private static long startTime = 0;

    public static void markStart() {
        startTime = System.currentTimeMillis();
    }

    public static long getElapsedMs() {
        if (startTime == 0) return 0;
        return System.currentTimeMillis() - startTime;
    }
}
""")

# 16. SettingsManager.java
write_java("settings/SettingsManager.java", """package com.yangkaibrowser.legacy.settings;

import android.content.Context;
import android.content.SharedPreferences;

public class SettingsManager {
    private static final String PREF_NAME = "yangkai_prefs";
    public static final String KEY_SEARCH_ENGINE = "search_engine";
    public static final String KEY_JAVASCRIPT = "js_enabled";
    public static final String KEY_IMAGES = "images_enabled";
    public static final String KEY_CURSOR_SPEED = "cursor_speed";

    private final SharedPreferences prefs;

    public SettingsManager(Context context) {
        this.prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public String getSearchEngine() {
        return prefs.getString(KEY_SEARCH_ENGINE, "https://html.duckduckgo.com/html/?q=");
    }

    public void setSearchEngine(String url) {
        prefs.edit().putString(KEY_SEARCH_ENGINE, url).commit();
    }

    public boolean isJavaScriptEnabled() {
        return prefs.getBoolean(KEY_JAVASCRIPT, true);
    }

    public void setJavaScriptEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_JAVASCRIPT, enabled).commit();
    }

    public boolean isImagesEnabled() {
        return prefs.getBoolean(KEY_IMAGES, true);
    }

    public void setImagesEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_IMAGES, enabled).commit();
    }

    public int getCursorSpeed() {
        return prefs.getInt(KEY_CURSOR_SPEED, 20);
    }

    public void setCursorSpeed(int speed) {
        prefs.edit().putInt(KEY_CURSOR_SPEED, speed).commit();
    }
}
""")

# 17. LegacyCompatibility.java
write_java("compatibility/LegacyCompatibility.java", """package com.yangkaibrowser.legacy.compatibility;

import android.os.Build;

public class LegacyCompatibility {
    public static boolean isKitKat() {
        return Build.VERSION.SDK_INT == Build.VERSION_CODES.KITKAT;
    }

    public static String getDeviceInfo() {
        return "Model: " + Build.MODEL + " | ABI: " + Build.CPU_ABI + " | API: " + Build.VERSION.SDK_INT;
    }
}
""")

# 18. MainActivity.java
write_java("MainActivity.java", """package com.yangkaibrowser.legacy;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.yangkaibrowser.legacy.browser.BrowserController;
import com.yangkaibrowser.legacy.browser.BrowserEngine;
import com.yangkaibrowser.legacy.browser.NavigationManager;
import com.yangkaibrowser.legacy.data.BookmarkManager;
import com.yangkaibrowser.legacy.data.HistoryManager;
import com.yangkaibrowser.legacy.performance.CacheManager;
import com.yangkaibrowser.legacy.performance.MemoryManager;
import com.yangkaibrowser.legacy.performance.PerformanceMonitor;
import com.yangkaibrowser.legacy.settings.SettingsManager;
import com.yangkaibrowser.legacy.tabs.TabManager;
import com.yangkaibrowser.legacy.tv.CursorManager;
import com.yangkaibrowser.legacy.tv.FocusManager;
import com.yangkaibrowser.legacy.tv.RemoteManager;

import java.util.List;

public class MainActivity extends Activity implements RemoteManager.KeyEventListener, BrowserEngine.EngineCallback {

    private BrowserController browserController;
    private TabManager tabManager;
    private HistoryManager historyManager;
    private BookmarkManager bookmarkManager;
    private SettingsManager settingsManager;
    private RemoteManager remoteManager;
    private CursorManager cursorManager;

    private EditText urlInput;
    private ProgressBar progressBar;
    private Button btnBack;
    private Button btnForward;
    private Button btnReload;
    private Button btnHome;
    private Button btnGo;
    private Button btnTabs;
    private Button btnCursorToggle;
    private Button btnMenu;
    private TextView tvMemStatus;
    private TextView tvModeStatus;
    private LinearLayout keyEventOverlay;
    private TextView tvLastKey;
    private TextView tvKeyCode;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        PerformanceMonitor.markStart();
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initManagers();
        initViews();
        setupListeners();

        // Load initial local homepage
        loadTab(0);
        updateMemoryStatus();
    }

    private void initManagers() {
        historyManager = new HistoryManager(this);
        bookmarkManager = new BookmarkManager(this);
        settingsManager = new SettingsManager(this);
        remoteManager = new RemoteManager();
        remoteManager.setListener(this);
        tabManager = new TabManager(this);
    }

    private void initViews() {
        FrameLayout webContainer = (FrameLayout) findViewById(R.id.webview_container);
        browserController = new BrowserController(this, webContainer);

        urlInput = (EditText) findViewById(R.id.url_input);
        progressBar = (ProgressBar) findViewById(R.id.progress_bar);
        btnBack = (Button) findViewById(R.id.btn_back);
        btnForward = (Button) findViewById(R.id.btn_forward);
        btnReload = (Button) findViewById(R.id.btn_reload);
        btnHome = (Button) findViewById(R.id.btn_home);
        btnGo = (Button) findViewById(R.id.btn_go);
        btnTabs = (Button) findViewById(R.id.btn_tabs);
        btnCursorToggle = (Button) findViewById(R.id.btn_cursor_toggle);
        btnMenu = (Button) findViewById(R.id.btn_menu);
        tvMemStatus = (TextView) findViewById(R.id.tv_mem_status);
        tvModeStatus = (TextView) findViewById(R.id.tv_mode_status);

        ImageView cursorImg = (ImageView) findViewById(R.id.virtual_cursor);
        cursorManager = new CursorManager(cursorImg, webContainer);

        keyEventOverlay = (LinearLayout) findViewById(R.id.key_event_overlay);
        tvLastKey = (TextView) findViewById(R.id.tv_last_key);
        tvKeyCode = (TextView) findViewById(R.id.tv_key_code);

        // Initial focus strictly on URL bar for fast TV interaction
        FocusManager.requestInitialFocus(urlInput);
    }

    private void setupListeners() {
        btnBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                navigateBack();
            }
        });

        btnForward.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                BrowserEngine engine = browserController.getActiveEngine();
                if (engine != null && engine.canGoForward()) {
                    engine.goForward();
                }
            }
        });

        btnReload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                BrowserEngine engine = browserController.getActiveEngine();
                if (engine != null) engine.reload();
            }
        });

        btnHome.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loadUrl(NavigationManager.HOMEPAGE_URL);
            }
        });

        btnGo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                submitUrlInput();
            }
        });

        urlInput.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                if (actionId == EditorInfo.IME_ACTION_GO || (event != null && event.getKeyCode() == KeyEvent.KEYCODE_ENTER)) {
                    submitUrlInput();
                    return true;
                }
                return false;
            }
        });

        btnTabs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showTabsDialog();
            }
        });

        btnCursorToggle.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                toggleCursorMode();
            }
        });

        btnMenu.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showMenuDialog();
            }
        });
    }

    private void submitUrlInput() {
        String input = urlInput.getText().toString();
        String resolved = NavigationManager.resolveInput(input, settingsManager.getSearchEngine());
        loadUrl(resolved);
        // Hide keyboard / unfocus to return to web content
        urlInput.clearFocus();
    }

    private void loadUrl(String url) {
        BrowserEngine engine = browserController.getActiveEngine();
        if (engine != null) {
            engine.loadUrl(url);
            updateMemoryStatus();
        }
    }

    private void loadTab(int index) {
        tabManager.selectTab(index);
        TabManager.TabItem tab = tabManager.getActiveTab();
        if (tab != null && tab.engine != null) {
            tab.engine.setEngineCallback(this);
            browserController.attachEngine(tab.engine);
            tab.engine.loadUrl(tab.url != null ? tab.url : NavigationManager.HOMEPAGE_URL);
            btnTabs.setText("Tabs (" + tabManager.getTabs().size() + ")");
        }
    }

    private void toggleCursorMode() {
        boolean next = !cursorManager.isCursorMode();
        cursorManager.setCursorMode(next);
        btnCursorToggle.setText(next ? "🎯 DPAD" : "🎯 Pointer");
        tvModeStatus.setText(next ? "MODE: VIRTUAL CURSOR" : "MODE: DPAD FOCUS");
        Toast.makeText(this, next ? "Virtual Cursor Active (Use D-Pad arrows)" : "DPAD Focus Navigation Active", Toast.LENGTH_SHORT).show();
    }

    private void updateMemoryStatus() {
        tvMemStatus.setText(MemoryManager.getMemorySummary());
        // Auto-evict inactive tabs if under memory pressure
        if (MemoryManager.evaluateMemory() == MemoryManager.MemoryState.CRITICAL ||
            MemoryManager.evaluateMemory() == MemoryManager.MemoryState.EMERGENCY) {
            tabManager.evictInactiveWebViews();
        }
    }

    private void navigateBack() {
        BrowserEngine engine = browserController.getActiveEngine();
        if (engine != null && engine.canGoBack()) {
            engine.goBack();
        } else {
            // Confirm exit dialog to avoid accidental exit on TV
            new AlertDialog.Builder(this)
                .setTitle("Exit Yang Kai Browser?")
                .setMessage("Do you want to exit the browser?")
                .setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        finish();
                    }
                })
                .setNegativeButton("Stay", null)
                .show();
        }
    }

    // RemoteManager.KeyEventListener implementations
    @Override
    public boolean onDpadUp() {
        if (cursorManager.isCursorMode()) {
            cursorManager.move(0, -1);
            return true;
        }
        return false;
    }

    @Override
    public boolean onDpadDown() {
        if (cursorManager.isCursorMode()) {
            cursorManager.move(0, 1);
            return true;
        }
        return false;
    }

    @Override
    public boolean onDpadLeft() {
        if (cursorManager.isCursorMode()) {
            cursorManager.move(-1, 0);
            return true;
        }
        return false;
    }

    @Override
    public boolean onDpadRight() {
        if (cursorManager.isCursorMode()) {
            cursorManager.move(1, 0);
            return true;
        }
        return false;
    }

    @Override
    public boolean onDpadCenter() {
        if (cursorManager.isCursorMode()) {
            cursorManager.click();
            return true;
        }
        return false;
    }

    @Override
    public boolean onBackKey() {
        navigateBack();
        return true;
    }

    @Override
    public boolean onMenuKey() {
        showMenuDialog();
        return true;
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        // Record forensic key logs
        if (keyEventOverlay.getVisibility() == View.VISIBLE) {
            tvLastKey.setText("Last Key: " + KeyEvent.keyCodeToString(event.getKeyCode()));
            tvKeyCode.setText("KeyCode: " + event.getKeyCode() + " | Action: " + event.getAction());
        }

        if (remoteManager.dispatchKeyEvent(event)) {
            return true;
        }
        return super.dispatchKeyEvent(event);
    }

    // EngineCallback implementation
    @Override
    public void onProgress(int progress) {
        if (progress > 0 && progress < 100) {
            progressBar.setVisibility(View.VISIBLE);
            progressBar.setProgress(progress);
        } else {
            progressBar.setVisibility(View.GONE);
        }
    }

    @Override
    public void onTitleReceived(String title) {
        TabManager.TabItem active = tabManager.getActiveTab();
        if (active != null) active.title = title;
        if (title != null && !title.isEmpty() && !title.startsWith("http")) {
            urlInput.setHint(title);
        }
    }

    @Override
    public void onUrlChanged(String url) {
        if (url != null && !url.equals(urlInput.getText().toString())) {
            urlInput.setText(url);
            historyManager.addEntry(url, browserController.getActiveEngine() != null ? browserController.getActiveEngine().getTitle() : url);
        }
        updateMemoryStatus();
    }

    @Override
    public void onLoadingStateChanged(boolean isLoading) {
        btnReload.setText(isLoading ? "✕" : "⟳");
        updateMemoryStatus();
    }

    @Override
    public void onError(int errorCode, String description, String failingUrl) {
        loadUrl("file:///android_asset/error.html");
    }

    @Override
    public void onSslError(String failingUrl) {
        Toast.makeText(this, "SSL Security Warning: Insecure connection blocked on legacy TV", Toast.LENGTH_LONG).show();
        loadUrl("file:///android_asset/error.html");
    }

    private void showTabsDialog() {
        List<TabManager.TabItem> tabs = tabManager.getTabs();
        String[] items = new String[tabs.size() + 1];
        for (int i = 0; i < tabs.size(); i++) {
            items[i] = (i == tabManager.getActiveIndex() ? "● " : "○ ") + "Tab " + (i + 1) + ": " + (tabs.get(i).title != null ? tabs.get(i).title : "Untitled");
        }
        items[tabs.size()] = "➕ New Tab (Max " + TabManager.MAX_TABS + ")";

        new AlertDialog.Builder(this)
            .setTitle(R.string.dialog_title_tabs)
            .setItems(items, new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    if (which < tabManager.getTabs().size()) {
                        loadTab(which);
                    } else {
                        if (!tabManager.addTab(NavigationManager.HOMEPAGE_URL)) {
                            Toast.makeText(MainActivity.this, "RAM Safety Policy: Maximum 3 tabs on 512MB RAM", Toast.LENGTH_SHORT).show();
                        } else {
                            loadTab(tabManager.getActiveIndex());
                        }
                    }
                }
            })
            .show();
    }

    private void showMenuDialog() {
        String[] menu = new String[]{
            "⭐ Add Current Page to Bookmarks",
            "📖 Open Bookmarks",
            "🕒 Browsing History",
            "🩺 Legacy Hardware Diagnostics",
            "🔍 Key Event Tester (Forensic Overlay)",
            "🧹 Clear Cache & Free RAM",
            "⚙️ Settings",
            "ℹ️ About Yang Kai Browser"
        };

        new AlertDialog.Builder(this)
            .setTitle(R.string.btn_menu)
            .setItems(menu, new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    switch (which) {
                        case 0:
                            if (browserController.getActiveEngine() != null) {
                                bookmarkManager.addBookmark(browserController.getActiveEngine().getTitle(), browserController.getActiveEngine().getUrl());
                                Toast.makeText(MainActivity.this, "Bookmark Saved!", Toast.LENGTH_SHORT).show();
                            }
                            break;
                        case 1:
                            showBookmarksDialog();
                            break;
                        case 2:
                            showHistoryDialog();
                            break;
                        case 3:
                            loadUrl("file:///android_asset/diagnostics.html");
                            break;
                        case 4:
                            boolean show = keyEventOverlay.getVisibility() != View.VISIBLE;
                            keyEventOverlay.setVisibility(show ? View.VISIBLE : View.GONE);
                            Toast.makeText(MainActivity.this, show ? "Key Event Tester Enabled" : "Key Event Tester Disabled", Toast.LENGTH_SHORT).show();
                            break;
                        case 5:
                            CacheManager.clearAppCache(MainActivity.this);
                            if (browserController.getActiveEngine() != null) {
                                browserController.getActiveEngine().clearCache(true);
                            }
                            tabManager.evictInactiveWebViews();
                            System.gc();
                            updateMemoryStatus();
                            Toast.makeText(MainActivity.this, "Memory & Cache Cleared!", Toast.LENGTH_SHORT).show();
                            break;
                        case 6:
                            showSettingsDialog();
                            break;
                        case 7:
                            showAboutDialog();
                            break;
                    }
                }
            })
            .show();
    }

    private void showBookmarksDialog() {
        final List<BookmarkManager.BookmarkItem> bookmarks = bookmarkManager.getAllBookmarks();
        if (bookmarks.isEmpty()) {
            Toast.makeText(this, "No bookmarks saved yet.", Toast.LENGTH_SHORT).show();
            return;
        }
        String[] items = new String[bookmarks.size()];
        for (int i = 0; i < bookmarks.size(); i++) {
            items[i] = bookmarks.get(i).title;
        }
        new AlertDialog.Builder(this)
            .setTitle(R.string.dialog_title_bookmarks)
            .setItems(items, new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    loadUrl(bookmarks.get(which).url);
                }
            })
            .show();
    }

    private void showHistoryDialog() {
        final List<HistoryManager.HistoryEntry> history = historyManager.getRecentEntries(50);
        if (history.isEmpty()) {
            Toast.makeText(this, "Browsing history is empty.", Toast.LENGTH_SHORT).show();
            return;
        }
        String[] items = new String[history.size()];
        for (int i = 0; i < history.size(); i++) {
            items[i] = history.get(i).title != null ? history.get(i).title : history.get(i).url;
        }
        new AlertDialog.Builder(this)
            .setTitle(R.string.dialog_title_history)
            .setItems(items, new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    loadUrl(history.get(which).url);
                }
            })
            .setPositiveButton("Clear History", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    historyManager.clearAll();
                    Toast.makeText(MainActivity.this, "History Cleared!", Toast.LENGTH_SHORT).show();
                }
            })
            .show();
    }

    private void showSettingsDialog() {
        final String[] options = new String[]{
            "JavaScript: " + (settingsManager.isJavaScriptEnabled() ? "ENABLED" : "DISABLED"),
            "Images: " + (settingsManager.isImagesEnabled() ? "ENABLED" : "DISABLED"),
            "Search Engine: DuckDuckGo Lite",
            "Cursor Speed: " + settingsManager.getCursorSpeed() + "px/step"
        };
        new AlertDialog.Builder(this)
            .setTitle(R.string.dialog_title_settings)
            .setItems(options, new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    if (which == 0) {
                        boolean next = !settingsManager.isJavaScriptEnabled();
                        settingsManager.setJavaScriptEnabled(next);
                        if (browserController.getActiveEngine() != null) {
                            browserController.getActiveEngine().setJavaScriptEnabled(next);
                        }
                    } else if (which == 1) {
                        boolean next = !settingsManager.isImagesEnabled();
                        settingsManager.setImagesEnabled(next);
                        if (browserController.getActiveEngine() != null) {
                            browserController.getActiveEngine().setImagesEnabled(next);
                        }
                    }
                    Toast.makeText(MainActivity.this, "Setting updated", Toast.LENGTH_SHORT).show();
                }
            })
            .show();
    }

    private void showAboutDialog() {
        new AlertDialog.Builder(this)
            .setTitle("🐉 Yang Kai Browser")
            .setMessage("Version: 1.0.0 (Build 2026.09)\n" +
                        "Architecture: ARM32 / Dalvik API 19\n" +
                        "Engine: Android System WebView\n" +
                        "Target: Android 4.4.4 KitKat TV Box (512MB RAM)\n" +
                        "Package: com.yangkaibrowser.legacy\n\n" +
                        "Autonomous, telemetry-free, remote-first legacy web browser engineered for extreme efficiency.")
            .setPositiveButton("OK", null)
            .show();
    }
}
""")

print("[+] All Java source files written successfully")
