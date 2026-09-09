package com.yangkaibrowser.legacy.data;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class BrowserDatabaseHelper extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "yangkai_browser.db";
    private static final int DATABASE_VERSION = 2;

    public static final String TABLE_HISTORY = "history";
    public static final String TABLE_BOOKMARKS = "bookmarks";
    public static final String TABLE_DOWNLOADS = "downloads";

    public BrowserDatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE " + TABLE_HISTORY + " ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "url TEXT NOT NULL, "
                + "title TEXT, "
                + "timestamp INTEGER NOT NULL);");

        db.execSQL("CREATE TABLE " + TABLE_BOOKMARKS + " ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "title TEXT NOT NULL, "
                + "url TEXT NOT NULL, "
                + "created_at INTEGER NOT NULL);");

        db.execSQL("CREATE TABLE " + TABLE_DOWNLOADS + " ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "filename TEXT NOT NULL, "
                + "url TEXT, "
                + "filepath TEXT, "
                + "mimetype TEXT, "
                + "filesize INTEGER, "
                + "downloaded_bytes INTEGER, "
                + "status TEXT, "
                + "timestamp INTEGER NOT NULL);");

        // Indices for fast lookups on slow flash memory
        db.execSQL("CREATE INDEX idx_history_timestamp ON " + TABLE_HISTORY + "(timestamp DESC);");
        db.execSQL("CREATE INDEX idx_bookmarks_url ON " + TABLE_BOOKMARKS + "(url);");
        db.execSQL("CREATE INDEX idx_downloads_timestamp ON " + TABLE_DOWNLOADS + "(timestamp DESC);");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_HISTORY);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_BOOKMARKS);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_DOWNLOADS);
        onCreate(db);
    }
}
