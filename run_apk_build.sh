#!/bin/bash
set -e

echo "=== [1/8] Generating R.java with aapt ==="
aapt package -m -J YangKaiBrowser/source/src \
    -M YangKaiBrowser/source/AndroidManifest.xml \
    -S YangKaiBrowser/source/res \
    -I /usr/lib/android-sdk/platforms/android-23/android.jar

echo "=== [2/8] Compiling Java classes with javac (Target 1.7 / Dalvik compatible) ==="
rm -rf YangKaiBrowser/build_tmp
mkdir -p YangKaiBrowser/build_tmp/classes
find YangKaiBrowser/source/src -name "*.java" > YangKaiBrowser/build_tmp/sources.txt
javac -source 7 -target 7 \
    -bootclasspath /usr/lib/android-sdk/platforms/android-23/android.jar \
    -cp /usr/lib/android-sdk/platforms/android-23/android.jar \
    -d YangKaiBrowser/build_tmp/classes \
    @YangKaiBrowser/build_tmp/sources.txt

echo "=== [3/8] Dexing bytecode into classes.dex ==="
/usr/lib/android-sdk/build-tools/debian/dx --dex \
    --output=YangKaiBrowser/build_tmp/classes.dex \
    YangKaiBrowser/build_tmp/classes

echo "=== [4/8] Packaging APK resources and assets with aapt ==="
aapt package -f \
    -M YangKaiBrowser/source/AndroidManifest.xml \
    -S YangKaiBrowser/source/res \
    -A YangKaiBrowser/source/assets \
    -I /usr/lib/android-sdk/platforms/android-23/android.jar \
    -F YangKaiBrowser/build_tmp/unaligned.apk

echo "=== [5/8] Injecting classes.dex into APK ==="
(cd YangKaiBrowser/build_tmp && aapt add unaligned.apk classes.dex)

echo "=== [6/8] 4-byte ZipAligning APK ==="
zipalign -f -p 4 YangKaiBrowser/build_tmp/unaligned.apk YangKaiBrowser/build_tmp/aligned.apk

echo "=== [7/8] Signing APKs (Persistent Keystore + v1/v2/v3 Schemes) ==="
mkdir -p YangKaiBrowser/apk

# Persistent Debug Keystore
if [ ! -f YangKaiBrowser/debug.keystore ]; then
    keytool -genkeypair -noprompt -v -keystore YangKaiBrowser/debug.keystore \
        -storepass android -alias androiddebugkey -keypass android \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -dname "CN=Android Debug,O=Android,C=US"
fi

apksigner sign --ks YangKaiBrowser/debug.keystore --ks-pass pass:android \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --out YangKaiBrowser/apk/YangKaiBrowser-debug.apk \
    YangKaiBrowser/build_tmp/aligned.apk

# Persistent Release Keystore (Never overwrite to maintain certificate continuity)
if [ ! -f YangKaiBrowser/release.keystore ]; then
    keytool -genkeypair -noprompt -v -keystore YangKaiBrowser/release.keystore \
        -storepass yangkai2026 -alias yangkairelease -keypass yangkai2026 \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -dname "CN=Yang Kai Release,OU=Dragon Engineering,O=YangKaiBrowser,C=US"
fi

apksigner sign --ks YangKaiBrowser/release.keystore --ks-pass pass:yangkai2026 \
    --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
    --out YangKaiBrowser/apk/YangKaiBrowser-release.apk \
    YangKaiBrowser/build_tmp/aligned.apk

echo "=== [8/8] Verifying APK Signatures and calculating SHA-256 ==="
echo "--- RELEASE APK VERIFY ---"
apksigner verify -v YangKaiBrowser/apk/YangKaiBrowser-release.apk

echo "--- SHA-256 CALCULATION ---"
sha256sum YangKaiBrowser/apk/YangKaiBrowser-release.apk > YangKaiBrowser/SHA256.txt
sha256sum YangKaiBrowser/apk/YangKaiBrowser-debug.apk >> YangKaiBrowser/SHA256.txt
cat YangKaiBrowser/SHA256.txt

echo "--- APK BADGING & METADATA ---"
aapt dump badging YangKaiBrowser/apk/YangKaiBrowser-release.apk | head -n 16

ls -lh YangKaiBrowser/apk/
echo "=== BUILD COMPLETE! ==="
