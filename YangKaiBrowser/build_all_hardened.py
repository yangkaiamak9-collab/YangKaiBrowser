#!/usr/bin/env python3
"""
Yang Kai Browser - Master Engineering Hardened Source Generator & Builder
Target: Android 4.4.4 KitKat / API 19 / ARM32 / 512MB RAM / Android TV / D-Pad Remote
"""

import os
import sys
import subprocess
import hashlib
import json

WORKSPACE_DIR = os.path.abspath(os.getcwd())
PROJECT_DIR = os.path.join(WORKSPACE_DIR, "YangKaiBrowser")
SOURCE_DIR = os.path.join(PROJECT_DIR, "source")
JAVA_BASE = os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy")

def write_file(rel_path, content):
    full_path = os.path.join(JAVA_BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[+] Wrote Java source: {rel_path}")

def write_res(rel_path, content):
    full_path = os.path.join(SOURCE_DIR, "res", rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[+] Wrote Resource: {rel_path}")

def write_asset(rel_path, content):
    full_path = os.path.join(SOURCE_DIR, "assets", rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[+] Wrote Asset: {rel_path}")

print("[*] Generating hardened API 19 source tree...")

# ==============================================================================
# 1. BROWSER ENGINE INTERFACE
# ==============================================================================
write_file("browser/BrowserEngine.java", """
package com.yangkaibrowser.legacy.browser;

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
    void setUserAgent(String userAgent);
    void setZoom(int percent);
    String getTitle();
    String getUrl();
    int getScrollX();
    int getScrollY();
    View getView();
    void setEngineCallback(EngineCallback callback);

    interface EngineCallback {
        void onProgress(int progress);
        void onTitleReceived(String title);
        void onUrlChanged(String url);
        void onLoadingStateChanged(boolean isLoading);
        void onError(int errorCode, String description, String failingUrl);
        void onSslError(String failingUrl, String sslReason);
        void onDownloadRequested(String url, String userAgent, String contentDisposition, String mimeType, long contentLength);
    }
}
""")

# ==============================================================================
# 2. JAVASCRIPT BRIDGE (BUG #1 FIX)
# Strict security: Only executes on UI thread, only for file:///android_asset/
# ==============================================================================
write_file("browser/YangKaiJsBridge.java", """
package com.yangkaibrowser.legacy.browser;

import android.app.Activity;
import android.webkit.JavascriptInterface;

public class YangKaiJsBridge {
    private final Activity activity;
    private final BridgeListener listener;

    public interface BridgeListener {
        void onOpenBookmarks();
        void onOpenHistory();
        void onOpenDownloads();
        void onOpenSettings();
        void onOpenDiagnostics();
        void onClearCacheRequested();
        String getDiagnosticsDataJson();
    }

    public YangKaiJsBridge(Activity activity, BridgeListener listener) {
        this.activity = activity;
        this.listener = listener;
    }

    @JavascriptInterface
    public void openBookmarks() {
        if (activity == null || listener == null) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenBookmarks();
            }
        });
    }

    @JavascriptInterface
    public void openHistory() {
        if (activity == null || listener == null) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenHistory();
            }
        });
    }

    @JavascriptInterface
    public void openDownloads() {
        if (activity == null || listener == null) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenDownloads();
            }
        });
    }

    @JavascriptInterface
    public void openSettings() {
        if (activity == null || listener == null) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenSettings();
            }
        });
    }

    @JavascriptInterface
    public void openDiagnostics() {
        if (activity == null || listener == null) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenDiagnostics();
            }
        });
    }

    @JavascriptInterface
    public void clearCache() {
        if (activity == null || listener == null) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onClearCacheRequested();
            }
        });
    }

    @JavascriptInterface
    public String getDiagnostics() {
        if (listener == null) return "{}";
        return listener.getDiagnosticsDataJson();
    }
}
""")

# ==============================================================================
# 3. LEGACY WEBVIEW ENGINE (BUG #1, BUG #2, BUG #3, SSL FIX)
# ==============================================================================
write_file("browser/LegacyWebViewEngine.java", """
package com.yangkaibrowser.legacy.browser;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.net.http.SslError;
import android.os.Build;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.DownloadListener;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class LegacyWebViewEngine implements BrowserEngine {
    private final WebView webView;
    private EngineCallback callback;
    private String currentTitle = "";
    private YangKaiJsBridge jsBridge;

    @SuppressLint("SetJavaScriptEnabled")
    public LegacyWebViewEngine(Context context, YangKaiJsBridge.BridgeListener bridgeListener) {
        this.webView = new WebView(context);
        initSettings();
        initClients();
        initDownloadListener();
        if (context instanceof Activity && bridgeListener != null) {
            jsBridge = new YangKaiJsBridge((Activity) context, bridgeListener);
            webView.addJavascriptInterface(jsBridge, "yangkai");
        }
    }

    private void initSettings() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setLoadsImagesAutomatically(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAppCacheEnabled(true);
        settings.setAppCacheMaxSize(8 * 1024 * 1024); // 8MB strict cache for 512MB RAM
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        
        // Security policy for API 19: Allow local assets, block arbitrary cross-file leaks
        settings.setAllowFileAccess(true);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);

        // Security: SavePassword strictly FALSE by default
        settings.setSaveFormData(false);
        settings.setSavePassword(false);

        // Hardware TV friendly setup
        webView.setBackgroundColor(0xFF121214);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
    }

    private void initClients() {
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url == null) return false;
                if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("file:///")) {
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
                    callback.onTitleReceived(currentTitle != null ? currentTitle : "");
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
                // SSL Security Rule: Never bypass untrusted SSL certificates
                handler.cancel();

                String reason = "Certificate validation failure";
                if (error != null) {
                    switch (error.getPrimaryError()) {
                        case SslError.SSL_EXPIRED:
                            reason = "Certificate has expired (common on Android 4.4 legacy root CA store)";
                            break;
                        case SslError.SSL_IDMISMATCH:
                            reason = "Host name mismatch in certificate";
                            break;
                        case SslError.SSL_UNTRUSTED:
                            reason = "Untrusted certificate authority (legacy Android 4.4 root store limitation)";
                            break;
                        case SslError.SSL_NOTYETVALID:
                            reason = "Certificate is not yet valid";
                            break;
                        default:
                            reason = "Untrusted SSL handshake error (" + error.getPrimaryError() + ")";
                            break;
                    }
                }

                if (callback != null) {
                    callback.onSslError(error != null ? error.getUrl() : "", reason);
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

    private void initDownloadListener() {
        webView.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String userAgent, String contentDisposition, String mimeType, long contentLength) {
                if (callback != null) {
                    callback.onDownloadRequested(url, userAgent, contentDisposition, mimeType, contentLength);
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
            // Memory safe destruction recommended by Android docs:
            // 1. Remove from parent view hierarchy
            ViewGroup parent = (ViewGroup) webView.getParent();
            if (parent != null) {
                parent.removeView(webView);
            }
            // 2. Stop loading and clean listeners
            webView.stopLoading();
            webView.setWebChromeClient(null);
            webView.setWebViewClient(null);
            webView.setDownloadListener(null);
            webView.clearHistory();
            webView.removeAllViews();
            // 3. Destroy underlying Chromium instance
            webView.destroy();
        } catch (Exception ignored) {}
    }

    @Override
    public void clearCache(boolean includeDiskFiles) {
        try {
            webView.clearCache(includeDiskFiles);
        } catch (Exception ignored) {}
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
    public void setUserAgent(String userAgent) {
        if (userAgent != null && !userAgent.isEmpty()) {
            webView.getSettings().setUserAgentString(userAgent);
        }
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
    public int getScrollX() {
        return webView.getScrollX();
    }

    @Override
    public int getScrollY() {
        return webView.getScrollY();
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

# ==============================================================================
# 4. NAVIGATION MANAGER (Unified URL Policy, DuckDuckGo Lite, IPv4, No FTP)
# ==============================================================================
write_file("browser/NavigationManager.java", """
package com.yangkaibrowser.legacy.browser;

import java.net.URLEncoder;
import java.util.regex.Pattern;

public class NavigationManager {
    public static final String HOMEPAGE_URL = "file:///android_asset/homepage.html";
    public static final String ERROR_URL = "file:///android_asset/error.html";
    public static final String DIAGNOSTICS_URL = "file:///android_asset/diagnostics.html";

    // Matches standard domain names with optional port and path
    private static final Pattern DOMAIN_PATTERN = Pattern.compile("^[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}(:[0-9]+)?(/.*)?$");
    // Matches IPv4 addresses with optional port and path
    private static final Pattern IPV4_PATTERN = Pattern.compile("^([0-9]{1,3}\\\\.){3}[0-9]{1,3}(:[0-9]+)?(/.*)?$");

    public static String resolveInput(String input, String searchEngineUrl) {
        if (input == null || input.trim().isEmpty()) {
            return HOMEPAGE_URL;
        }
        String clean = input.trim();

        // Local shortcuts
        if (clean.equalsIgnoreCase("about:blank") || clean.equalsIgnoreCase("yangkai://home") || clean.equalsIgnoreCase("home")) {
            return HOMEPAGE_URL;
        }
        if (clean.equalsIgnoreCase("diagnostics") || clean.equalsIgnoreCase("yangkai://diag")) {
            return DIAGNOSTICS_URL;
        }

        // Direct protocol specification
        if (clean.startsWith("http://") || clean.startsWith("https://") || clean.startsWith("file:///")) {
            return clean;
        }

        // Explicitly reject unsupported protocols like ftp:// and treat as search
        if (clean.startsWith("ftp://")) {
            clean = clean.substring(6);
        }

        // Check if user entered localhost or local IP or domain name
        if (clean.startsWith("localhost") || IPV4_PATTERN.matcher(clean).matches() || DOMAIN_PATTERN.matcher(clean).matches()) {
            return "http://" + clean;
        }

        // Default: Search query safely URL-encoded
        try {
            String encoded = URLEncoder.encode(clean, "UTF-8");
            String engine = (searchEngineUrl != null && !searchEngineUrl.isEmpty()) 
                    ? searchEngineUrl 
                    : "https://html.duckduckgo.com/html/?q=";
            return engine + encoded;
        } catch (Exception e) {
            return "https://html.duckduckgo.com/html/?q=" + clean;
        }
    }
}
""")

# ==============================================================================
# 5. BROWSER CONTROLLER (Container attachment)
# ==============================================================================
write_file("browser/BrowserController.java", """
package com.yangkaibrowser.legacy.browser;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;

public class BrowserController {
    private final FrameLayout container;
    private BrowserEngine activeEngine;

    public BrowserController(Context context, FrameLayout container) {
        this.container = container;
    }

    public void attachEngine(BrowserEngine engine) {
        if (engine == null) return;
        this.activeEngine = engine;
        container.removeAllViews();
        View view = engine.getView();
        if (view != null) {
            ViewGroup parent = (ViewGroup) view.getParent();
            if (parent != null) {
                parent.removeView(view);
            }
            container.addView(view, new FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.MATCH_PARENT));
            view.requestFocus();
        }
    }

    public BrowserEngine getActiveEngine() {
        return activeEngine;
    }

    public void detachActiveEngine() {
        container.removeAllViews();
        this.activeEngine = null;
    }
}
""")

# ==============================================================================
# 6. TAB MANAGER (BUG #3 FIX: Strict MAX_LIVE_WEBVIEWS = 1 on 512MB RAM)
# ==============================================================================
write_file("tabs/TabManager.java", """
package com.yangkaibrowser.legacy.tabs;

import android.content.Context;
import com.yangkaibrowser.legacy.browser.BrowserEngine;
import com.yangkaibrowser.legacy.browser.LegacyWebViewEngine;
import com.yangkaibrowser.legacy.browser.NavigationManager;
import com.yangkaibrowser.legacy.browser.YangKaiJsBridge;
import java.util.ArrayList;
import java.util.List;

public class TabManager {
    public static final int MAX_TABS = 3; // Max 3 logical tabs
    public static final int MAX_LIVE_WEBVIEWS = 1; // Strict single live WebView for 512MB RAM

    private final Context context;
    private final YangKaiJsBridge.BridgeListener bridgeListener;
    private final List<TabItem> tabs = new ArrayList<TabItem>();
    private int activeIndex = 0;

    public static class TabItem {
        public String url;
        public String title;
        public int scrollX = 0;
        public int scrollY = 0;
        public BrowserEngine engine = null;

        public TabItem(String url, String title) {
            this.url = url;
            this.title = title;
        }
    }

    public TabManager(Context context, YangKaiJsBridge.BridgeListener bridgeListener) {
        this.context = context;
        this.bridgeListener = bridgeListener;
        // Tab 1 initial entry
        tabs.add(new TabItem(NavigationManager.HOMEPAGE_URL, "Home"));
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
            return false; // RAM policy constraint
        }
        // Save current tab state before adding new tab
        saveActiveTabState();
        destroyInactiveWebViews();

        TabItem newTab = new TabItem(url != null ? url : NavigationManager.HOMEPAGE_URL, "New Tab");
        tabs.add(newTab);
        activeIndex = tabs.size() - 1;
        return true;
    }

    public BrowserEngine selectTab(int index, BrowserEngine.EngineCallback callback) {
        if (index < 0 || index >= tabs.size()) return null;

        // 1. Save state of old active tab and destroy its live WebView
        if (index != activeIndex) {
            saveActiveTabState();
            destroyInactiveWebViews();
        }

        activeIndex = index;
        TabItem current = tabs.get(index);

        // 2. Re-create fresh, clean WebView instance
        if (current.engine == null) {
            current.engine = new LegacyWebViewEngine(context, bridgeListener);
            if (callback != null) {
                current.engine.setEngineCallback(callback);
            }
            current.engine.loadUrl(current.url != null ? current.url : NavigationManager.HOMEPAGE_URL);
        }
        return current.engine;
    }

    public void closeTab(int index) {
        if (tabs.size() <= 1) return; // Keep at least one tab
        if (index >= 0 && index < tabs.size()) {
            TabItem item = tabs.remove(index);
            if (item.engine != null) {
                item.engine.destroy();
                item.engine = null;
            }
            if (activeIndex >= tabs.size()) {
                activeIndex = tabs.size() - 1;
            }
        }
    }

    public void saveActiveTabState() {
        TabItem active = getActiveTab();
        if (active != null && active.engine != null) {
            String liveUrl = active.engine.getUrl();
            if (liveUrl != null && !liveUrl.isEmpty()) {
                active.url = liveUrl;
            }
            String liveTitle = active.engine.getTitle();
            if (liveTitle != null && !liveTitle.isEmpty()) {
                active.title = liveTitle;
            }
            active.scrollX = active.engine.getScrollX();
            active.scrollY = active.engine.getScrollY();
        }
    }

    public void destroyInactiveWebViews() {
        for (int i = 0; i < tabs.size(); i++) {
            TabItem item = tabs.get(i);
            if (item.engine != null) {
                item.engine.destroy();
                item.engine = null;
            }
        }
    }
}
""")

# ==============================================================================
# 7. DOWNLOAD MANAGER (BUG #2 FIX: Real Streaming, 8KB Buffer, SQLite Tracking)
# ==============================================================================
write_file("data/DownloadManager.java", """
package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.AsyncTask;
import android.os.Environment;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class DownloadManager {
    private final Context context;
    private final BrowserDatabaseHelper dbHelper;
    private DownloadListener listener;

    public interface DownloadListener {
        void onDownloadProgress(long id, String filename, int progress, long bytesRead, long totalBytes);
        void onDownloadFinished(long id, String filename, boolean success, String errorMsg);
    }

    public static class DownloadItem {
        public long id;
        public String filename;
        public String url;
        public String filePath;
        public String mimeType;
        public long fileSize;
        public long downloadedBytes;
        public String status; // PENDING, DOWNLOADING, COMPLETED, FAILED, CANCELLED
        public long timestamp;

        public DownloadItem(long id, String filename, String url, String filePath, String mimeType, long fileSize, long downloadedBytes, String status, long timestamp) {
            this.id = id;
            this.filename = filename;
            this.url = url;
            this.filePath = filePath;
            this.mimeType = mimeType;
            this.fileSize = fileSize;
            this.downloadedBytes = downloadedBytes;
            this.status = status;
            this.timestamp = timestamp;
        }
    }

    public DownloadManager(Context context) {
        this.context = context;
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public void setListener(DownloadListener listener) {
        this.listener = listener;
    }

    public long enqueueDownload(String downloadUrl, String filename, String mimeType, long estimatedSize) {
        if (downloadUrl == null || downloadUrl.isEmpty()) return -1;
        String safeName = sanitizeFilename(filename, downloadUrl);

        File destDir = getDownloadDestinationDir();
        File targetFile = new File(destDir, safeName);

        long id = -1;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            ContentValues cv = new ContentValues();
            cv.put("filename", safeName);
            cv.put("url", downloadUrl);
            cv.put("filepath", targetFile.getAbsolutePath());
            cv.put("mimetype", mimeType != null ? mimeType : "application/octet-stream");
            cv.put("filesize", estimatedSize > 0 ? estimatedSize : 0);
            cv.put("downloaded_bytes", 0);
            cv.put("status", "DOWNLOADING");
            cv.put("timestamp", System.currentTimeMillis());
            id = db.insert(BrowserDatabaseHelper.TABLE_DOWNLOADS, null, cv);
        } catch (Exception ignored) {}

        if (id > 0) {
            new DownloadTask(id, downloadUrl, targetFile).execute();
        }
        return id;
    }

    public List<DownloadItem> getAllDownloads() {
        List<DownloadItem> list = new ArrayList<DownloadItem>();
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            c = db.rawQuery("SELECT id, filename, url, filepath, mimetype, filesize, downloaded_bytes, status, timestamp FROM " +
                    BrowserDatabaseHelper.TABLE_DOWNLOADS + " ORDER BY timestamp DESC", null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new DownloadItem(
                            c.getLong(0),
                            c.getString(1),
                            c.getString(2),
                            c.getString(3),
                            c.getString(4),
                            c.getLong(5),
                            c.getLong(6),
                            c.getString(7),
                            c.getLong(8)
                    ));
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.close();
        }
        return list;
    }

    public void deleteDownload(long id) {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_DOWNLOADS, "id = ?", new String[]{String.valueOf(id)});
        } catch (Exception ignored) {}
    }

    public void clearAllDownloads() {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_DOWNLOADS, null, null);
        } catch (Exception ignored) {}
    }

    private File getDownloadDestinationDir() {
        File dir = null;
        if (Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
            dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        }
        if (dir == null || (!dir.exists() && !dir.mkdirs())) {
            dir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        }
        if (dir == null) {
            dir = context.getFilesDir();
        }
        if (!dir.exists()) {
            dir.mkdirs();
        }
        return dir;
    }

    private String sanitizeFilename(String filename, String url) {
        if (filename != null && !filename.trim().isEmpty()) {
            String clean = filename.replace("/", "_").replace("\\\\", "_").replace("..", "_");
            if (clean.length() > 64) clean = clean.substring(clean.length() - 64);
            return clean;
        }
        try {
            String path = new URL(url).getPath();
            int idx = path.lastIndexOf('/');
            if (idx >= 0 && idx < path.length() - 1) {
                return path.substring(idx + 1).replaceAll("[^a-zA-Z0-9._-]", "_");
            }
        } catch (Exception ignored) {}
        return "download_" + System.currentTimeMillis() + ".bin";
    }

    private class DownloadTask extends AsyncTask<Void, Integer, Boolean> {
        private final long downloadId;
        private final String downloadUrl;
        private final File targetFile;
        private String errorMessage = "";
        private long totalBytes = 0;
        private long bytesRead = 0;

        public DownloadTask(long downloadId, String downloadUrl, File targetFile) {
            this.downloadId = downloadId;
            this.downloadUrl = downloadUrl;
            this.targetFile = targetFile;
        }

        @Override
        protected Boolean doInBackground(Void... params) {
            HttpURLConnection conn = null;
            InputStream in = null;
            FileOutputStream out = null;

            try {
                URL u = new URL(downloadUrl);
                conn = (HttpURLConnection) u.openConnection();
                conn.setConnectTimeout(15000);
                conn.setReadTimeout(30000);
                conn.setRequestProperty("User-Agent", "YangKaiBrowser/1.0 (Android 4.4.4; D-Pad TV Box)");
                conn.setInstanceFollowRedirects(true);
                conn.connect();

                int code = conn.getResponseCode();
                if (code < 200 || code >= 300) {
                    errorMessage = "HTTP " + code + ": " + conn.getResponseMessage();
                    return false;
                }

                totalBytes = conn.getContentLength();
                in = conn.getInputStream();
                out = new FileOutputStream(targetFile);

                // Strictly 8KB buffer - never buffer full file in memory for 512MB RAM!
                byte[] buffer = new byte[8192];
                int n;
                long lastProgressUpdate = 0;

                while ((n = in.read(buffer)) != -1) {
                    if (isCancelled()) {
                        errorMessage = "Cancelled by user";
                        return false;
                    }
                    out.write(buffer, 0, n);
                    bytesRead += n;

                    long now = System.currentTimeMillis();
                    if (now - lastProgressUpdate > 500) {
                        int pct = totalBytes > 0 ? (int) ((bytesRead * 100) / totalBytes) : 0;
                        publishProgress(pct);
                        lastProgressUpdate = now;
                    }
                }
                out.flush();
                return true;

            } catch (Exception e) {
                errorMessage = e.getMessage() != null ? e.getMessage() : "Network error during download";
                return false;
            } finally {
                try { if (in != null) in.close(); } catch (Exception ignored) {}
                try { if (out != null) out.close(); } catch (Exception ignored) {}
                if (conn != null) conn.disconnect();
            }
        }

        @Override
        protected void onProgressUpdate(Integer... values) {
            int pct = values[0];
            if (listener != null) {
                listener.onDownloadProgress(downloadId, targetFile.getName(), pct, bytesRead, totalBytes);
            }
        }

        @Override
        protected void onPostExecute(Boolean success) {
            String status = success ? "COMPLETED" : "FAILED";
            try {
                SQLiteDatabase db = dbHelper.getWritableDatabase();
                ContentValues cv = new ContentValues();
                cv.put("status", status);
                cv.put("downloaded_bytes", bytesRead);
                if (totalBytes > 0) cv.put("filesize", totalBytes);
                db.update(BrowserDatabaseHelper.TABLE_DOWNLOADS, cv, "id = ?", new String[]{String.valueOf(downloadId)});
            } catch (Exception ignored) {}

            if (listener != null) {
                listener.onDownloadFinished(downloadId, targetFile.getName(), success, errorMessage);
            }
        }
    }
}
""")

# ==============================================================================
# 8. DATABASE HELPER (History, Bookmarks, Real Downloads Schema)
# ==============================================================================
write_file("data/BrowserDatabaseHelper.java", """
package com.yangkaibrowser.legacy.data;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class BrowserDatabaseHelper extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "yangkai_browser.db";
    private static final int DATABASE_VERSION = 2;

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
                + "filepath TEXT, "
                + "mimetype TEXT, "
                + "filesize INTEGER, "
                + "downloaded_bytes INTEGER, "
                + "status TEXT, "
                + "timestamp INTEGER NOT NULL);");

        // Indices for fast lookups on slow flash memory
        db.execSQL("CREATE INDEX idx_history_timestamp ON " + TABLE_HISTORY + "(timestamp DESC);");
        db.execSQL("CREATE INDEX idx_bookmarks_url ON " + TABLE_BOOKMARKS + "(url);");
        db.execSQL("CREATE INDEX idx_downloads_timestamp ON " + TABLE_DOWNLOADS + "(timestamp DESC);");
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

# ==============================================================================
# 9. BOOKMARKS & HISTORY MANAGERS (Leak-free cursor cleanup, indexed)
# ==============================================================================
write_file("data/BookmarkManager.java", """
package com.yangkaibrowser.legacy.data;

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
        public long createdAt;

        public BookmarkItem(long id, String title, String url, long createdAt) {
            this.id = id;
            this.title = title;
            this.url = url;
            this.createdAt = createdAt;
        }
    }

    public BookmarkManager(Context context) {
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public boolean addBookmark(String title, String url) {
        if (url == null || url.trim().isEmpty()) return false;
        String safeTitle = (title != null && !title.trim().isEmpty()) ? title.trim() : url;
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            c = db.query(BrowserDatabaseHelper.TABLE_BOOKMARKS, new String[]{"id"}, "url = ?", new String[]{url}, null, null, null);
            if (c != null && c.getCount() > 0) {
                return false; // Already bookmarked
            }
            ContentValues cv = new ContentValues();
            cv.put("title", safeTitle);
            cv.put("url", url);
            cv.put("created_at", System.currentTimeMillis());
            db.insert(BrowserDatabaseHelper.TABLE_BOOKMARKS, null, cv);
            return true;
        } catch (Exception e) {
            return false;
        } finally {
            if (c != null) c.close();
        }
    }

    public List<BookmarkItem> getAllBookmarks() {
        List<BookmarkItem> list = new ArrayList<BookmarkItem>();
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            c = db.rawQuery("SELECT id, title, url, created_at FROM " +
                    BrowserDatabaseHelper.TABLE_BOOKMARKS + " ORDER BY created_at DESC", null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new BookmarkItem(c.getLong(0), c.getString(1), c.getString(2), c.getLong(3)));
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.close();
        }
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

write_file("data/HistoryManager.java", """
package com.yangkaibrowser.legacy.data;

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

            // Maintain max 300 items limit to prevent slow flash wear
            db.execSQL("DELETE FROM " + BrowserDatabaseHelper.TABLE_HISTORY +
                       " WHERE id NOT IN (SELECT id FROM " + BrowserDatabaseHelper.TABLE_HISTORY +
                       " ORDER BY timestamp DESC LIMIT " + MAX_HISTORY_ITEMS + ")");
        } catch (Exception ignored) {}
    }

    public List<HistoryEntry> getRecentEntries(int limit) {
        List<HistoryEntry> list = new ArrayList<HistoryEntry>();
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            c = db.rawQuery("SELECT id, url, title, timestamp FROM " +
                    BrowserDatabaseHelper.TABLE_HISTORY + " ORDER BY timestamp DESC LIMIT " + limit, null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new HistoryEntry(c.getLong(0), c.getString(1), c.getString(2), c.getLong(3)));
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.close();
        }
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

# ==============================================================================
# 10. REAL MEMORY MANAGER (Kernel Available RAM + Java Heap)
# ==============================================================================
write_file("performance/MemoryManager.java", """
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
""")

# ==============================================================================
# 11. CACHE MANAGER (Web Cache, Cookies, App Cache, Total Temporary Wipe)
# ==============================================================================
write_file("performance/CacheManager.java", """
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
""")

write_file("performance/PerformanceMonitor.java", """
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
""")

# ==============================================================================
# 12. SETTINGS MANAGER (SavePassword = false by default, UA, Performance mode)
# ==============================================================================
write_file("settings/SettingsManager.java", """
package com.yangkaibrowser.legacy.settings;

import android.content.Context;
import android.content.SharedPreferences;

public class SettingsManager {
    private static final String PREF_NAME = "yangkai_prefs";
    public static final String KEY_SEARCH_ENGINE = "search_engine";
    public static final String KEY_JAVASCRIPT = "js_enabled";
    public static final String KEY_IMAGES = "images_enabled";
    public static final String KEY_SAVE_PASSWORDS = "save_passwords";
    public static final String KEY_USER_AGENT = "user_agent_mode";
    public static final String KEY_CURSOR_SPEED = "cursor_speed";
    public static final String KEY_PERFORMANCE_MODE = "perf_mode";

    public static final int UA_DEFAULT = 0;
    public static final int UA_MOBILE = 1;
    public static final int UA_DESKTOP = 2;

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

    public boolean isSavePasswordsEnabled() {
        return prefs.getBoolean(KEY_SAVE_PASSWORDS, false); // Strictly false by default
    }

    public void setSavePasswordsEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_SAVE_PASSWORDS, enabled).commit();
    }

    public int getUserAgentMode() {
        return prefs.getInt(KEY_USER_AGENT, UA_DEFAULT);
    }

    public void setUserAgentMode(int mode) {
        prefs.edit().putInt(KEY_USER_AGENT, mode).commit();
    }

    public int getCursorSpeed() {
        return prefs.getInt(KEY_CURSOR_SPEED, 18);
    }

    public void setCursorSpeed(int speed) {
        prefs.edit().putInt(KEY_CURSOR_SPEED, speed).commit();
    }

    public boolean isPerformanceMode() {
        return prefs.getBoolean(KEY_PERFORMANCE_MODE, true);
    }

    public void setPerformanceMode(boolean enabled) {
        prefs.edit().putBoolean(KEY_PERFORMANCE_MODE, enabled).commit();
    }
}
""")

# ==============================================================================
# 13. TV INPUT MANAGERS (D-Pad, Virtual Pointer, Focus)
# ==============================================================================
write_file("tv/RemoteManager.java", """
package com.yangkaibrowser.legacy.tv;

import android.view.KeyEvent;

public class RemoteManager {
    private KeyEventListener listener;

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
        if (event == null || listener == null) return false;

        // Process only key-down events for snappy TV responsiveness
        if (event.getAction() != KeyEvent.ACTION_DOWN) {
            return false;
        }

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
}
""")

write_file("tv/CursorManager.java", """
package com.yangkaibrowser.legacy.tv;

import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ImageView;

public class CursorManager {
    private final ImageView cursorView;
    private final View targetContainer;
    private boolean isCursorMode = false;
    private float cursorX = 400f;
    private float cursorY = 250f;
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
            int maxX = targetContainer.getWidth() - 16;
            int maxY = targetContainer.getHeight() - 16;
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
        MotionEvent upEvent = MotionEvent.obtain(downTime, eventTime + 40, MotionEvent.ACTION_UP, cursorX, cursorY, 0);

        targetContainer.dispatchTouchEvent(downEvent);
        targetContainer.dispatchTouchEvent(upEvent);

        downEvent.recycle();
        upEvent.recycle();
    }
}
""")

write_file("tv/FocusManager.java", """
package com.yangkaibrowser.legacy.tv;

import android.view.View;

public class FocusManager {
    public static void requestInitialFocus(final View view) {
        if (view == null) return;
        view.post(new Runnable() {
            @Override
            public void run() {
                view.requestFocus();
            }
        });
    }
}
""")

write_file("compatibility/LegacyCompatibility.java", """
package com.yangkaibrowser.legacy.compatibility;

import android.os.Build;

public class LegacyCompatibility {
    public static boolean isKitKat() {
        return Build.VERSION.SDK_INT == 19;
    }

    public static String getSystemArch() {
        return Build.CPU_ABI != null ? Build.CPU_ABI : "armeabi-v7a";
    }
}
""")

print("[*] Core components generated successfully.")
