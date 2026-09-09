# 🏛️ YANG KAI BROWSER — ARCHITECTURE SPECIFICATION

```
YangKaiBrowser/
├── source/
│   ├── AndroidManifest.xml
│   ├── res/
│   │   ├── drawable/          (High-contrast TV selectors & icons)
│   │   ├── layout/            (D-Pad toolbar, WebView container, forensics overlay)
│   │   └── values/            (Strings, Dragon palette #E5A93C/#121214, fullscreen styles)
│   ├── assets/
│   │   ├── homepage.html      (Offline-first TV portal)
│   │   ├── diagnostics.html   (System capability matrix)
│   │   └── error.html         (Safe error fallback)
│   └── src/com/yangkaibrowser/legacy/
│       ├── MainActivity.java                  (Single activity orchestrator)
│       ├── browser/
│       │   ├── BrowserEngine.java             (Engine abstraction interface)
│       │   ├── LegacyWebViewEngine.java       (KitKat WebView implementation)
│       │   ├── BrowserController.java         (Container attachment & state)
│       │   └── NavigationManager.java         (URL vs search query parser)
│       ├── tv/
│       │   ├── RemoteManager.java             (Key event dispatcher: D-Pad, Center, Back, Menu)
│       │   ├── FocusManager.java              (Initial focus & traversal)
│       │   └── CursorManager.java             (Virtual Pointer simulation with MotionEvents)
│       ├── tabs/
│       │   └── TabManager.java                (Max 3 tabs with Dalvik memory eviction)
│       ├── data/
│       │   ├── BrowserDatabaseHelper.java     (Direct SQLiteOpenHelper)
│       │   ├── HistoryManager.java            (Max 300 history records with auto-trim)
│       │   ├── BookmarkManager.java           (CRUD bookmarks)
│       │   └── DownloadManager.java           (Safe file downloads without auto-execution)
│       ├── performance/
│       │   ├── MemoryManager.java             (Dalvik heap monitor: NORMAL/WARN/CRITICAL/EMERGENCY)
│       │   ├── CacheManager.java              (Cache directory cleanup)
│       │   └── PerformanceMonitor.java        (Startup & page latency timer)
│       ├── settings/
│       │   └── SettingsManager.java           (SharedPreferences configuration)
│       └── compatibility/
│           └── LegacyCompatibility.java       (API 19 runtime diagnostics)
```

## Key Architectural Decisions

1. **Direct SQLite Without ORM:**
   Modern ORMs (Room, greenDAO) inject reflection and annotations that consume megabytes of RAM and slow down Dalvik JIT. `BrowserDatabaseHelper` uses pure Android SDK SQLite statements.

2. **Memory Eviction Strategy:**
   When `MemoryManager` evaluates heap saturation at `CRITICAL` (>78%) or `EMERGENCY` (>88%), `TabManager.evictInactiveWebViews()` destroys background `WebView` native instances, retaining only their target URLs and titles. When the user switches back, the tab is lazily re-instantiated.

3. **Virtual Pointer Subsystem:**
   Many web pages are designed exclusively for mouse/touch. `CursorManager` maintains an on-screen cursor icon moved by D-Pad pulses. When DPAD_CENTER is pressed, it constructs synthetic `ACTION_DOWN` and `ACTION_UP` `MotionEvent` pairs dispatched directly to the underlying WebView view hierarchy.

4. **SSL Interception Policy:**
   Legacy KitKat devices often have outdated root certificates. To protect the user, `LegacyWebViewEngine` intercepts `onReceivedSslError`, cancels the connection, and routes the user to a local secure warning page rather than silently calling `handler.proceed()`.
