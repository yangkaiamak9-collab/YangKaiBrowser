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
        boolean isCurrentUrlTrustedLocalAsset();
    }

    public YangKaiJsBridge(Activity activity, BridgeListener listener) {
        this.activity = activity;
        this.listener = listener;
    }

    private boolean isAuthorizedCaller() {
        return activity != null && listener != null && listener.isCurrentUrlTrustedLocalAsset();
    }

    @JavascriptInterface
    public void openBookmarks() {
        if (!isAuthorizedCaller()) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenBookmarks();
            }
        });
    }

    @JavascriptInterface
    public void openHistory() {
        if (!isAuthorizedCaller()) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenHistory();
            }
        });
    }

    @JavascriptInterface
    public void openDownloads() {
        if (!isAuthorizedCaller()) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenDownloads();
            }
        });
    }

    @JavascriptInterface
    public void openSettings() {
        if (!isAuthorizedCaller()) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenSettings();
            }
        });
    }

    @JavascriptInterface
    public void openDiagnostics() {
        if (!isAuthorizedCaller()) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onOpenDiagnostics();
            }
        });
    }

    @JavascriptInterface
    public void clearCache() {
        if (!isAuthorizedCaller()) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                listener.onClearCacheRequested();
            }
        });
    }

    @JavascriptInterface
    public String getDiagnostics() {
        if (!isAuthorizedCaller()) return "{}";
        return listener.getDiagnosticsDataJson();
    }
}
