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
