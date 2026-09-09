# 📥 YANG KAI BROWSER — INSTALLATION GUIDE

### 1. Requirements
* Legacy Android TV Box running Android 4.4.4 KitKat (API 19) or higher.
* Input: IR Remote Control, 2.4G RF Air Mouse, or USB Keyboard/Mouse.
* Minimum Free Storage: 1 MB (APK size is 42 KB).
* Minimum RAM: 256MB - 512MB.

---

### 2. Installation via ADB (Android Debug Bridge)

1. Enable USB Debugging or Network ADB on your TV Box:
   - Go to `Settings` -> `About Device` -> tap `Build Number` 7 times.
   - Go to `Developer Options` -> enable `USB Debugging`.
   - If connecting via WiFi/LAN:
     ```bash
     adb connect <TV_BOX_IP_ADDRESS>:5555
     ```
2. Install the APK:
   ```bash
   adb install -r YangKaiBrowser-release.apk
   ```
3. Launch the browser on the TV:
   ```bash
   adb shell am start -n com.yangkaibrowser.legacy/.MainActivity
   ```

---

### 3. Installation via USB Flash Drive / SD Card

1. Copy `YangKaiBrowser-release.apk` onto a FAT32-formatted USB flash drive.
2. Insert the flash drive into the USB port of the TV Box.
3. Open the TV Box's built-in **File Browser** or **App Installer**.
4. If prompted with *"Install from Unknown Sources"*, tap `Allow` / `Enable`.
5. Tap `YangKaiBrowser-release.apk` and select `Install`.
6. Once installed, launch **Yang Kai Browser** from your TV Home Launcher or Leanback Apps grid.

---

### 4. Remote Control Button Cheat Sheet

| Button | KeyCode | Browser Action |
| :--- | :--- | :--- |
| **D-Pad Arrows** | 19, 20, 21, 22 | Navigate between address bar, navigation buttons, and webpage links (or moves pointer in Virtual Cursor mode) |
| **OK / Center** | 23 / 66 | Click focused link/button, activate input field, or execute virtual cursor click |
| **Back Button** | 4 | Step back in browsing history; if no back history, displays exit confirmation prompt |
| **Menu Button** | 82 | Opens Yang Kai Quick Menu (Bookmarks, History, Diagnostics, Cache Clear, Settings) |
| **Cursor Toggle** | (Toolbar) | Toggles between D-Pad Focus Ring mode and Virtual Pointer mode |
