#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " YANG KAI BROWSER — ABSOLUTE BULLETPROOF APK BUILD ENGINE"
echo " Target: Android 4.4.4 KitKat (API 19) • ARM32 • TV Remote"
echo " Dual-Digest Signing (SHA-1 + SHA-256) • Dalvik DEX 035"
echo "=========================================================="

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$WORKDIR"

export PATH="/usr/lib/android-sdk/build-tools/debian:$PATH"

rm -rf YangKaiBrowser/build_tmp
mkdir -p YangKaiBrowser/build_tmp/classes
mkdir -p YangKaiBrowser/apk
mkdir -p public/apk
mkdir -p dist/apk

echo "=== [1/8] Generating R.java from Android Resources ==="
aapt package -f -m \
    -J YangKaiBrowser/source/src \
    -M YangKaiBrowser/source/AndroidManifest.xml \
    -S YangKaiBrowser/source/res \
    -I /usr/lib/android-sdk/platforms/android-23/android.jar

echo "=== [2/8] Compiling Java 7 Bytecode for Dalvik Virtual Machine ==="
find YangKaiBrowser/source/src -name "*.java" > YangKaiBrowser/build_tmp/sources.txt
javac -source 7 -target 7 \
    -bootclasspath /usr/lib/android-sdk/platforms/android-23/android.jar \
    -d YangKaiBrowser/build_tmp/classes \
    @YangKaiBrowser/build_tmp/sources.txt

echo "=== [3/8] Converting Bytecode to Dalvik Executable (classes.dex) ==="
dx --dex --output=YangKaiBrowser/build_tmp/classes.dex YangKaiBrowser/build_tmp/classes

echo "=== [4/8] Packaging Main Release APK (com.yangkaibrowser.legacy) ==="
aapt package -f \
    -M YangKaiBrowser/source/AndroidManifest.xml \
    -S YangKaiBrowser/source/res \
    -A YangKaiBrowser/source/assets \
    -I /usr/lib/android-sdk/platforms/android-23/android.jar \
    -F YangKaiBrowser/build_tmp/unaligned_release.apk

(cd YangKaiBrowser/build_tmp && aapt add unaligned_release.apk classes.dex)
zipalign -f -p 4 YangKaiBrowser/build_tmp/unaligned_release.apk YangKaiBrowser/build_tmp/aligned_release.apk

echo "=== [5/8] Packaging Standalone APK (com.yangkai.tvbrowser) ==="
# Using --rename-manifest-package ensures a guaranteed fresh package name that avoids any signature conflict
aapt package -f \
    -M YangKaiBrowser/source/AndroidManifest.xml \
    -S YangKaiBrowser/source/res \
    -A YangKaiBrowser/source/assets \
    -I /usr/lib/android-sdk/platforms/android-23/android.jar \
    --rename-manifest-package com.yangkai.tvbrowser \
    -F YangKaiBrowser/build_tmp/unaligned_standalone.apk

(cd YangKaiBrowser/build_tmp && aapt add unaligned_standalone.apk classes.dex)
zipalign -f -p 4 YangKaiBrowser/build_tmp/unaligned_standalone.apk YangKaiBrowser/build_tmp/aligned_standalone.apk

echo "=== [6/8] Packaging Universal Modern APK (targetSdkVersion 28) ==="
mkdir -p YangKaiBrowser/build_tmp/modern
sed 's/android:targetSdkVersion="19"/android:targetSdkVersion="28"/g' YangKaiBrowser/source/AndroidManifest.xml > YangKaiBrowser/build_tmp/modern/AndroidManifest.xml

aapt package -f \
    -M YangKaiBrowser/build_tmp/modern/AndroidManifest.xml \
    -S YangKaiBrowser/source/res \
    -A YangKaiBrowser/source/assets \
    -I /usr/lib/android-sdk/platforms/android-23/android.jar \
    --rename-manifest-package com.yangkai.tvbrowser \
    -F YangKaiBrowser/build_tmp/unaligned_universal.apk

(cd YangKaiBrowser/build_tmp && aapt add unaligned_universal.apk classes.dex)
zipalign -f -p 4 YangKaiBrowser/build_tmp/unaligned_universal.apk YangKaiBrowser/build_tmp/aligned_universal.apk

echo "=== [7/8] Keystore Setup & Universal Signing ==="
# Generating production keystore with startdate 2010 to prevent CertificateNotYetValidException on older clocks
if [ ! -f YangKaiBrowser/release.keystore ]; then
    keytool -genkeypair -noprompt -v -keystore YangKaiBrowser/release.keystore \
        -storepass yangkai2026 -alias yangkairelease -keypass yangkai2026 \
        -keyalg RSA -keysize 2048 -validity 20000 \
        -startdate "2010/01/01 00:00:00" \
        -dname "CN=Yang Kai Release,OU=Dragon Engineering,O=YangKaiBrowser,C=US"
fi

if [ ! -f YangKaiBrowser/debug.keystore ]; then
    keytool -genkeypair -noprompt -v -keystore YangKaiBrowser/debug.keystore \
        -storepass android -alias androiddebugkey -keypass android \
        -keyalg RSA -keysize 2048 -validity 20000 \
        -startdate "2010/01/01 00:00:00" \
        -dname "CN=Android Debug,O=Android,C=US"
fi

# CRITICAL: We use --min-sdk-version 1
# This forces apksigner to generate SHA1-Digest-Manifest and SHA1-Digest for KitKat 4.4.4 Dalvik JarVerifier,
# while ALSO generating SHA-256 v2 and v3 signatures for modern Android!
echo "Signing Release APK with dual SHA-1 + SHA-256 digests..."
apksigner sign --ks YangKaiBrowser/release.keystore --ks-pass pass:yangkai2026 \
    --min-sdk-version 1 \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --out YangKaiBrowser/apk/YangKaiBrowser-release.apk \
    YangKaiBrowser/build_tmp/aligned_release.apk

echo "Signing Standalone APK with dual SHA-1 + SHA-256 digests..."
apksigner sign --ks YangKaiBrowser/release.keystore --ks-pass pass:yangkai2026 \
    --min-sdk-version 1 \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --out YangKaiBrowser/apk/YangKaiBrowser-standalone.apk \
    YangKaiBrowser/build_tmp/aligned_standalone.apk

echo "Signing Universal Modern APK..."
apksigner sign --ks YangKaiBrowser/release.keystore --ks-pass pass:yangkai2026 \
    --min-sdk-version 1 \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --out YangKaiBrowser/apk/YangKaiBrowser-universal.apk \
    YangKaiBrowser/build_tmp/aligned_universal.apk

echo "Signing Debug APK..."
apksigner sign --ks YangKaiBrowser/debug.keystore --ks-pass pass:android \
    --min-sdk-version 1 \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --out YangKaiBrowser/apk/YangKaiBrowser-debug.apk \
    YangKaiBrowser/build_tmp/aligned_release.apk

echo "=== [8/8] Artifact Verification & Archiving ==="
cp YangKaiBrowser/apk/*.apk public/apk/
cp YangKaiBrowser/apk/*.apk dist/apk/ 2>/dev/null || true

python3 -c "
import zipfile, os
with zipfile.ZipFile('YangKaiBrowser/apk/YangKaiBrowser-Release-v1.0.3.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('YangKaiBrowser/apk/YangKaiBrowser-release.apk', 'YangKaiBrowser-release.apk')
    z.write('YangKaiBrowser/apk/YangKaiBrowser-standalone.apk', 'YangKaiBrowser-standalone.apk')
    z.write('YangKaiBrowser/apk/YangKaiBrowser-universal.apk', 'YangKaiBrowser-universal.apk')
"
cp YangKaiBrowser/apk/YangKaiBrowser-Release-v1.0.3.zip public/apk/
cp YangKaiBrowser/apk/YangKaiBrowser-Release-v1.0.3.zip dist/apk/ 2>/dev/null || true

echo "--- VERIFYING APK SIGNATURES ---"
echo "[1] Release:"
apksigner verify -v YangKaiBrowser/apk/YangKaiBrowser-release.apk
echo "[2] Standalone:"
apksigner verify -v YangKaiBrowser/apk/YangKaiBrowser-standalone.apk
echo "[3] Universal:"
apksigner verify -v YangKaiBrowser/apk/YangKaiBrowser-universal.apk

echo "--- SHA-256 HASHES ---"
sha256sum YangKaiBrowser/apk/YangKaiBrowser-release.apk > YangKaiBrowser/SHA256.txt
sha256sum YangKaiBrowser/apk/YangKaiBrowser-standalone.apk >> YangKaiBrowser/SHA256.txt
sha256sum YangKaiBrowser/apk/YangKaiBrowser-universal.apk >> YangKaiBrowser/SHA256.txt
sha256sum YangKaiBrowser/apk/YangKaiBrowser-debug.apk >> YangKaiBrowser/SHA256.txt
cat YangKaiBrowser/SHA256.txt
cp YangKaiBrowser/SHA256.txt SHA256.txt

echo "--- AAPT BADGING DUMP ---"
aapt dump badging YangKaiBrowser/apk/YangKaiBrowser-release.apk | head -n 12
echo "=========================================================="
echo " BUILD SUCCESSFUL! ALL ARTIFACTS VERIFIED AND READY!"
echo "=========================================================="
