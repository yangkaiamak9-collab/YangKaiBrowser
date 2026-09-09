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
