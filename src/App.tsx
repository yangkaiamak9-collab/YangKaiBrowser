import React, { useState } from 'react';
import { Tv, Package, Code2, FileText, Download, ShieldCheck, Cpu, Archive } from 'lucide-react';
import { TvSimulator } from './components/TvSimulator';
import { ApkArtifactsView } from './components/ApkArtifactsView';
import { SourceCodeViewer } from './components/SourceCodeViewer';
import { DocsViewer } from './components/DocsViewer';
import { downloadBase64File } from './utils/apkDownloader';
import { YANG_KAI_RELEASE_APK_BASE64, YANG_KAI_RELEASE_ZIP_BASE64 } from './apkBase64';

export default function App() {
  const [activeTab, setActiveTab] = useState<'simulator' | 'artifacts' | 'source' | 'docs'>('artifacts');
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  const handleDownloadApk = () => {
    const ok = downloadBase64File(
      YANG_KAI_RELEASE_APK_BASE64,
      'YangKaiBrowser-release.apk',
      'application/vnd.android.package-archive'
    );
    if (ok) {
      setDownloadSuccess('تم بدء تنزيل ملف YangKaiBrowser-release.apk بنجاح!');
      setTimeout(() => setDownloadSuccess(null), 4000);
    }
  };

  const handleDownloadZip = () => {
    const ok = downloadBase64File(
      YANG_KAI_RELEASE_ZIP_BASE64,
      'YangKaiBrowser-release.zip',
      'application/zip'
    );
    if (ok) {
      setDownloadSuccess('تم بدء تنزيل ملف YangKaiBrowser-release.zip بنجاح!');
      setTimeout(() => setDownloadSuccess(null), 4000);
    }
  };

  return (
    <div className="min-h-screen bg-[#0E0E12] text-[#F0F0F2] font-sans flex flex-col">
      {/* Top Global Command Header */}
      <header className="border-b border-[#22222C] bg-[#14141A]/95 sticky top-0 z-50 backdrop-blur-md px-4 lg:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Brand Identity */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E5A93C] to-[#8B1E1E] flex items-center justify-center text-xl shadow-lg border border-[#FFD54F]/40">
              🐉
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-wider text-white">YANG KAI BROWSER</h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E5A93C] text-[#121214]">
                  v1.0.3
                </span>
              </div>
              <p className="text-xs text-gray-400">
                Hardware-Specific Autonomous Legacy TV Browser (Android 4.4.4 KitKat • API 19 • 512MB RAM)
              </p>
            </div>
          </div>

          {/* Quick Action Download Buttons */}
          <div className="flex items-center gap-2">
            <button
              id="top_download_apk_btn"
              onClick={handleDownloadApk}
              className="px-4 py-2 bg-gradient-to-r from-[#E5A93C] to-[#FFD54F] hover:brightness-110 active:scale-95 text-[#121214] text-xs font-black rounded-xl flex items-center gap-2 shadow-lg transition-all cursor-pointer"
              title="تحميل ملف الـ APK مباشرة لجهازك"
            >
              <Download className="w-4 h-4" />
              تحميل الـ APK الآن (62.6 KB)
            </button>
            <button
              id="top_download_zip_btn"
              onClick={handleDownloadZip}
              className="px-3 py-2 bg-[#22222E] hover:bg-[#2C2C3A] text-gray-300 text-xs font-semibold rounded-xl flex items-center gap-1.5 border border-[#3A3A4C] transition-all cursor-pointer"
              title="تحميل كملف مضغوط ZIP يحتوي على الـ APK"
            >
              <Archive className="w-3.5 h-3.5 text-[#FFD54F]" />
              تحميل ZIP
            </button>
          </div>
        </div>

        {/* Floating Download Success Toast */}
        {downloadSuccess && (
          <div className="max-w-7xl mx-auto mt-2 p-2 bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 rounded-lg text-xs font-bold text-center animate-bounce">
            ✓ {downloadSuccess} تفقد مجلد التنزيلات (Downloads) في جهازك.
          </div>
        )}

        {/* Sub-Header Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-3 pt-2 border-t border-[#20202A] flex gap-2">
          <button
            id="tab_nav_simulator"
            onClick={() => setActiveTab('simulator')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              activeTab === 'simulator'
                ? 'bg-[#E5A93C] text-[#121214]'
                : 'text-gray-400 hover:text-white hover:bg-[#1C1C26]'
            }`}
          >
            <Tv className="w-3.5 h-3.5" /> TV & Remote Simulator
          </button>

          <button
            id="tab_nav_artifacts"
            onClick={() => setActiveTab('artifacts')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              activeTab === 'artifacts'
                ? 'bg-[#E5A93C] text-[#121214]'
                : 'text-gray-400 hover:text-white hover:bg-[#1C1C26]'
            }`}
          >
            <Package className="w-3.5 h-3.5" /> Built APK & Hashes
          </button>

          <button
            id="tab_nav_source"
            onClick={() => setActiveTab('source')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              activeTab === 'source'
                ? 'bg-[#E5A93C] text-[#121214]'
                : 'text-gray-400 hover:text-white hover:bg-[#1C1C26]'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" /> Java Sources (SDK 19)
          </button>

          <button
            id="tab_nav_docs"
            onClick={() => setActiveTab('docs')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
              activeTab === 'docs'
                ? 'bg-[#E5A93C] text-[#121214]'
                : 'text-gray-400 hover:text-white hover:bg-[#1C1C26]'
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> Compatibility Docs
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8">
        {activeTab === 'simulator' && (
          <TvSimulator onDownloadApk={() => setActiveTab('artifacts')} />
        )}
        {activeTab === 'artifacts' && <ApkArtifactsView />}
        {activeTab === 'source' && <SourceCodeViewer />}
        {activeTab === 'docs' && <DocsViewer />}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#20202A] bg-[#121216] px-4 py-4 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-[#E5A93C] font-bold">YANG KAI BROWSER 🐉</span>
            <span>•</span>
            <span>Target: ARM Cortex-A7 (32-bit) Dual-Core</span>
            <span>•</span>
            <span>512 MB Physical RAM Target</span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>Release SHA-256: dda93ac18c...87af</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> Signed & Verified
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
