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
    private boolean isBridgeAttached = false;

    @SuppressLint("SetJavaScriptEnabled")
    public LegacyWebViewEngine(Context context, YangKaiJsBridge.BridgeListener bridgeListener) {
        this.webView = new WebView(context);
        initSettings();
        initClients();
        initDownloadListener();
        if (context instanceof Activity && bridgeListener != null) {
            jsBridge = new YangKaiJsBridge((Activity) context, bridgeListener);
            // Bridge is intentionally not attached globally; attached only on file:///android_asset/
            isBridgeAttached = false;
        }
    }

    private void updateJsBridgeSecurity(String url) {
        if (webView == null) return;
        boolean isTrustedLocal = url != null && url.startsWith("file:///android_asset/");
        if (isTrustedLocal) {
            if (!isBridgeAttached && jsBridge != null) {
                webView.addJavascriptInterface(jsBridge, "yangkai");
                isBridgeAttached = true;
            }
        } else {
            if (isBridgeAttached) {
                webView.removeJavascriptInterface("yangkai");
                isBridgeAttached = false;
            }
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
                if (url == null) return true;
                if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("file:///android_asset/")) {
                    updateJsBridgeSecurity(url);
                    view.loadUrl(url);
                    return true;
                }
                // Block all non-permitted schemes: intent:, javascript:, data:, ftp:, and unauthorized file:///
                return true;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                updateJsBridgeSecurity(url);
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
            String clean = url.trim();
            updateJsBridgeSecurity(clean);
            webView.loadUrl(clean);
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
