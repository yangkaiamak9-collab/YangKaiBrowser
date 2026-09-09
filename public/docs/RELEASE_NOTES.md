# 🚀 YANG KAI BROWSER — RELEASE NOTES v1.0.0

**Release Date:** September 2026  
**Build Code:** 1  
**Build Name:** 1.0.0 (Dragon Flame)  
**Binary Size:** 42,083 bytes (41.1 KB)  

---

### Highlights & Features
* **Engineered for Legacy Android TV Boxes:** Tailored for ARM Cortex-A7, 512MB RAM, Android 4.4.4 KitKat (API 19).
* **Ultra-Compact Footprint:** Entire application is only 41.1 KB, installing in milliseconds without taxing low-end 4GB NAND flash storage.
* **Remote Control First:**
  * Full D-Pad direction navigation with high-visibility gold (#FFD54F) focus outlines.
  * Virtual Cursor mode (toggled via button or DPAD toggle) allowing freeform pointer interaction on complex websites using the TV remote.
  * Real-time Key Event Tester forensic overlay.
* **Memory Protection Subsystem:**
  * Strict cap of 3 concurrent tabs.
  * Automatic WebView eviction for inactive tabs when heap memory exceeds 78%.
  * SQLite database with auto-trimming history (capped at 300 entries).
* **Local Offline Experience:**
  * Built-in local offline homepage with quick portals.
  * Offline diagnostics matrix.
  * Local error fallback page.
* **Privacy & Security:**
  * Zero telemetry and zero analytics.
  * SSL security interception (no insecure auto-proceed on broken certificates).
