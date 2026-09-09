package com.yangkaibrowser.legacy;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.StatFs;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.webkit.MimeTypeMap;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.yangkaibrowser.legacy.browser.BrowserController;
import com.yangkaibrowser.legacy.browser.BrowserEngine;
import com.yangkaibrowser.legacy.browser.NavigationManager;
import com.yangkaibrowser.legacy.browser.YangKaiJsBridge;
import com.yangkaibrowser.legacy.data.BookmarkManager;
import com.yangkaibrowser.legacy.data.DownloadManager;
import com.yangkaibrowser.legacy.data.HistoryManager;
import com.yangkaibrowser.legacy.performance.CacheManager;
import com.yangkaibrowser.legacy.performance.MemoryManager;
import com.yangkaibrowser.legacy.settings.SettingsManager;
import com.yangkaibrowser.legacy.tabs.TabManager;
import com.yangkaibrowser.legacy.tv.CursorManager;
import com.yangkaibrowser.legacy.tv.RemoteManager;

import java.io.File;
import java.util.List;

public class MainActivity extends Activity implements
        RemoteManager.KeyEventListener,
        BrowserEngine.EngineCallback,
        YangKaiJsBridge.BridgeListener,
        DownloadManager.DownloadListener {

    private TabManager tabManager;
    private BrowserController browserController;
    private SettingsManager settingsManager;
    private BookmarkManager bookmarkManager;
    private HistoryManager historyManager;
    private DownloadManager downloadManager;
    private RemoteManager remoteManager;
    private CursorManager cursorManager;

    // UI Widgets
    private EditText urlInput;
    private Button btnGo;
    private Button btnBack;
    private Button btnForward;
    private Button btnReload;
    private Button btnHome;
    private Button btnTabs;
    private Button btnDownloads;
    private Button btnCursorToggle;
    private Button btnMenu;
    private ProgressBar progressBar;
    private FrameLayout webviewContainer;
    private ImageView virtualCursor;
    private TextView tvBrand;
    private TextView tvMemStatus;
    private TextView tvModeStatus;

    private AlertDialog currentDialog;
    private boolean isCurrentlyLoading = false;
    private final Handler memUpdateHandler = new Handler();
    private Runnable memUpdateRunnable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initManagers();
        initViews();
        setupListeners();
        startMemoryMonitoring();

        // Load initial tab
        activateTab(0);
    }

    private void initManagers() {
        this.settingsManager = new SettingsManager(this);
        this.bookmarkManager = new BookmarkManager(this);
        this.historyManager = new HistoryManager(this);
        this.downloadManager = new DownloadManager(this);
        this.downloadManager.setListener(this);
        this.tabManager = new TabManager(this, this);
        this.remoteManager = new RemoteManager();
        this.remoteManager.setListener(this);
    }

    private void initViews() {
        this.urlInput = (EditText) findViewById(R.id.url_input);
        this.btnGo = (Button) findViewById(R.id.btn_go);
        this.btnBack = (Button) findViewById(R.id.btn_back);
        this.btnForward = (Button) findViewById(R.id.btn_forward);
        this.btnReload = (Button) findViewById(R.id.btn_reload);
        this.btnHome = (Button) findViewById(R.id.btn_home);
        this.btnTabs = (Button) findViewById(R.id.btn_tabs);
        this.btnDownloads = (Button) findViewById(R.id.btn_downloads);
        this.btnCursorToggle = (Button) findViewById(R.id.btn_cursor_toggle);
        this.btnMenu = (Button) findViewById(R.id.btn_menu);
        this.progressBar = (ProgressBar) findViewById(R.id.progress_bar);
        this.webviewContainer = (FrameLayout) findViewById(R.id.webview_container);
        this.virtualCursor = (ImageView) findViewById(R.id.virtual_cursor);
        this.tvBrand = (TextView) findViewById(R.id.tv_brand);
        this.tvMemStatus = (TextView) findViewById(R.id.tv_mem_status);
        this.tvModeStatus = (TextView) findViewById(R.id.tv_mode_status);

        this.browserController = new BrowserController(this, webviewContainer);
        this.cursorManager = new CursorManager(virtualCursor, webviewContainer);
        this.cursorManager.setSpeed(settingsManager.getCursorSpeed());
    }

    private void setupListeners() {
        btnGo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                performNavigation();
            }
        });

        urlInput.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                if (actionId == EditorInfo.IME_ACTION_GO || actionId == EditorInfo.IME_ACTION_DONE ||
                    (event != null && event.getKeyCode() == KeyEvent.KEYCODE_ENTER)) {
                    performNavigation();
                    return true;
                }
                return false;
            }
        });

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
                if (engine != null) {
                    if (isCurrentlyLoading) {
                        engine.stopLoading();
                    } else {
                        engine.reload();
                    }
                }
            }
        });

        btnHome.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loadUrl(NavigationManager.HOMEPAGE_URL);
            }
        });

        btnTabs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showTabsDialog();
            }
        });

        if (btnDownloads != null) {
            btnDownloads.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showDownloadsDialog();
                }
            });
        }

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

    private void performNavigation() {
        String input = urlInput.getText().toString();
        String resolved = NavigationManager.resolveInput(input, settingsManager.getSearchEngine());
        loadUrl(resolved);
    }

    public void loadUrl(String url) {
        BrowserEngine engine = browserController.getActiveEngine();
        if (engine != null) {
            engine.loadUrl(url);
            urlInput.setText(url);
        }
    }

    private void activateTab(int index) {
        BrowserEngine engine = tabManager.selectTab(index, this);
        if (engine != null) {
            // Apply current settings
            engine.setJavaScriptEnabled(settingsManager.isJavaScriptEnabled());
            engine.setImagesEnabled(settingsManager.isImagesEnabled());
            applyUserAgent(engine);

            browserController.attachEngine(engine);
            updateTabsButtonText();
            updateMemoryStatus();
        }
    }

    private void applyUserAgent(BrowserEngine engine) {
        int mode = settingsManager.getUserAgentMode();
        if (mode == SettingsManager.UA_MOBILE) {
            engine.setUserAgent("Mozilla/5.0 (Linux; Android 4.4.4; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0");
        } else if (mode == SettingsManager.UA_DESKTOP) {
            engine.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36");
        }
    }

    private void updateTabsButtonText() {
        int count = tabManager.getTabs().size();
        int active = tabManager.getActiveIndex() + 1;
        btnTabs.setText("Tab " + active + "/" + count);
    }

    private void toggleCursorMode() {
        boolean nextMode = !cursorManager.isCursorMode();
        cursorManager.setCursorMode(nextMode);
        btnCursorToggle.setText(nextMode ? "🎯 Pointer" : "🎮 D-Pad");
        tvModeStatus.setText(nextMode ? "MODE: VIRTUAL CURSOR" : "MODE: DPAD FOCUS");
        tvModeStatus.setTextColor(nextMode ? 0xFFFFD54F : 0xFFE5A93C);
    }

    private void navigateBack() {
        BrowserEngine engine = browserController.getActiveEngine();
        if (engine != null && engine.canGoBack()) {
            engine.goBack();
        } else {
            TabManager.TabItem active = tabManager.getActiveTab();
            if (active != null && active.url != null && !active.url.equals(NavigationManager.HOMEPAGE_URL)) {
                loadUrl(NavigationManager.HOMEPAGE_URL);
            } else {
                showExitDialog();
            }
        }
    }

    // =========================================================================
    // D-PAD & TV REMOTE DISPATCH
    // =========================================================================
    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        // If an alert dialog is visible, let Android handle dialog key events (e.g. dismiss on BACK)
        if (currentDialog != null && currentDialog.isShowing()) {
            return super.dispatchKeyEvent(event);
        }

        if (remoteManager.dispatchKeyEvent(event)) {
            return true;
        }
        return super.dispatchKeyEvent(event);
    }

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

    // =========================================================================
    // BROWSER ENGINE CALLBACKS
    // =========================================================================
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
        if (active != null) {
            active.title = title;
        }
        if (title != null && !title.isEmpty() && !title.startsWith("file:///")) {
            historyManager.addEntry(tabManager.getActiveTab().url, title);
        }
    }

    @Override
    public void onUrlChanged(String url) {
        if (url != null && !url.startsWith("file:///android_asset/")) {
            urlInput.setText(url);
        }
        TabManager.TabItem active = tabManager.getActiveTab();
        if (active != null) {
            active.url = url;
        }
        updateMemoryStatus();
    }

    @Override
    public void onLoadingStateChanged(boolean isLoading) {
        this.isCurrentlyLoading = isLoading;
        progressBar.setVisibility(isLoading ? View.VISIBLE : View.GONE);
        if (btnReload != null) {
            btnReload.setText(isLoading ? getString(R.string.btn_stop) : getString(R.string.btn_reload));
        }
        if (!isLoading) {
            updateMemoryStatus();
        }
    }

    @Override
    public void onError(int errorCode, String description, String failingUrl) {
        progressBar.setVisibility(View.GONE);
        Toast.makeText(this, "Load Notice: " + description, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onSslError(final String failingUrl, final String sslReason) {
        progressBar.setVisibility(View.GONE);
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                showSslWarningDialog(failingUrl, sslReason);
            }
        });
    }

    @Override
    public void onDownloadRequested(final String url, String userAgent, String contentDisposition, final String mimeType, final long contentLength) {
        final String guessFilename = guessFilename(url, contentDisposition);
        final String sizeStr = contentLength > 0 ? (contentLength / 1024 + " KB") : "Unknown size";

        currentDialog = new AlertDialog.Builder(this)
                .setTitle("📥 Download Request")
                .setMessage("File: " + guessFilename + "\\nSize: " + sizeStr + "\\n\\nSave to device Downloads folder?")
                .setPositiveButton("Download", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        downloadManager.enqueueDownload(url, guessFilename, mimeType, contentLength);
                        Toast.makeText(MainActivity.this, "Download started: " + guessFilename, Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private String guessFilename(String url, String contentDisposition) {
        if (contentDisposition != null) {
            String prefix = "filename=";
            int idx = contentDisposition.indexOf(prefix);
            if (idx >= 0) {
                String name = contentDisposition.substring(idx + prefix.length()).trim().replace("\"", "");
                if (!name.isEmpty()) return name;
            }
        }
        try {
            Uri uri = Uri.parse(url);
            String lastPath = uri.getLastPathSegment();
            if (lastPath != null && !lastPath.isEmpty()) {
                return lastPath;
            }
        } catch (Exception ignored) {}
        return "file_" + System.currentTimeMillis() + ".bin";
    }

    // =========================================================================
    // DOWNLOAD MANAGER CALLBACKS
    // =========================================================================
    @Override
    public void onDownloadProgress(long id, String filename, int progress, long bytesRead, long totalBytes) {
        // Silent background tracking
    }

    @Override
    public void onDownloadFinished(long id, final String filename, final boolean success, final String errorMsg) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (success) {
                    Toast.makeText(MainActivity.this, "✓ Download Complete: " + filename, Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(MainActivity.this, "Download Failed (" + filename + "): " + errorMsg, Toast.LENGTH_LONG).show();
                }
            }
        });
    }

    // =========================================================================
    // JAVASCRIPT BRIDGE LISTENER (BUG #1 FIX)
    // =========================================================================
    @Override
    public boolean isCurrentUrlTrustedLocalAsset() {
        if (browserController == null) return false;
        BrowserEngine engine = browserController.getActiveEngine();
        if (engine == null) return false;
        String currentUrl = engine.getUrl();
        return currentUrl != null && currentUrl.startsWith("file:///android_asset/");
    }

    @Override
    public void onOpenBookmarks() {
        showBookmarksDialog();
    }

    @Override
    public void onOpenHistory() {
        showHistoryDialog();
    }

    @Override
    public void onOpenDownloads() {
        showDownloadsDialog();
    }

    @Override
    public void onOpenSettings() {
        showSettingsDialog();
    }

    @Override
    public void onOpenDiagnostics() {
        loadUrl(NavigationManager.DIAGNOSTICS_URL);
    }

    @Override
    public void onClearCacheRequested() {
        clearAllCacheWithFeedback();
    }

    @Override
    public String getDiagnosticsDataJson() {
        MemoryManager.MemorySnapshot snap = MemoryManager.getSnapshot(this);
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo ni = cm != null ? cm.getActiveNetworkInfo() : null;
        String netStatus = (ni != null && ni.isConnected()) ? (ni.getTypeName() + " (" + ni.getSubtypeName() + ")") : "Disconnected";

        long freeStorageMB = 0;
        try {
            StatFs stat = new StatFs(Environment.getDataDirectory().getPath());
            freeStorageMB = ((long) stat.getAvailableBlocks() * (long) stat.getBlockSize()) / (1024 * 1024);
        } catch (Exception ignored) {}

        StringBuilder sb = new StringBuilder();
        sb.append("{");
        sb.append("\"osVersion\":\"").append(Build.VERSION.RELEASE).append("\",");
        sb.append("\"apiLevel\":").append(Build.VERSION.SDK_INT).append(",");
        sb.append("\"deviceModel\":\"").append(Build.MODEL).append("\",");
        sb.append("\"hardware\":\"").append(Build.HARDWARE).append("\",");
        sb.append("\"cpuAbi\":\"").append(Build.CPU_ABI).append("\",");
        sb.append("\"totalRamMB\":").append(snap.totalMemMB).append(",");
        sb.append("\"availRamMB\":").append(snap.availMemMB).append(",");
        sb.append("\"isLowMem\":").append(snap.isLowMemory).append(",");
        sb.append("\"heapUsedMB\":").append(snap.usedHeapMB).append(",");
        sb.append("\"heapMaxMB\":").append(snap.maxHeapMB).append(",");
        sb.append("\"internalFreeMB\":").append(freeStorageMB).append(",");
        sb.append("\"activeTabs\":").append(tabManager.getTabs().size()).append(",");
        sb.append("\"liveWebviews\":").append(TabManager.MAX_LIVE_WEBVIEWS).append(",");
        sb.append("\"networkStatus\":\"").append(netStatus).append("\"");
        sb.append("}");
        return sb.toString();
    }

    // =========================================================================
    // NATIVE TV DIALOGS
    // =========================================================================
    private void showMenuDialog() {
        final String[] menuItems = new String[]{
                "➕ New Tab",
                "📑 Tab Manager (" + tabManager.getTabs().size() + "/3)",
                "🏠 Home Page",
                "⟳ Reload Page",
                "⭐ Add Bookmark",
                "📖 Bookmarks",
                "🕒 Browsing History",
                "📥 Downloads Manager",
                cursorManager.isCursorMode() ? "🎮 Switch to D-Pad Mode" : "🎯 Switch to Pointer Mode",
                "🧹 Free RAM & Clear Cache",
                "⚙️ Browser Settings",
                "🩺 Hardware Diagnostics",
                "ℹ️ About Yang Kai Browser",
                "🚪 Exit Browser"
        };

        currentDialog = new AlertDialog.Builder(this)
                .setTitle("🐉 Yang Kai TV Menu")
                .setItems(menuItems, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which) {
                            case 0: // New tab
                                if (tabManager.addTab(NavigationManager.HOMEPAGE_URL)) {
                                    activateTab(tabManager.getTabs().size() - 1);
                                    Toast.makeText(MainActivity.this, "Opened Tab " + tabManager.getTabs().size(), Toast.LENGTH_SHORT).show();
                                } else {
                                    Toast.makeText(MainActivity.this, "Tab limit reached (Max 3 for 512MB RAM)", Toast.LENGTH_SHORT).show();
                                }
                                break;
                            case 1: // Tab manager
                                showTabsDialog();
                                break;
                            case 2: // Home
                                loadUrl(NavigationManager.HOMEPAGE_URL);
                                break;
                            case 3: // Reload
                                if (browserController.getActiveEngine() != null) {
                                    browserController.getActiveEngine().reload();
                                }
                                break;
                            case 4: // Add bookmark
                                addCurrentBookmark();
                                break;
                            case 5: // Bookmarks
                                showBookmarksDialog();
                                break;
                            case 6: // History
                                showHistoryDialog();
                                break;
                            case 7: // Downloads
                                showDownloadsDialog();
                                break;
                            case 8: // Toggle pointer
                                toggleCursorMode();
                                break;
                            case 9: // Clear cache
                                clearAllCacheWithFeedback();
                                break;
                            case 10: // Settings
                                showSettingsDialog();
                                break;
                            case 11: // Diagnostics
                                loadUrl(NavigationManager.DIAGNOSTICS_URL);
                                break;
                            case 12: // About
                                showAboutDialog();
                                break;
                            case 13: // Exit
                                finish();
                                break;
                        }
                    }
                })
                .show();
    }

    private void showTabsDialog() {
        final List<TabManager.TabItem> tabs = tabManager.getTabs();
        String[] titles = new String[tabs.size() + (tabs.size() < TabManager.MAX_TABS ? 1 : 0)];
        for (int i = 0; i < tabs.size(); i++) {
            TabManager.TabItem item = tabs.get(i);
            String title = item.title != null && !item.title.isEmpty() ? item.title : item.url;
            titles[i] = (i == tabManager.getActiveIndex() ? "● Tab " : "○ Tab ") + (i + 1) + ": " + title;
        }
        if (tabs.size() < TabManager.MAX_TABS) {
            titles[titles.length - 1] = "➕ Open New Tab";
        }

        currentDialog = new AlertDialog.Builder(this)
                .setTitle("📑 Tabs (" + tabs.size() + " / " + TabManager.MAX_TABS + ")")
                .setItems(titles, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        if (which < tabs.size()) {
                            activateTab(which);
                        } else {
                            if (tabManager.addTab(NavigationManager.HOMEPAGE_URL)) {
                                activateTab(tabManager.getTabs().size() - 1);
                            }
                        }
                    }
                })
                .setNeutralButton("Close Current Tab", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        if (tabs.size() > 1) {
                            tabManager.closeTab(tabManager.getActiveIndex());
                            activateTab(tabManager.getActiveIndex());
                        } else {
                            Toast.makeText(MainActivity.this, "Cannot close the only open tab", Toast.LENGTH_SHORT).show();
                        }
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showBookmarksDialog() {
        final List<BookmarkManager.BookmarkItem> bookmarks = bookmarkManager.getAllBookmarks();
        if (bookmarks.isEmpty()) {
            Toast.makeText(this, "No bookmarks saved yet.", Toast.LENGTH_SHORT).show();
            return;
        }
        final String[] items = new String[bookmarks.size()];
        for (int i = 0; i < bookmarks.size(); i++) {
            items[i] = bookmarks.get(i).title;
        }

        currentDialog = new AlertDialog.Builder(this)
                .setTitle("⭐ Saved Bookmarks")
                .setItems(items, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        loadUrl(bookmarks.get(which).url);
                    }
                })
                .setNegativeButton("Close", null)
                .show();
    }

    private void addCurrentBookmark() {
        TabManager.TabItem item = tabManager.getActiveTab();
        if (item != null && item.url != null && !item.url.startsWith("file:///")) {
            boolean added = bookmarkManager.addBookmark(item.title != null ? item.title : item.url, item.url);
            Toast.makeText(this, added ? "★ Bookmarked!" : "Already in bookmarks", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Cannot bookmark local page", Toast.LENGTH_SHORT).show();
        }
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

        currentDialog = new AlertDialog.Builder(this)
                .setTitle("🕒 Browsing History")
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
                        Toast.makeText(MainActivity.this, "History cleared!", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Close", null)
                .show();
    }

    private void showDownloadsDialog() {
        final List<DownloadManager.DownloadItem> downloads = downloadManager.getAllDownloads();
        if (downloads.isEmpty()) {
            Toast.makeText(this, "No download records found.", Toast.LENGTH_SHORT).show();
            return;
        }
        String[] items = new String[downloads.size()];
        for (int i = 0; i < downloads.size(); i++) {
            DownloadManager.DownloadItem d = downloads.get(i);
            String size = d.fileSize > 0 ? (d.fileSize / 1024 + " KB") : "";
            items[i] = "[" + d.status + "] " + d.filename + " " + size;
        }

        currentDialog = new AlertDialog.Builder(this)
                .setTitle("📥 Downloads")
                .setItems(items, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        showDownloadItemActions(downloads.get(which));
                    }
                })
                .setPositiveButton("Clear List", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        downloadManager.clearAllDownloads();
                        Toast.makeText(MainActivity.this, "Download records cleared", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("Close", null)
                .show();
    }

    private void showDownloadItemActions(final DownloadManager.DownloadItem item) {
        String[] actions = new String[]{"Open File", "Delete Record"};
        currentDialog = new AlertDialog.Builder(this)
                .setTitle(item.filename)
                .setItems(actions, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        if (which == 0) {
                            openDownloadedFile(item.filePath, item.mimeType);
                        } else if (which == 1) {
                            downloadManager.deleteDownload(item.id);
                            Toast.makeText(MainActivity.this, "Record removed", Toast.LENGTH_SHORT).show();
                        }
                    }
                })
                .show();
    }

    private void openDownloadedFile(String filePath, String mimeType) {
        if (filePath == null) return;
        File file = new File(filePath);
        if (!file.exists()) {
            Toast.makeText(this, "File does not exist on storage.", Toast.LENGTH_SHORT).show();
            return;
        }
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW);
            Uri uri = Uri.fromFile(file);
            String resolvedMime = mimeType;
            if (resolvedMime == null || resolvedMime.isEmpty() || resolvedMime.equals("application/octet-stream")) {
                String ext = MimeTypeMap.getFileExtensionFromUrl(uri.toString());
                if (ext != null) {
                    resolvedMime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext.toLowerCase());
                }
            }
            intent.setDataAndType(uri, resolvedMime != null ? resolvedMime : "*/*");
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "No app available to open this file.", Toast.LENGTH_SHORT).show();
        }
    }

    private void showSettingsDialog() {
        final String[] options = new String[]{
                "JavaScript: " + (settingsManager.isJavaScriptEnabled() ? "ENABLED" : "DISABLED"),
                "Images: " + (settingsManager.isImagesEnabled() ? "ENABLED" : "DISABLED"),
                "Search Engine: Bing (Default)",
                "User Agent Mode: " + getUserAgentName(settingsManager.getUserAgentMode()),
                "Cursor Speed: " + settingsManager.getCursorSpeed() + " px/step",
                "Performance Mode: " + (settingsManager.isPerformanceMode() ? "ACTIVE (512MB)" : "OFF"),
                "🧹 Clear Web Cache Only",
                "🍪 Clear Cookies Only",
                "⚠️ " + getString(R.string.dialog_title_clear_data)
        };

        currentDialog = new AlertDialog.Builder(this)
                .setTitle(getString(R.string.dialog_title_settings))
                .setItems(options, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which) {
                            case 0:
                                boolean nextJs = !settingsManager.isJavaScriptEnabled();
                                settingsManager.setJavaScriptEnabled(nextJs);
                                if (browserController.getActiveEngine() != null) {
                                    browserController.getActiveEngine().setJavaScriptEnabled(nextJs);
                                }
                                Toast.makeText(MainActivity.this, "JavaScript: " + (nextJs ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                                break;
                            case 1:
                                boolean nextImg = !settingsManager.isImagesEnabled();
                                settingsManager.setImagesEnabled(nextImg);
                                if (browserController.getActiveEngine() != null) {
                                    browserController.getActiveEngine().setImagesEnabled(nextImg);
                                }
                                Toast.makeText(MainActivity.this, "Images: " + (nextImg ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                                break;
                            case 2:
                                Toast.makeText(MainActivity.this, "Default Search: Bing (https://www.bing.com)", Toast.LENGTH_SHORT).show();
                                break;
                            case 3:
                                int nextMode = (settingsManager.getUserAgentMode() + 1) % 3;
                                settingsManager.setUserAgentMode(nextMode);
                                if (browserController.getActiveEngine() != null) {
                                    applyUserAgent(browserController.getActiveEngine());
                                }
                                Toast.makeText(MainActivity.this, "User-Agent: " + getUserAgentName(nextMode), Toast.LENGTH_SHORT).show();
                                break;
                            case 4:
                                int speed = settingsManager.getCursorSpeed() == 18 ? 26 : (settingsManager.getCursorSpeed() == 26 ? 12 : 18);
                                settingsManager.setCursorSpeed(speed);
                                cursorManager.setSpeed(speed);
                                Toast.makeText(MainActivity.this, "Cursor Speed: " + speed + " px", Toast.LENGTH_SHORT).show();
                                break;
                            case 5:
                                boolean nextPerf = !settingsManager.isPerformanceMode();
                                settingsManager.setPerformanceMode(nextPerf);
                                Toast.makeText(MainActivity.this, "Performance Mode: " + (nextPerf ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                                break;
                            case 6:
                                if (browserController.getActiveEngine() != null) {
                                    browserController.getActiveEngine().clearCache(true);
                                }
                                Toast.makeText(MainActivity.this, "Web Cache cleared", Toast.LENGTH_SHORT).show();
                                break;
                            case 7:
                                CacheManager.clearCookies(MainActivity.this);
                                Toast.makeText(MainActivity.this, "Cookies cleared", Toast.LENGTH_SHORT).show();
                                break;
                            case 8:
                                confirmClearBrowsingData();
                                break;
                        }
                    }
                })
                .setNegativeButton(getString(R.string.str_close), null)
                .show();
    }

    private void confirmClearBrowsingData() {
        currentDialog = new AlertDialog.Builder(this)
                .setTitle(R.string.dialog_title_clear_data)
                .setMessage("Are you sure you want to clear browsing history, web cache, and cookies?\\n\\nهل تريد حقاً مسح سجل التصفح وذاكرة التخزين المؤقت وملفات تعريف الارتباط؟")
                .setPositiveButton(getString(R.string.str_clear), new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        clearAllCacheWithFeedback();
                    }
                })
                .setNegativeButton(getString(R.string.str_cancel), null)
                .show();
    }

    private String getUserAgentName(int mode) {
        if (mode == SettingsManager.UA_MOBILE) return "Mobile";
        if (mode == SettingsManager.UA_DESKTOP) return "Desktop";
        return "Default (KitKat)";
    }

    private void clearAllCacheWithFeedback() {
        if (browserController.getActiveEngine() != null) {
            browserController.getActiveEngine().clearCache(true);
        }
        CacheManager.clearEverything(this, historyManager);
        updateMemoryStatus();
        Toast.makeText(this, "✓ All temporary cache & memory wiped!", Toast.LENGTH_SHORT).show();
    }

    private void showSslWarningDialog(final String url, String reason) {
        currentDialog = new AlertDialog.Builder(this)
                .setTitle("⚠️ HTTPS Certificate Warning")
                .setMessage("Unable to verify secure SSL connection to:\\n" + url +
                        "\\n\\nReason: " + reason +
                        "\\n\\nNotice: Android 4.4.4 root certificate authority stores lack modern Let's Encrypt certificates. The connection was cancelled to protect your security.")
                .setPositiveButton("Return Home", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        loadUrl(NavigationManager.HOMEPAGE_URL);
                    }
                })
                .setNegativeButton("Dismiss", null)
                .show();
    }

    private void showExitDialog() {
        currentDialog = new AlertDialog.Builder(this)
                .setTitle("🚪 Exit Yang Kai Browser")
                .setMessage("Are you sure you want to close the browser?")
                .setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        finish();
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showAboutDialog() {
        currentDialog = new AlertDialog.Builder(this)
                .setTitle("🐉 " + getString(R.string.app_name))
                .setMessage("Version: 1.0.1 (Hardened Build 2026)\\n" +
                        "Target: Android 4.4.4 KitKat (API 19)\\n" +
                        "Hardware Profile: ARM32 / Cortex-A7 / 512MB RAM TV\\n" +
                        "Architecture: Single Live WebView Engine\\n" +
                        "Package: com.yangkaibrowser.legacy\\n" +
                        "Default Search: Bing (UTF-8 Arabic Search)\\n\\n" +
                        "Features:\\n" +
                        "• Strict memory-safe Tab Management (1 Live WebView)\\n" +
                        "• Streaming 8KB chunk Download System (.tmp -> atomic rename)\\n" +
                        "• Dual-mode D-Pad & Virtual Cursor Navigation\\n" +
                        "• Secure Local JavaScript Bridge (file:///android_asset/ only)\\n" +
                        "• Real-time Physical RAM & Heap Diagnostics\\n" +
                        "• Zero Cloud Telemetry & Zero Analytics")
                .setPositiveButton("OK", null)
                .show();
    }

    // =========================================================================
    // MEMORY MONITORING & LIFECYCLE HOOKS
    // =========================================================================
    private void startMemoryMonitoring() {
        memUpdateRunnable = new Runnable() {
            @Override
            public void run() {
                updateMemoryStatus();
                memUpdateHandler.postDelayed(this, 3000); // 3-second cycle
            }
        };
        memUpdateHandler.postDelayed(memUpdateRunnable, 1000);
    }

    private void updateMemoryStatus() {
        if (isFinishing()) return;
        MemoryManager.MemorySnapshot snap = MemoryManager.getSnapshot(this);
        String summary = "RAM Free: " + snap.availMemMB + "MB • Heap: " + snap.usedHeapMB + "/" + snap.maxHeapMB + "MB";
        tvMemStatus.setText(summary);

        if (snap.state == MemoryManager.MemoryState.EMERGENCY || snap.state == MemoryManager.MemoryState.CRITICAL) {
            tvMemStatus.setTextColor(0xFFFF5252); // Red warning
            tabManager.destroyInactiveWebViews();
            if (snap.state == MemoryManager.MemoryState.EMERGENCY) {
                System.gc();
            }
        } else if (snap.state == MemoryManager.MemoryState.WARNING) {
            tvMemStatus.setTextColor(0xFFFFD54F); // Yellow warning
        } else {
            tvMemStatus.setTextColor(0xFFA0A0A8); // Normal gray
        }
    }

    @Override
    public void onTrimMemory(int level) {
        super.onTrimMemory(level);
        if (level >= TRIM_MEMORY_MODERATE) {
            tabManager.destroyInactiveWebViews();
            CacheManager.clearAppCache(this);
            System.gc();
        }
    }

    @Override
    public void onLowMemory() {
        super.onLowMemory();
        tabManager.destroyInactiveWebViews();
        CacheManager.clearAppCache(this);
        System.gc();
    }

    @Override
    protected void onDestroy() {
        memUpdateHandler.removeCallbacks(memUpdateRunnable);
        if (browserController != null) {
            browserController.detachActiveEngine();
        }
        if (tabManager != null) {
            tabManager.destroyInactiveWebViews();
        }
        super.onDestroy();
    }
}
