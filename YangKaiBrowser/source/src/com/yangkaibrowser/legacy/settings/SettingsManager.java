package com.yangkaibrowser.legacy.settings;

import android.content.Context;
import android.content.SharedPreferences;

public class SettingsManager {
    private static final String PREF_NAME = "yangkai_prefs";
    public static final String KEY_SEARCH_ENGINE = "search_engine";
    public static final String KEY_JAVASCRIPT = "js_enabled";
    public static final String KEY_IMAGES = "images_enabled";
    public static final String KEY_SAVE_PASSWORDS = "save_passwords";
    public static final String KEY_USER_AGENT = "user_agent_mode";
    public static final String KEY_CURSOR_SPEED = "cursor_speed";
    public static final String KEY_PERFORMANCE_MODE = "perf_mode";

    public static final int UA_DEFAULT = 0;
    public static final int UA_MOBILE = 1;
    public static final int UA_DESKTOP = 2;

    private final SharedPreferences prefs;

    public SettingsManager(Context context) {
        this.prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static final String DEFAULT_SEARCH_ENGINE = "https://www.bing.com/search?q=";

    public String getSearchEngine() {
        return prefs.getString(KEY_SEARCH_ENGINE, DEFAULT_SEARCH_ENGINE);
    }

    public void setSearchEngine(String url) {
        prefs.edit().putString(KEY_SEARCH_ENGINE, url).commit();
    }

    public boolean isJavaScriptEnabled() {
        return prefs.getBoolean(KEY_JAVASCRIPT, true);
    }

    public void setJavaScriptEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_JAVASCRIPT, enabled).commit();
    }

    public boolean isImagesEnabled() {
        return prefs.getBoolean(KEY_IMAGES, true);
    }

    public void setImagesEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_IMAGES, enabled).commit();
    }

    public boolean isSavePasswordsEnabled() {
        return prefs.getBoolean(KEY_SAVE_PASSWORDS, false); // Strictly false by default
    }

    public void setSavePasswordsEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_SAVE_PASSWORDS, enabled).commit();
    }

    public int getUserAgentMode() {
        return prefs.getInt(KEY_USER_AGENT, UA_DEFAULT);
    }

    public void setUserAgentMode(int mode) {
        prefs.edit().putInt(KEY_USER_AGENT, mode).commit();
    }

    public int getCursorSpeed() {
        return prefs.getInt(KEY_CURSOR_SPEED, 18);
    }

    public void setCursorSpeed(int speed) {
        prefs.edit().putInt(KEY_CURSOR_SPEED, speed).commit();
    }

    public boolean isPerformanceMode() {
        return prefs.getBoolean(KEY_PERFORMANCE_MODE, true);
    }

    public void setPerformanceMode(boolean enabled) {
        prefs.edit().putBoolean(KEY_PERFORMANCE_MODE, enabled).commit();
    }
}
