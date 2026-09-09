import React, { useState } from 'react';
import { FileCode, Copy, Check } from 'lucide-react';

interface FileEntry {
  path: string;
  name: string;
  category: 'core' | 'tv' | 'browser' | 'data' | 'manifest';
  code: string;
}

export const SourceCodeViewer: React.FC = () => {
  const [selectedPath, setSelectedPath] = useState<string>('AndroidManifest.xml');
  const [copied, setCopied] = useState<boolean>(false);

  const files: FileEntry[] = [
    {
      path: 'AndroidManifest.xml',
      name: 'AndroidManifest.xml',
      category: 'manifest',
      code: `<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.yangkaibrowser.legacy"
    android:versionCode="1"
    android:versionName="1.0.0">

    <uses-sdk
        android:minSdkVersion="19"
        android:targetSdkVersion="19" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

    <uses-feature
        android:name="android.hardware.touchscreen"
        android:required="false" />
    <uses-feature
        android:name="android.software.leanback"
        android:required="false" />

    <application
        android:allowBackup="true"
        android:hardwareAccelerated="true"
        android:icon="@drawable/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/YangKaiDarkTheme">

        <activity
            android:name="com.yangkaibrowser.legacy.MainActivity"
            android:configChanges="orientation|screenSize|keyboardHidden|keyboard"
            android:screenOrientation="landscape"
            android:launchMode="singleTask"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>`
    },
    {
      path: 'MainActivity.java',
      name: 'MainActivity.java',
      category: 'core',
      code: `package com.yangkaibrowser.legacy;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.widget.*;
import com.yangkaibrowser.legacy.browser.*;
import com.yangkaibrowser.legacy.tv.*;
import com.yangkaibrowser.legacy.tabs.*;
import com.yangkaibrowser.legacy.performance.*;

public class MainActivity extends Activity implements RemoteManager.KeyEventListener, BrowserEngine.EngineCallback {
    private BrowserController browserController;
    private TabManager tabManager;
    private RemoteManager remoteManager;
    private CursorManager cursorManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initManagers();
        initViews();
    }
}`
    },
    {
      path: 'browser/LegacyWebViewEngine.java',
      name: 'LegacyWebViewEngine.java',
      category: 'browser',
      code: `package com.yangkaibrowser.legacy.browser;

import android.content.Context;
import android.webkit.*;

public class LegacyWebViewEngine implements BrowserEngine {
    private final WebView webView;

    public LegacyWebViewEngine(Context context) {
        this.webView = new WebView(context);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setAppCacheEnabled(true);
        settings.setAppCacheMaxSize(8 * 1024 * 1024); // 8MB Dalvik budget
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
    }

    @Override
    public void loadUrl(String url) {
        webView.loadUrl(url);
    }
}`
    },
    {
      path: 'tv/CursorManager.java',
      name: 'CursorManager.java',
      category: 'tv',
      code: `package com.yangkaibrowser.legacy.tv;

import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ImageView;

public class CursorManager {
    private final ImageView cursorView;
    private final View targetContainer;
    private boolean isCursorMode = false;
    private float cursorX = 300f, cursorY = 200f;
    private int speedStep = 20;

    public void move(int dx, int dy) {
        if (!isCursorMode) return;
        cursorX += dx * speedStep;
        cursorY += dy * speedStep;
        updatePosition();
    }

    public void click() {
        long downTime = SystemClock.uptimeMillis();
        MotionEvent down = MotionEvent.obtain(downTime, downTime, MotionEvent.ACTION_DOWN, cursorX, cursorY, 0);
        MotionEvent up = MotionEvent.obtain(downTime, downTime + 50, MotionEvent.ACTION_UP, cursorX, cursorY, 0);
        targetContainer.dispatchTouchEvent(down);
        targetContainer.dispatchTouchEvent(up);
        down.recycle();
        up.recycle();
    }
}`
    },
    {
      path: 'performance/MemoryManager.java',
      name: 'MemoryManager.java',
      category: 'core',
      code: `package com.yangkaibrowser.legacy.performance;

public class MemoryManager {
    public enum MemoryState { NORMAL, WARNING, CRITICAL, EMERGENCY }

    public static MemoryState evaluateMemory() {
        Runtime rt = Runtime.getRuntime();
        long max = rt.maxMemory();
        long used = rt.totalMemory() - rt.freeMemory();
        double ratio = (double) used / (double) max;
        if (ratio > 0.88) return MemoryState.EMERGENCY;
        if (ratio > 0.78) return MemoryState.CRITICAL;
        if (ratio > 0.65) return MemoryState.WARNING;
        return MemoryState.NORMAL;
    }
}`
    }
  ];

  const currentFile = files.find(f => f.path === selectedPath) || files[0];

  const handleCopy = () => {
    navigator.clipboard.writeText(currentFile.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-5 text-left">
      {/* File List */}
      <div className="md:col-span-4 bg-[#14141A] rounded-2xl border border-[#242430] p-4">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
          Yang Kai Source Tree
        </h3>
        <div className="space-y-1 text-xs">
          {files.map(f => (
            <button
              key={f.path}
              onClick={() => setSelectedPath(f.path)}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center gap-2 transition-all ${
                selectedPath === f.path
                  ? 'bg-[#E5A93C] text-[#121214] font-bold shadow'
                  : 'text-gray-300 hover:bg-[#20202A]'
              }`}
            >
              <FileCode className="w-4 h-4 shrink-0" />
              <span className="truncate">{f.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Code Display */}
      <div className="md:col-span-8 bg-[#14141A] rounded-2xl border border-[#242430] p-5 flex flex-col">
        <div className="flex items-center justify-between pb-3 border-b border-[#242430] mb-3">
          <div>
            <span className="font-mono text-xs font-bold text-[#FFD54F]">{currentFile.path}</span>
            <span className="block text-[10px] text-gray-500">Pure Java 7 / KitKat SDK 19 Target</span>
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1 bg-[#20202A] hover:bg-[#2C2C3A] text-[#E5A93C] rounded-lg text-xs font-semibold border border-[#303040]"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy Code'}
          </button>
        </div>

        <pre className="p-4 bg-[#0D0D10] rounded-xl border border-[#1E1E28] text-xs font-mono text-gray-300 overflow-x-auto max-h-[440px] leading-relaxed">
          {currentFile.code}
        </pre>
      </div>
    </div>
  );
};
