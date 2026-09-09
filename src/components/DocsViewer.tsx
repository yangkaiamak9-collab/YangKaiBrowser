import React, { useState } from 'react';
import { BookOpen, Terminal, CheckCircle2, ShieldAlert } from 'lucide-react';

export const DocsViewer: React.FC = () => {
  const [activeDoc, setActiveDoc] = useState<'compat' | 'install' | 'arch' | 'test'>('compat');

  return (
    <div className="space-y-5 text-left">
      {/* Navigation tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#242430] pb-3">
        <button
          onClick={() => setActiveDoc('compat')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeDoc === 'compat'
              ? 'bg-[#E5A93C] text-[#121214]'
              : 'bg-[#181822] text-gray-400 hover:text-white border border-[#282836]'
          }`}
        >
          COMPATIBILITY.md
        </button>

        <button
          onClick={() => setActiveDoc('install')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeDoc === 'install'
              ? 'bg-[#E5A93C] text-[#121214]'
              : 'bg-[#181822] text-gray-400 hover:text-white border border-[#282836]'
          }`}
        >
          INSTALLATION.md
        </button>

        <button
          onClick={() => setActiveDoc('arch')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeDoc === 'arch'
              ? 'bg-[#E5A93C] text-[#121214]'
              : 'bg-[#181822] text-gray-400 hover:text-white border border-[#282836]'
          }`}
        >
          ARCHITECTURE.md
        </button>

        <button
          onClick={() => setActiveDoc('test')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeDoc === 'test'
              ? 'bg-[#E5A93C] text-[#121214]'
              : 'bg-[#181822] text-gray-400 hover:text-white border border-[#282836]'
          }`}
        >
          TEST_REPORT.md
        </button>
      </div>

      {/* Doc Contents */}
      <div className="p-6 bg-[#14141A] rounded-2xl border border-[#242430] space-y-4 text-xs text-gray-300 leading-relaxed">
        {activeDoc === 'compat' && (
          <div>
            <h2 className="text-base font-bold text-[#E5A93C] mb-3">Hardware & Runtime Compatibility Report</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
              <div className="p-3 bg-[#1C1C26] rounded-lg border border-[#2D2D3C]">
                <div className="font-bold text-white mb-1">Android OS Compatibility</div>
                <p className="text-gray-400">Strictly targets API 19 (Android 4.4.4 KitKat). Uses no APIs introduced in Lollipop (21) or later.</p>
              </div>
              <div className="p-3 bg-[#1C1C26] rounded-lg border border-[#2D2D3C]">
                <div className="font-bold text-white mb-1">ARM32 Architecture</div>
                <p className="text-gray-400">Compiled into standard Dalvik bytecode (`classes.dex`) running on 32-bit ARM Cortex-A7 processors.</p>
              </div>
              <div className="p-3 bg-[#1C1C26] rounded-lg border border-[#2D2D3C]">
                <div className="font-bold text-white mb-1">512 MB RAM Envelope</div>
                <p className="text-gray-400">Max 3 tabs with auto-eviction under memory pressure, keeping resident heap below 24MB.</p>
              </div>
              <div className="p-3 bg-[#1C1C26] rounded-lg border border-[#2D2D3C]">
                <div className="font-bold text-white mb-1">Physical Device Sideload Status</div>
                <p className="text-emerald-400">NOT YET VERIFIED on physical hardware (cloud container environment). Static binary verified.</p>
              </div>
            </div>
          </div>
        )}

        {activeDoc === 'install' && (
          <div>
            <h2 className="text-base font-bold text-[#E5A93C] mb-3">Installation Instructions (ADB & USB)</h2>
            <div className="space-y-3 font-mono">
              <div className="p-3 bg-[#0E0E12] rounded-lg border border-[#20202A]">
                <div className="text-[#FFD54F] font-bold text-xs mb-1">ADB Direct Install</div>
                <div className="text-gray-300">adb connect 192.168.1.xxx:5555</div>
                <div className="text-gray-300">adb install -r YangKaiBrowser-release.apk</div>
                <div className="text-gray-300">adb shell am start -n com.yangkaibrowser.legacy/.MainActivity</div>
              </div>
              <div className="p-3 bg-[#0E0E12] rounded-lg border border-[#20202A]">
                <div className="text-[#FFD54F] font-bold text-xs mb-1">USB Flash Drive Sideload</div>
                <div className="text-gray-400 text-xs font-sans">
                  1. Copy `YangKaiBrowser-release.apk` to FAT32 USB drive.<br/>
                  2. Connect to TV Box USB port and open File Browser.<br/>
                  3. Enable 'Unknown Sources' in TV Settings.<br/>
                  4. Select APK to install.
                </div>
              </div>
            </div>
          </div>
        )}

        {activeDoc === 'arch' && (
          <div>
            <h2 className="text-base font-bold text-[#E5A93C] mb-3">Architectural Highlights</h2>
            <ul className="space-y-2 list-disc pl-4 text-gray-300">
              <li><strong className="text-white">Zero Third-Party Dependencies:</strong> Built with pure Android SDK 19 classes without Jetpack, Kotlin stdlib, or heavy libraries.</li>
              <li><strong className="text-white">Dalvik Heap Protection:</strong> MemoryManager polls totalMemory and freeMemory, notifying TabManager to destroy background WebViews when heap saturation reaches 78%.</li>
              <li><strong className="text-white">Virtual Cursor Layer:</strong> CursorManager dispatches synthetic MotionEvent ACTION_DOWN and ACTION_UP pairs directly to the WebView for desktop-only sites.</li>
              <li><strong className="text-white">Zero-ORM SQLite:</strong> Direct SQLiteOpenHelper statements for bookmarks and history avoid reflection memory spikes.</li>
            </ul>
          </div>
        )}

        {activeDoc === 'test' && (
          <div>
            <h2 className="text-base font-bold text-[#E5A93C] mb-3">Verification & Static Test Matrix</h2>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" /> Java 7 Dalvik Bytecode: PASS
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" /> Android 4.4.4 KitKat v1 JAR Signature: PASS
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" /> 4-Byte ZipAlign Boundary: PASS
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" /> Leanback TV Launcher Category: PASS
              </div>
              <div className="flex items-center gap-2 text-amber-300">
                <ShieldAlert className="w-4 h-4" /> Physical Hardware Flash (TTX-V005): Ready for Sideload
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
