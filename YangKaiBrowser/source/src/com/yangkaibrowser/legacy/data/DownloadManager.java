package com.yangkaibrowser.legacy.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.AsyncTask;
import android.os.Environment;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class DownloadManager {
    private final Context context;
    private final BrowserDatabaseHelper dbHelper;
    private DownloadListener listener;

    public interface DownloadListener {
        void onDownloadProgress(long id, String filename, int progress, long bytesRead, long totalBytes);
        void onDownloadFinished(long id, String filename, boolean success, String errorMsg);
    }

    public static class DownloadItem {
        public long id;
        public String filename;
        public String url;
        public String filePath;
        public String mimeType;
        public long fileSize;
        public long downloadedBytes;
        public String status; // PENDING, DOWNLOADING, COMPLETED, FAILED, CANCELLED
        public long timestamp;

        public DownloadItem(long id, String filename, String url, String filePath, String mimeType, long fileSize, long downloadedBytes, String status, long timestamp) {
            this.id = id;
            this.filename = filename;
            this.url = url;
            this.filePath = filePath;
            this.mimeType = mimeType;
            this.fileSize = fileSize;
            this.downloadedBytes = downloadedBytes;
            this.status = status;
            this.timestamp = timestamp;
        }
    }

    public DownloadManager(Context context) {
        this.context = context;
        this.dbHelper = new BrowserDatabaseHelper(context);
    }

    public void setListener(DownloadListener listener) {
        this.listener = listener;
    }

    public long enqueueDownload(String downloadUrl, String filename, String mimeType, long estimatedSize) {
        if (downloadUrl == null || downloadUrl.isEmpty()) return -1;
        // Scheme validation: strictly http:// and https://
        if (!downloadUrl.startsWith("http://") && !downloadUrl.startsWith("https://")) {
            return -1;
        }

        String safeName = sanitizeFilename(filename, downloadUrl);
        File destDir = getDownloadDestinationDir();
        File targetFile = resolveUniqueFile(destDir, safeName);

        long id = -1;
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            ContentValues cv = new ContentValues();
            cv.put("filename", targetFile.getName());
            cv.put("url", downloadUrl);
            cv.put("filepath", targetFile.getAbsolutePath());
            cv.put("mimetype", mimeType != null ? mimeType : "application/octet-stream");
            cv.put("filesize", estimatedSize > 0 ? estimatedSize : 0);
            cv.put("downloaded_bytes", 0);
            cv.put("status", "QUEUED");
            cv.put("timestamp", System.currentTimeMillis());
            id = db.insert(BrowserDatabaseHelper.TABLE_DOWNLOADS, null, cv);
        } catch (Exception ignored) {}

        if (id > 0) {
            new DownloadTask(id, downloadUrl, targetFile).execute();
        }
        return id;
    }

    private File resolveUniqueFile(File dir, String filename) {
        File file = new File(dir, filename);
        if (!file.exists()) return file;
        String nameWithoutExt = filename;
        String ext = "";
        int dot = filename.lastIndexOf('.');
        if (dot > 0) {
            nameWithoutExt = filename.substring(0, dot);
            ext = filename.substring(dot);
        }
        int count = 1;
        while (file.exists() && count < 1000) {
            file = new File(dir, nameWithoutExt + " (" + count + ")" + ext);
            count++;
        }
        return file;
    }

    public List<DownloadItem> getAllDownloads() {
        List<DownloadItem> list = new ArrayList<DownloadItem>();
        Cursor c = null;
        try {
            SQLiteDatabase db = dbHelper.getReadableDatabase();
            c = db.rawQuery("SELECT id, filename, url, filepath, mimetype, filesize, downloaded_bytes, status, timestamp FROM " +
                    BrowserDatabaseHelper.TABLE_DOWNLOADS + " ORDER BY timestamp DESC", null);
            if (c != null) {
                while (c.moveToNext()) {
                    list.add(new DownloadItem(
                            c.getLong(0),
                            c.getString(1),
                            c.getString(2),
                            c.getString(3),
                            c.getString(4),
                            c.getLong(5),
                            c.getLong(6),
                            c.getString(7),
                            c.getLong(8)
                    ));
                }
            }
        } catch (Exception ignored) {
        } finally {
            if (c != null) c.close();
        }
        return list;
    }

    public void deleteDownload(long id) {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_DOWNLOADS, "id = ?", new String[]{String.valueOf(id)});
        } catch (Exception ignored) {}
    }

    public void clearAllDownloads() {
        try {
            SQLiteDatabase db = dbHelper.getWritableDatabase();
            db.delete(BrowserDatabaseHelper.TABLE_DOWNLOADS, null, null);
        } catch (Exception ignored) {}
    }

    private File getDownloadDestinationDir() {
        File dir = null;
        if (Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
            dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        }
        if (dir == null || (!dir.exists() && !dir.mkdirs())) {
            dir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        }
        if (dir == null) {
            dir = context.getFilesDir();
        }
        if (!dir.exists()) {
            dir.mkdirs();
        }
        return dir;
    }

    private String sanitizeFilename(String filename, String url) {
        String name = filename;
        if (name == null || name.trim().isEmpty()) {
            try {
                String path = new URL(url).getPath();
                int idx = path.lastIndexOf('/');
                if (idx >= 0 && idx < path.length() - 1) {
                    name = path.substring(idx + 1);
                }
            } catch (Exception ignored) {}
        }
        if (name == null || name.trim().isEmpty()) {
            name = "download_" + System.currentTimeMillis() + ".bin";
        }
        // Remove control characters, quotes, slashes, backslashes, path traversal
        name = name.replaceAll("[\\p{Cntrl}\\\\/:*?\"<>|]", "_").replace("..", "_").trim();
        if (name.length() > 64) {
            int dot = name.lastIndexOf('.');
            if (dot > 0 && dot < name.length() - 1) {
                String ext = name.substring(dot);
                name = name.substring(0, Math.min(dot, 56)) + ext;
            } else {
                name = name.substring(0, 64);
            }
        }
        return name.isEmpty() ? ("download_" + System.currentTimeMillis() + ".bin") : name;
    }

    private class DownloadTask extends AsyncTask<Void, Integer, Boolean> {
        private final long downloadId;
        private final String downloadUrl;
        private final File targetFile;
        private String errorMessage = "";
        private long totalBytes = 0;
        private long bytesRead = 0;

        public DownloadTask(long downloadId, String downloadUrl, File targetFile) {
            this.downloadId = downloadId;
            this.downloadUrl = downloadUrl;
            this.targetFile = targetFile;
        }

        @Override
        protected Boolean doInBackground(Void... params) {
            HttpURLConnection conn = null;
            InputStream in = null;
            FileOutputStream out = null;
            File tmpFile = new File(targetFile.getAbsolutePath() + ".tmp");

            try {
                String currentUrl = downloadUrl;
                int redirects = 0;
                while (redirects < 5) {
                    URL u = new URL(currentUrl);
                    conn = (HttpURLConnection) u.openConnection();
                    conn.setConnectTimeout(15000);
                    conn.setReadTimeout(30000);
                    conn.setRequestProperty("User-Agent", "YangKaiBrowser/1.0.1 (Android 4.4.4; D-Pad TV Box)");
                    conn.setInstanceFollowRedirects(false); // Manual handling for cross-protocol redirects
                    conn.connect();

                    int code = conn.getResponseCode();
                    if (code == HttpURLConnection.HTTP_MOVED_PERM || code == HttpURLConnection.HTTP_MOVED_TEMP ||
                        code == HttpURLConnection.HTTP_SEE_OTHER || code == 307 || code == 308) {
                        String newLoc = conn.getHeaderField("Location");
                        conn.disconnect();
                        if (newLoc == null || newLoc.isEmpty()) {
                            errorMessage = "Redirect without Location header";
                            return false;
                        }
                        if (!newLoc.startsWith("http://") && !newLoc.startsWith("https://")) {
                            URL base = new URL(currentUrl);
                            newLoc = new URL(base, newLoc).toString();
                        }
                        currentUrl = newLoc;
                        redirects++;
                    } else {
                        break;
                    }
                }

                int code = conn.getResponseCode();
                if (code < 200 || code >= 300) {
                    errorMessage = "HTTP " + code + ": " + conn.getResponseMessage();
                    return false;
                }

                totalBytes = conn.getContentLength();
                in = conn.getInputStream();
                out = new FileOutputStream(tmpFile);

                // Strictly 8KB streaming buffer - zero risk of OOM on 512MB RAM
                byte[] buffer = new byte[8192];
                int n;
                long lastProgressUpdate = 0;

                while ((n = in.read(buffer)) != -1) {
                    if (isCancelled()) {
                        errorMessage = "Cancelled by user";
                        tmpFile.delete();
                        return false;
                    }
                    out.write(buffer, 0, n);
                    bytesRead += n;

                    long now = System.currentTimeMillis();
                    if (now - lastProgressUpdate > 500) {
                        int pct = totalBytes > 0 ? (int) ((bytesRead * 100) / totalBytes) : 0;
                        publishProgress(pct);
                        lastProgressUpdate = now;
                    }
                }
                out.flush();
                out.close();
                out = null;

                // Atomic rename of .tmp to final destination targetFile
                if (tmpFile.renameTo(targetFile)) {
                    return true;
                } else {
                    errorMessage = "Failed to finalize downloaded file";
                    tmpFile.delete();
                    return false;
                }

            } catch (Exception e) {
                errorMessage = e.getMessage() != null ? e.getMessage() : "Network error during download";
                if (tmpFile.exists()) {
                    tmpFile.delete();
                }
                return false;
            } finally {
                try { if (in != null) in.close(); } catch (Exception ignored) {}
                try { if (out != null) out.close(); } catch (Exception ignored) {}
                if (conn != null) conn.disconnect();
            }
        }

        @Override
        protected void onProgressUpdate(Integer... values) {
            int pct = values[0];
            if (listener != null) {
                listener.onDownloadProgress(downloadId, targetFile.getName(), pct, bytesRead, totalBytes);
            }
        }

        @Override
        protected void onPostExecute(Boolean success) {
            String status = success ? "COMPLETED" : "FAILED";
            try {
                SQLiteDatabase db = dbHelper.getWritableDatabase();
                ContentValues cv = new ContentValues();
                cv.put("status", status);
                cv.put("downloaded_bytes", bytesRead);
                if (totalBytes > 0) cv.put("filesize", totalBytes);
                db.update(BrowserDatabaseHelper.TABLE_DOWNLOADS, cv, "id = ?", new String[]{String.valueOf(downloadId)});
            } catch (Exception ignored) {}

            if (listener != null) {
                listener.onDownloadFinished(downloadId, targetFile.getName(), success, errorMessage);
            }
        }
    }
}
