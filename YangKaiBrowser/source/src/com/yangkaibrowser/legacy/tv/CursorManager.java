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
