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
