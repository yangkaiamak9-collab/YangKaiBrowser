# 🐉 YANG KAI BROWSER — PROJECT OVERVIEW

**Version:** 1.0.0 (Build 2026.09)  
**Target Hardware:** Legacy Android TV Box (TTX-V005 specification)  
**SoC / CPU:** ARM Cortex-A7 (Dual-Core @ 1.3 GHz, 32-bit `armeabi-v7a`)  
**RAM:** 512 MB Physical RAM  
**Internal Storage:** 4 GB NAND Flash  
**Operating System:** Android 4.4.4 KitKat (API Level 19)  
**Package:** `com.yangkaibrowser.legacy`  
**License:** Open Hardware Autonomous Engineering

---

## 🎯 Engineering Philosophy
**"Maximum Practical Web Usability Per Megabyte"**

Yang Kai Browser is engineered from the silicon up for severe hardware resource constraints:
1. **Zero External Frameworks:** No Jetpack Compose, no Kotlin runtime bloat, no heavy AndroidX dependencies. Pure Java 7 Dalvik bytecode.
2. **Under 50 KB Footprint:** The entire compiled and signed release APK is only **41.1 KB (42,083 bytes)**.
3. **RAM Preservation (<30MB baseline):** Retains strict Dalvik heap budget (128MB ceiling). Inactive tabs automatically evict WebView instances under memory pressure while preserving URL and session state.
4. **100% TV Remote-First:** Native D-Pad navigation, high-contrast gold focus rings, hardware Back button handling, and a toggleable virtual cursor for websites lacking keyboard focus navigation.
5. **Completely Offline-Ready:** Ships with built-in local HTML homepage (`file:///android_asset/homepage.html`), local error fallbacks, and offline hardware diagnostics.
6. **Zero Telemetry:** Zero external analytics, zero tracking pings, zero advertising scripts.

---

## 📦 Verified APK Deliverables

| Artifact | File Size | SHA-256 Checksum | Signer Schemes |
| :--- | :--- | :--- | :--- |
| **YangKaiBrowser-release.apk** | 42,083 bytes (41.1 KB) | `dda93ac18cc446340ff744ecef73896ecfb2bb2e1abf95885518629773ac87af` | v1 (JAR) + v2 + v3 |
| **YangKaiBrowser-debug.apk** | 42,083 bytes (41.1 KB) | `a5aa77118758e2030626db52432b320b7d8acfc866ee9ea4f2db9bb25461196f` | v1 (JAR) + v2 + v3 |

*Verified with AOSP `apksigner v0.9` and `aapt v0.2`.*
