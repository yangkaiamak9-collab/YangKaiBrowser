#!/usr/bin/env python3
import os
import sys
import subprocess
import hashlib
import struct
import zlib

print("[*] Starting Yang Kai Browser autonomous build process...")
WORKSPACE_DIR = os.path.abspath(os.getcwd())
PROJECT_DIR = os.path.join(WORKSPACE_DIR, "YangKaiBrowser")
SOURCE_DIR = os.path.join(PROJECT_DIR, "source")
APK_DIR = os.path.join(PROJECT_DIR, "apk")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
BUILD_TEMP = os.path.join(PROJECT_DIR, "build_tmp")

os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "browser"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "tv"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "tabs"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "data"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "performance"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "settings"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "src", "com", "yangkaibrowser", "legacy", "compatibility"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "res", "drawable"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "res", "layout"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "res", "values"), exist_ok=True)
os.makedirs(os.path.join(SOURCE_DIR, "assets"), exist_ok=True)
os.makedirs(APK_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(BUILD_TEMP, exist_ok=True)

# 1. Create simple 96x96 valid PNG icon (Dragon Gold & Black)
def create_png_icon(filepath):
    width, height = 96, 96
    # Create raw RGBA bitmap
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # filter type 0 (None)
        for x in range(width):
            # Center distance
            dx = x - width / 2
            dy = y - height / 2
            dist = (dx*dx + dy*dy) ** 0.5
            # Circle radius 42
            if dist <= 42:
                # Golden dragon shield
                if dist >= 38: # gold border
                    raw_data.extend([229, 169, 60, 255]) # #E5A93C
                elif abs(dx) < 6 and abs(dy) < 24: # dragon spine / sword
                    raw_data.extend([229, 169, 60, 255])
                elif abs(dy) < 6 and abs(dx) < 20: # crossbar
                    raw_data.extend([192, 57, 43, 255]) # deep crimson
                elif (dx > 0 and dy < 0) or (dx < 0 and dy > 0):
                    raw_data.extend([28, 28, 30, 255]) # dark slate
                else:
                    raw_data.extend([18, 18, 20, 255]) # deep black
            else:
                raw_data.extend([0, 0, 0, 0]) # transparent

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw_data)))
    png += chunk(b'IEND', b'')

    with open(filepath, 'wb') as f:
        f.write(png)

create_png_icon(os.path.join(SOURCE_DIR, "res", "drawable", "ic_launcher.png"))
create_png_icon(os.path.join(SOURCE_DIR, "res", "drawable", "ic_dragon.png"))
print("[+] Created dragon application icons")

# 2. AndroidManifest.xml
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.yangkaibrowser.legacy"
    android:versionCode="1"
    android:versionName="1.0.0">

    <!-- Minimum Android 4.4.4 KitKat (API 19) Target -->
    <uses-sdk
        android:minSdkVersion="19"
        android:targetSdkVersion="19" />

    <!-- Minimum required permissions strictly justified -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

    <!-- TV hardware declarations: Touchscreen not required, Leanback compatible -->
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

        <!-- Main Single Activity - Landscape TV First -->
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
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="http" />
                <data android:scheme="https" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

with open(os.path.join(SOURCE_DIR, "AndroidManifest.xml"), "w") as f:
    f.write(manifest_content)

# 3. Resources (values, drawables, layouts)
with open(os.path.join(SOURCE_DIR, "res", "values", "strings.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Yang Kai Browser</string>
    <string name="app_tagline">Autonomous Legacy TV Browser</string>
    <string name="search_hint">Enter URL or Search Query...</string>
    <string name="btn_back">◀ Back</string>
    <string name="btn_forward">Forward ▶</string>
    <string name="btn_reload">⟳</string>
    <string name="btn_home">🏠</string>
    <string name="btn_tabs">Tabs (1)</string>
    <string name="btn_menu">☰</string>
    <string name="btn_cursor">🎯 Pointer</string>
    <string name="quick_search">DuckDuckGo</string>
    <string name="quick_youtube">YouTube Web</string>
    <string name="quick_wiki">Wikipedia</string>
    <string name="quick_archive">Archive.org</string>
    <string name="quick_news">Lite News</string>
    <string name="nav_history">History</string>
    <string name="nav_bookmarks">Bookmarks</string>
    <string name="nav_downloads">Downloads</string>
    <string name="nav_settings">Settings</string>
    <string name="nav_diagnostics">Diagnostics</string>
    <string name="dialog_title_settings">Yang Kai Browser Settings</string>
    <string name="dialog_title_tabs">Tab Manager (Max 3)</string>
    <string name="dialog_title_history">Browsing History (Max 300)</string>
    <string name="dialog_title_bookmarks">Bookmarks</string>
    <string name="dialog_title_diagnostics">Legacy TV Hardware Diagnostics</string>
</resources>
""")

with open(os.path.join(SOURCE_DIR, "res", "values", "colors.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="yk_black">#121214</color>
    <color name="yk_dark_surface">#1A1A1E</color>
    <color name="yk_card_surface">#24242A</color>
    <color name="yk_gold">#E5A93C</color>
    <color name="yk_gold_bright">#FFD54F</color>
    <color name="yk_crimson">#8B1E1E</color>
    <color name="yk_crimson_light">#C0392B</color>
    <color name="yk_white">#F0F0F2</color>
    <color name="yk_gray_text">#A0A0A8</color>
    <color name="yk_focus_glow">#FFD54F</color>
    <color name="yk_cursor_color">#E5A93C</color>
</resources>
""")

with open(os.path.join(SOURCE_DIR, "res", "values", "styles.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="YangKaiDarkTheme" parent="@android:style/Theme.NoTitleBar.Fullscreen">
        <item name="android:windowBackground">@color/yk_black</item>
        <item name="android:textColor">@color/yk_white</item>
    </style>
</resources>
""")

with open(os.path.join(SOURCE_DIR, "res", "drawable", "btn_normal.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#24242A" />
    <stroke android:width="1dp" android:color="#3A3A44" />
    <corners android:radius="4dp" />
</shape>
""")

with open(os.path.join(SOURCE_DIR, "res", "drawable", "btn_focused.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#353540" />
    <stroke android:width="3dp" android:color="#FFD54F" />
    <corners android:radius="4dp" />
</shape>
""")

with open(os.path.join(SOURCE_DIR, "res", "drawable", "btn_selector.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true" android:drawable="@drawable/btn_focused" />
    <item android:state_pressed="true" android:drawable="@drawable/btn_focused" />
    <item android:drawable="@drawable/btn_normal" />
</selector>
""")

with open(os.path.join(SOURCE_DIR, "res", "drawable", "edittext_selector.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true">
        <shape android:shape="rectangle">
            <solid android:color="#1A1A22" />
            <stroke android:width="3dp" android:color="#FFD54F" />
            <corners android:radius="4dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#16161C" />
            <stroke android:width="1dp" android:color="#444450" />
            <corners android:radius="4dp" />
        </shape>
    </item>
</selector>
""")

# activity_main.xml layout
with open(os.path.join(SOURCE_DIR, "res", "layout", "activity_main.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/yk_black">

    <!-- Top Navigation Toolbar (TV D-Pad friendly) -->
    <LinearLayout
        android:id="@+id/top_toolbar"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:layout_alignParentTop="true"
        android:orientation="horizontal"
        android:background="@color/yk_dark_surface"
        android:gravity="center_vertical"
        android:paddingLeft="8dp"
        android:paddingRight="8dp">

        <Button
            android:id="@+id/btn_back"
            android:layout_width="wrap_content"
            android:layout_height="38dp"
            android:text="@string/btn_back"
            android:textSize="13sp"
            android:textColor="@color/yk_white"
            android:background="@drawable/btn_selector"
            android:paddingLeft="10dp"
            android:paddingRight="10dp"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_forward"
            android:nextFocusDown="@+id/url_input" />

        <Button
            android:id="@+id/btn_forward"
            android:layout_width="wrap_content"
            android:layout_height="38dp"
            android:layout_marginLeft="4dp"
            android:text="@string/btn_forward"
            android:textSize="13sp"
            android:textColor="@color/yk_white"
            android:background="@drawable/btn_selector"
            android:paddingLeft="10dp"
            android:paddingRight="10dp"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_reload"
            android:nextFocusDown="@+id/url_input" />

        <Button
            android:id="@+id/btn_reload"
            android:layout_width="44dp"
            android:layout_height="38dp"
            android:layout_marginLeft="4dp"
            android:text="@string/btn_reload"
            android:textSize="16sp"
            android:textColor="@color/yk_gold"
            android:background="@drawable/btn_selector"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_home"
            android:nextFocusDown="@+id/url_input" />

        <Button
            android:id="@+id/btn_home"
            android:layout_width="44dp"
            android:layout_height="38dp"
            android:layout_marginLeft="4dp"
            android:text="@string/btn_home"
            android:textSize="16sp"
            android:textColor="@color/yk_gold"
            android:background="@drawable/btn_selector"
            android:focusable="true"
            android:nextFocusRight="@+id/url_input"
            android:nextFocusDown="@+id/url_input" />

        <!-- Address / Search Bar -->
        <EditText
            android:id="@+id/url_input"
            android:layout_width="0dp"
            android:layout_height="38dp"
            android:layout_weight="1"
            android:layout_marginLeft="6dp"
            android:layout_marginRight="6dp"
            android:hint="@string/search_hint"
            android:textColorHint="@color/yk_gray_text"
            android:textColor="@color/yk_white"
            android:background="@drawable/edittext_selector"
            android:textSize="13sp"
            android:paddingLeft="12dp"
            android:paddingRight="12dp"
            android:singleLine="true"
            android:imeOptions="actionGo"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_go" />

        <Button
            android:id="@+id/btn_go"
            android:layout_width="wrap_content"
            android:layout_height="38dp"
            android:text="Go"
            android:textSize="13sp"
            android:textStyle="bold"
            android:textColor="@color/yk_black"
            android:background="@drawable/btn_selector"
            android:paddingLeft="14dp"
            android:paddingRight="14dp"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_tabs" />

        <Button
            android:id="@+id/btn_tabs"
            android:layout_width="wrap_content"
            android:layout_height="38dp"
            android:layout_marginLeft="4dp"
            android:text="@string/btn_tabs"
            android:textSize="13sp"
            android:textColor="@color/yk_gold"
            android:background="@drawable/btn_selector"
            android:paddingLeft="10dp"
            android:paddingRight="10dp"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_cursor_toggle" />

        <Button
            android:id="@+id/btn_cursor_toggle"
            android:layout_width="wrap_content"
            android:layout_height="38dp"
            android:layout_marginLeft="4dp"
            android:text="@string/btn_cursor"
            android:textSize="13sp"
            android:textColor="@color/yk_white"
            android:background="@drawable/btn_selector"
            android:paddingLeft="8dp"
            android:paddingRight="8dp"
            android:focusable="true"
            android:nextFocusRight="@+id/btn_menu" />

        <Button
            android:id="@+id/btn_menu"
            android:layout_width="44dp"
            android:layout_height="38dp"
            android:layout_marginLeft="4dp"
            android:text="@string/btn_menu"
            android:textSize="16sp"
            android:textColor="@color/yk_white"
            android:background="@drawable/btn_selector"
            android:focusable="true" />
    </LinearLayout>

    <!-- Progress indicator bar -->
    <ProgressBar
        android:id="@+id/progress_bar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="3dp"
        android:layout_below="@+id/top_toolbar"
        android:visibility="gone"
        android:max="100" />

    <!-- Web Content Container -->
    <FrameLayout
        android:id="@+id/webview_container"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:layout_below="@+id/progress_bar"
        android:layout_above="@+id/status_bar"
        android:background="@color/yk_black" />

    <!-- Virtual Cursor View (Overlay for TV Remote D-Pad pointing) -->
    <ImageView
        android:id="@+id/virtual_cursor"
        android:layout_width="22dp"
        android:layout_height="22dp"
        android:src="@drawable/ic_launcher"
        android:visibility="gone" />

    <!-- Bottom Mini Status Bar: RAM & Status Diagnostics -->
    <LinearLayout
        android:id="@+id/status_bar"
        android:layout_width="match_parent"
        android:layout_height="22dp"
        android:layout_alignParentBottom="true"
        android:background="@color/yk_dark_surface"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:paddingLeft="10dp"
        android:paddingRight="10dp">

        <TextView
            android:id="@+id/tv_brand"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="🐉 Yang Kai v1.0.0 [API 19 / 512MB RAM]"
            android:textColor="@color/yk_gold"
            android:textSize="11sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/tv_mem_status"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:gravity="right"
            android:text="MEM: NORMAL (Heap: 12MB / 128MB)"
            android:textColor="@color/yk_gray_text"
            android:textSize="11sp" />

        <TextView
            android:id="@+id/tv_mode_status"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginLeft="12dp"
            android:text="MODE: DPAD FOCUS"
            android:textColor="@color/yk_gold_bright"
            android:textSize="11sp" />
    </LinearLayout>

    <!-- Custom On-Screen Key Event Tester / Forensic Overlay (Toggleable) -->
    <LinearLayout
        android:id="@+id/key_event_overlay"
        android:layout_width="260dp"
        android:layout_height="wrap_content"
        android:layout_alignParentBottom="true"
        android:layout_alignParentRight="true"
        android:layout_margin="28dp"
        android:background="#DD121216"
        android:padding="8dp"
        android:orientation="vertical"
        android:visibility="gone">

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="REMOTE KEY EVENT FORENSICS"
            android:textColor="@color/yk_gold"
            android:textSize="11sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/tv_last_key"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Last Key: None"
            android:textColor="@color/yk_white"
            android:textSize="11sp" />

        <TextView
            android:id="@+id/tv_key_code"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="KeyCode: 0 | Action: IDLE"
            android:textColor="@color/yk_gray_text"
            android:textSize="10sp" />
    </LinearLayout>
</RelativeLayout>
""")

# 4. Assets: homepage.html, diagnostics.html, error.html
with open(os.path.join(SOURCE_DIR, "assets", "homepage.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yang Kai Browser</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background-color: #121214;
    color: #F0F0F2;
    font-family: sans-serif;
    padding: 24px 32px;
    user-select: none;
}
.header {
    text-align: center;
    margin-bottom: 24px;
}
.dragon-badge {
    color: #E5A93C;
    font-size: 32px;
    font-weight: bold;
    letter-spacing: 2px;
}
.subtitle {
    color: #A0A0A8;
    font-size: 13px;
    margin-top: 4px;
}
.specs {
    display: inline-block;
    background: #1E1E24;
    border: 1px solid #3A3A44;
    border-radius: 4px;
    padding: 4px 12px;
    margin-top: 8px;
    font-size: 11px;
    color: #E5A93C;
}
.section-title {
    color: #E5A93C;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    border-bottom: 1px solid #282830;
    padding-bottom: 6px;
}
.grid {
    display: table;
    width: 100%;
    margin-bottom: 24px;
}
.row {
    display: table-row;
}
.tile {
    display: table-cell;
    width: 20%;
    padding: 6px;
}
.tile-btn {
    display: block;
    background: #1C1C22;
    border: 2px solid #2A2A34;
    border-radius: 6px;
    padding: 14px 10px;
    text-decoration: none;
    color: #F0F0F2;
    text-align: center;
    font-size: 14px;
    font-weight: bold;
}
.tile-btn:focus, .tile-btn:hover {
    background: #2D2D38;
    border-color: #FFD54F;
    color: #FFD54F;
    outline: none;
}
.icon {
    font-size: 20px;
    display: block;
    margin-bottom: 6px;
}
.footer-note {
    text-align: center;
    color: #666672;
    font-size: 11px;
    margin-top: 20px;
}
</style>
</head>
<body>
<div class="header">
    <div class="dragon-badge">🐉 YANG KAI BROWSER</div>
    <div class="subtitle">Hardware-Specific Autonomous Legacy TV Browser</div>
    <div class="specs">Target: Android 4.4.4 KitKat • API 19 • 512MB RAM • ARM32 • D-Pad Remote</div>
</div>

<div class="section-title">⚡ Quick Access Web Portals</div>
<div class="grid">
    <div class="row">
        <div class="tile">
            <a class="tile-btn" href="https://html.duckduckgo.com/html/">
                <span class="icon">🔍</span>DuckDuckGo Lite
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="https://m.youtube.com">
                <span class="icon">📺</span>YouTube Web
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="https://en.m.wikipedia.org">
                <span class="icon">📖</span>Wikipedia
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="https://archive.org">
                <span class="icon">🏛️</span>Archive.org
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="https://news.ycombinator.com">
                <span class="icon">📰</span>Hacker News
            </a>
        </div>
    </div>
</div>

<div class="section-title">🛠️ Local Browser Utilities (Offline Capable)</div>
<div class="grid">
    <div class="row">
        <div class="tile">
            <a class="tile-btn" href="javascript:yangkai.openBookmarks()">
                <span class="icon">⭐</span>Bookmarks
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="javascript:yangkai.openHistory()">
                <span class="icon">🕒</span>History
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="javascript:yangkai.openDownloads()">
                <span class="icon">📥</span>Downloads
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="file:///android_asset/diagnostics.html">
                <span class="icon">🩺</span>Diagnostics
            </a>
        </div>
        <div class="tile">
            <a class="tile-btn" href="javascript:yangkai.openSettings()">
                <span class="icon">⚙️</span>Settings
            </a>
        </div>
    </div>
</div>

<div class="footer-note">
    100% Standalone • Zero Analytics • Zero Cloud Telemetry • Preserves 512MB RAM
</div>
</body>
</html>
""")

with open(os.path.join(SOURCE_DIR, "assets", "diagnostics.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Diagnostics - Yang Kai Browser</title>
<style>
body { background: #121214; color: #F0F0F2; font-family: sans-serif; padding: 20px; }
h1 { color: #E5A93C; font-size: 20px; margin-bottom: 16px; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { border: 1px solid #333; padding: 8px 12px; text-align: left; font-size: 13px; }
th { background: #1E1E24; color: #E5A93C; }
.pass { color: #2ECC71; font-weight: bold; }
.btn { display: inline-block; background: #2A2A34; border: 1px solid #FFD54F; color: #FFD54F; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-top: 16px; font-weight: bold; }
</style>
</head>
<body>
<h1>🐉 Legacy TV Hardware & Runtime Diagnostics</h1>
<table>
    <tr><th>Subsystem</th><th>Target Profile</th><th>Status</th></tr>
    <tr><td>OS Version</td><td>Android 4.4.4 KitKat</td><td class="pass">TARGETED (API 19)</td></tr>
    <tr><td>Dalvik Architecture</td><td>ARM32 (armeabi-v7a / Cortex-A7)</td><td class="pass">COMPATIBLE</td></tr>
    <tr><td>System Memory</td><td>512 MB Physical RAM</td><td class="pass">MONITORED</td></tr>
    <tr><td>Engine Mode</td><td>System WebView (KitKat Chromium 30/33)</td><td class="pass">INTEGRATED</td></tr>
    <tr><td>Input Controller</td><td>Physical TV Remote (D-Pad + Center)</td><td class="pass">SUPPORTED</td></tr>
    <tr><td>Virtual Pointer</td><td>D-Pad Virtual Cursor System</td><td class="pass">READY</td></tr>
    <tr><td>Tab Limit</td><td>Strict Max 3 Tabs with Memory Eviction</td><td class="pass">ACTIVE</td></tr>
    <tr><td>Cache Strategy</td><td>LOW Storage Footprint (< 10MB)</td><td class="pass">CONFIGURED</td></tr>
    <tr><td>SQLite Database</td><td>Zero-ORM Direct SQLite</td><td class="pass">VERIFIED</td></tr>
</table>
<a class="btn" href="file:///android_asset/homepage.html">◀ Return to Home</a>
</body>
</html>
""")

with open(os.path.join(SOURCE_DIR, "assets", "error.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Connection Error</title>
<style>
body { background: #121214; color: #F0F0F2; font-family: sans-serif; text-align: center; padding: 60px 20px; }
.icon { font-size: 48px; color: #E74C3C; margin-bottom: 16px; }
h1 { font-size: 22px; color: #E5A93C; margin-bottom: 8px; }
p { font-size: 14px; color: #A0A0A8; margin-bottom: 24px; }
.btn { display: inline-block; background: #24242A; border: 2px solid #FFD54F; color: #FFD54F; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; margin: 0 8px; }
</style>
</head>
<body>
<div class="icon">⚠️</div>
<h1>Connection Notice</h1>
<p>Unable to load web resource. Check device network connectivity or target site SSL certificate.</p>
<a class="btn" href="javascript:history.back()">◀ Go Back</a>
<a class="btn" href="javascript:location.reload()">⟳ Retry</a>
<a class="btn" href="file:///android_asset/homepage.html">🏠 Home</a>
</body>
</html>
""")

print("[+] Created resources, layouts, and assets")

