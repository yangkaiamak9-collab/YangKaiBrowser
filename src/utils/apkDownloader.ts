// Client-side instant binary downloader using Base64 Blobs
// Completely avoids server errors, cookies, auth walls, and MIME type browser text dumps.

export function downloadBase64File(base64Data: string, filename: string, mimeType: string): boolean {
  try {
    const binaryString = window.atob(base64Data);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      if (document.body.contains(a)) {
        document.body.removeChild(a);
      }
      URL.revokeObjectURL(url);
    }, 2000);
    return true;
  } catch (err) {
    console.error('Download error:', err);
    return false;
  }
}
