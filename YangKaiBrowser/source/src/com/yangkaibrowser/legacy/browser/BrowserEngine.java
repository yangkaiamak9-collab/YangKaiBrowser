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
