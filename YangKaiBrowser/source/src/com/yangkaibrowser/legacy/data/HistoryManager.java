package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.ArrayList;
import java.util.List;

public class HistoryManager {
    private static final int MAX_HISTORY_ITEMS = 300;
    private final BrowserDatabaseHelper dbHelper;

    public static class HistoryEntry {
        public long id;
        public String url;
        public String title;
        public long timestamp;

        public HistoryEntry(long id, String url, String title, long timestamp) {
            this.id = id;
            this.url = url;
            this.title = title;
            this.timestamp = timestamp;
        }
    }

    public HistoryManager(Context context) {
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public void addEntry(String url, String title) {
        if (url == null || url.startsWith("file:///android_asset/")) return;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            ContentValues cv = new ContentValues();
            cv.put("url", url);
            cv.put("title", title != null ? title : url);
            cv.put("timestamp", System.currentTimeMillis());
            db.insert(BrowserDatabaseHelper.TABLE_HISTORY, null, cv);

            // Maintain max 300 items limit to prevent slow flash wear
            db.execSQL("DELETE FROM " + BrowserDatabaseHelper.TABLE_HISTORY +
                       " WHERE id NOT IN (SELECT id FROM " + BrowserDatabaseHelper.TABLE_HISTORY +
                       " ORDER BY timestamp DESC LIMIT " + MAX_HISTORY_ITEMS + ")");
        } catch (Exception ignored) {}
    }

    public List<HistoryEntry> getRecentEntries(int limit) {
        List<HistoryEntry> list = new ArrayList<HistoryEntry>();
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            c = db.rawQuery("SELECT id, url, title, timestamp FROM " +
                    BrowserDatabaseHelper.TABLE_HISTORY + " ORDER BY timestamp DESC LIMIT " + limit, null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new HistoryEntry(c.getLong(0), c.getString(1), c.getString(2), c.getLong(3)));
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.close();
        }
        return list;
    }

    public void clearAll() {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_HISTORY, null, null);
        } catch (Exception ignored) {}
    }
}
