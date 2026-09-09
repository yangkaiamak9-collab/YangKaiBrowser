package com.yangkaibrowser.legacy.browser;

import java.net.URLEncoder;
import java.util.regex.Pattern;

public class NavigationManager {
    public static final String HOMEPAGE_URL = "file:///android_asset/homepage.html";
    public static final String ERROR_URL = "file:///android_asset/error.html";
    public static final String DIAGNOSTICS_URL = "file:///android_asset/diagnostics.html";

    // Matches standard domain names with optional port and path
    private static final Pattern DOMAIN_PATTERN = Pattern.compile("^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(:[0-9]+)?(/.*)?$");
    // Matches IPv4 addresses with optional port and path
    private static final Pattern IPV4_PATTERN = Pattern.compile("^([0-9]{1,3}\\.){3}[0-9]{1,3}(:[0-9]+)?(/.*)?$");

    public static String resolveInput(String input, String searchEngineUrl) {
        if (input == null || input.trim().isEmpty()) {
            return HOMEPAGE_URL;
        }
        String clean = input.trim();

        // Local shortcuts
        if (clean.equalsIgnoreCase("about:blank") || clean.equalsIgnoreCase("yangkai://home") || clean.equalsIgnoreCase("home")) {
            return HOMEPAGE_URL;
        }
        if (clean.equalsIgnoreCase("diagnostics") || clean.equalsIgnoreCase("yangkai://diag")) {
            return DIAGNOSTICS_URL;
        }

        // Direct protocol specification (Strict Scheme Policy: only http, https, and trusted android_asset)
        if (clean.startsWith("http://") || clean.startsWith("https://")) {
            return clean;
        }
        if (clean.startsWith("file:///android_asset/")) {
            return clean;
        }

        // Security: Block arbitrary local file:/// access (convert to search or reject)
        if (clean.startsWith("file:///")) {
            clean = clean.substring(8);
        }

        // Security: Disallow pseudo-schemes like javascript:, data:, intent:, content:
        if (clean.startsWith("javascript:") || clean.startsWith("data:") || clean.startsWith("intent:") || clean.startsWith("content:")) {
            return HOMEPAGE_URL;
        }

        // Explicitly reject unsupported protocols like ftp:// and treat as search
        if (clean.startsWith("ftp://")) {
            clean = clean.substring(6);
        }

        // Check if user entered localhost or local IP or domain name
        if (clean.startsWith("localhost") || IPV4_PATTERN.matcher(clean).matches() || DOMAIN_PATTERN.matcher(clean).matches()) {
            return "http://" + clean;
        }

        // Default: Search query safely URL-encoded in UTF-8
        try {
            String encoded = URLEncoder.encode(clean, "UTF-8");
            String engine = (searchEngineUrl != null && !searchEngineUrl.isEmpty()) 
                    ? searchEngineUrl 
                    : "https://www.bing.com/search?q=";
            return engine + encoded;
        } catch (Exception e) {
            return "https://www.bing.com/search?q=" + clean;
        }
    }
}
