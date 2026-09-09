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
