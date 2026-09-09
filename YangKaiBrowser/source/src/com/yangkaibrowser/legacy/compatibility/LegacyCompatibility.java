package com.yangkaibrowser.legacy.compatibility;

import android.os.Build;

public class LegacyCompatibility {
    public static boolean isKitKat() {
        return Build.VERSION.SDK_INT == 19;
    }

    public static String getSystemArch() {
        return Build.CPU_ABI != null ? Build.CPU_ABI : "armeabi-v7a";
    }
}
