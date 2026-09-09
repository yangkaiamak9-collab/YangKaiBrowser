package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.ArrayList;
import java.util.List;

public class BookmarkManager {
    private final BrowserDatabaseHelper dbHelper;

    public static class BookmarkItem {
        public long id;
        public String title;
        public String url;
        public long createdAt;

        public BookmarkItem(long id, String title, String url, long createdAt) {
            this.id = id;
            this.title = title;
            this.url = url;
            this.createdAt = createdAt;
        }
    }

    public BookmarkManager(Context context) {
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public boolean addBookmark(String title, String url) {
        if (url == null || url.trim().isEmpty()) return false;
        String safeTitle = (title != null && !title.trim().isEmpty()) ? title.trim() : url;
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            c = db.query(BrowserDatabaseHelper.TABLE_BOOKMARKS, new String[]{"id"}, "url = ?", new String[]{url}, null, null, null);
            if (c != null && c.getCount() > 0) {
                return false; // Already bookmarked
            }
            ContentValues cv = new ContentValues();
            cv.put("title", safeTitle);
            cv.put("url", url);
            cv.put("created_at", System.currentTimeMillis());
            db.insert(BrowserDatabaseHelper.TABLE_BOOKMARKS, null, cv);
            return true;
        } catch (Exception e) {
            return false;
        } finally {
            if (c != null) c.close();
        }
    }

    public List<BookmarkItem> getAllBookmarks() {
        List<BookmarkItem> list = new ArrayList<BookmarkItem>();
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            c = db.rawQuery("SELECT id, title, url, created_at FROM " +
                    BrowserDatabaseHelper.TABLE_BOOKMARKS + " ORDER BY created_at DESC", null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new BookmarkItem(c.getLong(0), c.getString(1), c.getString(2), c.getLong(3)));
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.close();
        }
        return list;
    }

    public void deleteBookmark(long id) {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_BOOKMARKS, "id = ?", new String[]{String.valueOf(id)});
        } catch (Exception ignored) {}
    }
}
