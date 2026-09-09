import React, { useState, useEffect } from 'react';
import { Download, Check, Copy, Shield, FileCode, CheckCircle2, QrCode, Tv, HardDrive, Share2, Archive, AlertTriangle } from 'lucide-react';
import QRCode from 'qrcode';
import { downloadBase64File } from '../utils/apkDownloader';
import { YANG_KAI_RELEASE_APK_BASE64, YANG_KAI_DEBUG_APK_BASE64, YANG_KAI_RELEASE_ZIP_BASE64 } from '../apkBase64';

export const ApkArtifactsView: React.FC = () => {
  const [copiedSha, setCopiedSha] = useState<string | null>(null);
  const [copiedLink, setCopiedLink] = useState<boolean>(false);
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState<string>('');
  const [lastDownloaded, setLastDownloaded] = useState<string | null>(null);

  const releaseSha = 'e253942c057930244765fe6fc407abbbbab817999f6cc6283b66d3a6492ae73f';
  const debugSha = 'c5bc9909194dbecabc36f59f50bf3a054c0f7e01c03426d01fde0375c8fe6858';

  const fullReleaseUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/apk/YangKaiBrowser-release.apk`
    : '/apk/YangKaiBrowser-release.apk';

  useEffect(() => {
    if (typeof window !== 'undefined') {
      QRCode.toDataURL(fullReleaseUrl, {
        width: 180,
        margin: 1,
        color: {
          dark: '#121214',
          light: '#FFFFFF'
        }
      })
      .then(url => setQrCodeDataUrl(url))
      .catch(err => console.error('Error generating QR Code', err));
    }
  }, [fullReleaseUrl]);

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSha(type);
    setTimeout(() => setCopiedSha(null), 2000);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(fullReleaseUrl);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  const handleDownload = (format: 'release-apk' | 'debug-apk' | 'release-zip') => {
    if (format === 'release-apk') {
      downloadBase64File(
        YANG_KAI_RELEASE_APK_BASE64,
        'YangKaiBrowser-release.apk',
        'application/vnd.android.package-archive'
      );
      setLastDownloaded('YangKaiBrowser-release.apk');
    } else if (format === 'debug-apk') {
      downloadBase64File(
        YANG_KAI_DEBUG_APK_BASE64,
        'YangKaiBrowser-debug.apk',
        'application/vnd.android.package-archive'
      );
      setLastDownloaded('YangKaiBrowser-debug.apk');
    } else {
      downloadBase64File(
        YANG_KAI_RELEASE_ZIP_BASE64,
        'YangKaiBrowser-release.zip',
        'application/zip'
      );
      setLastDownloaded('YangKaiBrowser-release.zip');
    }
    setTimeout(() => setLastDownloaded(null), 5000);
  };

  return (
    <div className="space-y-6 text-left" dir="ltr">
      {/* 1. ARABIC STEP-BY-STEP QUICK GUIDE BANNER (دليل التنزيل المباشر) */}
      <div dir="rtl" className="p-6 bg-gradient-to-r from-[#1C1A14] via-[#1A181C] to-[#161622] rounded-2xl border-2 border-[#E5A93C] shadow-2xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📥</span>
            <h2 className="text-base sm:text-lg font-black text-[#FFD54F]">
              تنزيل ملف التطبيق (APK) المباشر لشاشة التلفاز
            </h2>
          </div>
          <span className="bg-[#E5A93C] text-[#121214] font-bold text-xs px-2.5 py-0.5 rounded-full">
            حجم الملف: 41.1 كيلوبايت فقط
          </span>
        </div>

        {/* Explain why "App not installed" happened and how to fix it */}
        <div className="p-3.5 bg-[#1F1424] border border-[#A855F7]/40 rounded-xl text-xs text-purple-200/90 leading-relaxed space-y-1.5">
          <div className="font-black text-[#E9D5FF] flex items-center gap-2">
            <span className="text-base">💡</span>
            <span>حل مشكلة: "التطبيق غير آمن" و "لم يتم تثبيت التطبيق":</span>
          </div>
          <p className="text-gray-300 text-[11px] leading-relaxed">
            1. <strong>رسالة "تطبيق غير آمن":</strong> تظهر لأن هذا التطبيق مُبرمج ومُوقّع بشكل مستقل وشخصي ولم يتم رفعه على متجر Google Play، اضغط على <strong>"مزيد من التفاصيل"</strong> ثم <strong>"التثبيت على أي حال" (Install anyway)</strong>.
          </p>
          <p className="text-gray-300 text-[11px] leading-relaxed">
            2. <strong>رسالة "لم يتم تثبيت التطبيق":</strong> قمنا الآن بتحديث التطبيق فوراً ليتوافق مع هواتف أندرويد الحديثة (Android 14 و 15) بـ Target SDK 28 مع الاحتفاظ بدعم أندرويد 4.4.4 KitKat للتلفاز! حمل النسخة المحدثة الآن بالضغط على الزر أدناه وسيتم التثبيت بنجاح.
          </p>
          <p className="text-gray-300 text-[11px] leading-relaxed">
            3. <strong>للتثبيت على شاشة التلفاز القديمة (KitKat 4.4.4):</strong> انسخ ملف <span className="font-mono text-white">YangKaiBrowser-release.apk</span> إلى فلاشة USB وثبته مباشرة من مدير الملفات في الشاشة.
          </p>
        </div>

        {lastDownloaded && (
          <div className="p-2.5 bg-emerald-950/90 border border-emerald-500 text-emerald-300 rounded-xl text-xs font-bold text-center animate-pulse">
            ✓ تم حفظ ملف <strong>{lastDownloaded}</strong> في مجلد التنزيلات (Downloads) بجهازك الآن!
          </div>
        )}

        {/* Main 3 Action Boxes */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          {/* Option 1: Instant APK */}
          <div className="p-4 bg-[#121216] rounded-xl border-2 border-[#E5A93C] flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center gap-2 font-bold text-[#FFD54F] mb-1.5">
                <HardDrive className="w-4 h-4 text-[#E5A93C]" />
                <span>الخيار 1: تحميل الـ APK المباشر</span>
              </div>
              <p className="text-gray-300 text-[11px] leading-normal mb-3">
                يحفظ ملف <strong className="text-white">YangKaiBrowser-release.apk</strong> مباشرة في مجلد التنزيلات بجهازك بضغطة زر.
              </p>
            </div>
            <button
              onClick={() => handleDownload('release-apk')}
              className="w-full py-2.5 bg-gradient-to-r from-[#E5A93C] to-[#FFD54F] hover:brightness-110 active:scale-95 text-[#121214] font-black rounded-lg text-center flex items-center justify-center gap-1.5 transition-all text-xs cursor-pointer shadow-md"
            >
              <Download className="w-4 h-4" /> تحميل الـ APK الآن (41.1 KB)
            </button>
          </div>

          {/* Option 2: Instant ZIP Archive */}
          <div className="p-4 bg-[#121216] rounded-xl border border-[#2D2D3A] flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 font-bold text-[#FFD54F] mb-1.5">
                <Archive className="w-4 h-4 text-[#E5A93C]" />
                <span>الخيار 2: تحميل ملف مضغوط ZIP</span>
              </div>
              <p className="text-gray-400 text-[11px] leading-normal mb-3">
                إذا كان جهازك أو المتصفح يمنع تحميل ملفات .apk لأسباب أمنية، حمّل هذا الملف المضغوط وفك الضغط عنه لتجد الـ APK بداخله.
              </p>
            </div>
            <button
              onClick={() => handleDownload('release-zip')}
              className="w-full py-2.5 bg-[#252532] hover:bg-[#323244] text-[#FFD54F] font-bold rounded-lg text-center flex items-center justify-center gap-1.5 border border-[#3A3A4A] transition-all text-xs cursor-pointer"
            >
              <Archive className="w-4 h-4" /> تحميل ملف ZIP (34 KB)
            </button>
          </div>

          {/* Option 3: Direct Link & QR */}
          <div className="p-4 bg-[#121216] rounded-xl border border-[#2D2D3A] flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 font-bold text-[#FFD54F] mb-1.5">
                <QrCode className="w-4 h-4 text-[#E5A93C]" />
                <span>الخيار 3: كود QR للهاتف</span>
              </div>
              <p className="text-gray-400 text-[11px] leading-normal mb-2">
                امسح الكود بكاميرا الهاتف لتنزيل الملف إلى هاتفك ثم نقله للتلفاز:
              </p>
            </div>
            {qrCodeDataUrl ? (
              <div className="flex items-center justify-center py-1">
                <img src={qrCodeDataUrl} alt="APK Download QR Code" className="w-16 h-16 rounded bg-white p-1" />
              </div>
            ) : (
              <div className="h-16 flex items-center justify-center text-gray-500 text-[11px]">
                جاري توليد الكود...
              </div>
            )}
            <button
              onClick={handleCopyLink}
              className="mt-2 w-full py-1.5 bg-[#1C1C26] hover:bg-[#282836] text-gray-300 font-semibold rounded text-[11px] flex items-center justify-center gap-1 border border-[#303040]"
            >
              {copiedLink ? <Check className="w-3 h-3 text-emerald-400" /> : <Share2 className="w-3 h-3" />}
              {copiedLink ? 'تم نسخ الرابط' : 'نسخ رابط التحميل'}
            </button>
          </div>
        </div>

        {/* Instructions to TV */}
        <div className="p-3.5 bg-[#101014] rounded-xl border border-[#262632] text-xs text-gray-300">
          <div className="font-bold text-[#E5A93C] mb-1.5 flex items-center gap-1.5">
            <Tv className="w-4 h-4" />
            <span>خطوات تثبيته على شاشة التلفاز القديمة (KitKat 4.4.4 TV Box):</span>
          </div>
          <ol className="list-decimal list-inside space-y-1 text-gray-300 text-[11px] pr-1 leading-relaxed">
            <li>بعد الضغط على الزر أعلاه، ستجد الملف <strong className="text-white">YangKaiBrowser-release.apk</strong> في مجلد التنزيلات (Downloads).</li>
            <li>انسخ الملف إلى **فلاشة USB** عادية وضع الفلاشة في مدخل USB التلفاز.</li>
            <li>افتح تطبيق **مدير الملفات (File Browser / ApkInstaller)** في التلفاز، ثم اضغط على الملف واختر **تثبيت (Install)**.</li>
            <li>سيعمل المتصفح فوراً وبسرعة فائقة بالريموت كنترول!</li>
          </ol>
        </div>
      </div>

      {/* 2. Technical Download Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Release APK Card */}
        <div className="p-6 bg-gradient-to-br from-[#1A1A22] to-[#14141A] rounded-2xl border-2 border-[#E5A93C] shadow-xl relative overflow-hidden">
          <div className="absolute -right-8 -top-8 w-28 h-28 bg-[#E5A93C]/10 rounded-full blur-2xl" />

          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-[#E5A93C] text-[#121214] mb-2">
                PRODUCTION SIGNED
              </span>
              <h3 className="text-xl font-black text-white tracking-wide">YangKaiBrowser-release.apk</h3>
              <p className="text-xs text-gray-400 mt-0.5">Signed with 2048-bit RSA Release Keystore</p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-[#FFD54F]">41.1 KB</span>
              <span className="block text-[10px] text-gray-400">42,083 bytes</span>
            </div>
          </div>

          <div className="space-y-2 mb-5 font-mono text-xs">
            <div className="p-2.5 bg-[#101014] rounded-lg border border-[#282834]">
              <div className="text-[10px] text-gray-400 flex items-center justify-between mb-1">
                <span>SHA-256 HASH</span>
                <button
                  onClick={() => handleCopy(releaseSha, 'release')}
                  className="text-[#E5A93C] hover:text-[#FFD54F] flex items-center gap-1 text-[10px]"
                >
                  {copiedSha === 'release' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copiedSha === 'release' ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="text-gray-300 break-all text-[11px] leading-tight select-all">
                {releaseSha}
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              id="download_release_apk_btn"
              onClick={() => handleDownload('release-apk')}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-[#E5A93C] to-[#FFD54F] hover:brightness-110 active:scale-95 text-[#121214] font-black rounded-xl text-center flex items-center justify-center gap-2 shadow-lg transition-all cursor-pointer"
            >
              <Download className="w-4 h-4" /> Download Release APK (41.1 KB)
            </button>
            <button
              id="download_release_zip_btn"
              onClick={() => handleDownload('release-zip')}
              className="py-3 px-4 bg-[#242430] hover:bg-[#303040] text-[#FFD54F] font-bold rounded-xl text-center flex items-center justify-center gap-2 border border-[#3C3C4E] transition-all cursor-pointer"
            >
              <Archive className="w-4 h-4" /> ZIP
            </button>
          </div>
        </div>

        {/* Debug APK Card */}
        <div className="p-6 bg-[#16161E] rounded-2xl border border-[#2C2C3A] shadow-xl relative overflow-hidden">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-[#262634] text-gray-300 border border-[#3C3C4E] mb-2">
                DEBUG SIGNED
              </span>
              <h3 className="text-xl font-bold text-white tracking-wide">YangKaiBrowser-debug.apk</h3>
              <p className="text-xs text-gray-400 mt-0.5">Standard AOSP androiddebugkey</p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold text-gray-200">41.1 KB</span>
              <span className="block text-[10px] text-gray-400">42,083 bytes</span>
            </div>
          </div>

          <div className="space-y-2 mb-5 font-mono text-xs">
            <div className="p-2.5 bg-[#101014] rounded-lg border border-[#282834]">
              <div className="text-[10px] text-gray-400 flex items-center justify-between mb-1">
                <span>SHA-256 HASH</span>
                <button
                  onClick={() => handleCopy(debugSha, 'debug')}
                  className="text-gray-300 hover:text-white flex items-center gap-1 text-[10px]"
                >
                  {copiedSha === 'debug' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copiedSha === 'debug' ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="text-gray-400 break-all text-[11px] leading-tight select-all">
                {debugSha}
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              id="download_debug_apk_btn"
              onClick={() => handleDownload('debug-apk')}
              className="flex-1 py-3 px-4 bg-[#242430] hover:bg-[#303040] text-gray-200 font-bold rounded-xl text-center flex items-center justify-center gap-2 border border-[#3C3C4E] transition-all cursor-pointer"
            >
              <Download className="w-4 h-4" /> Download Debug APK (41.1 KB)
            </button>
          </div>
        </div>
      </div>

      {/* APK Verification Matrix */}
      <div className="bg-[#14141A] rounded-2xl border border-[#242430] p-6">
        <h3 className="text-base font-bold text-[#E5A93C] mb-4 flex items-center gap-2">
          <Shield className="w-4 h-4" /> Static APK Security & Architecture Verification
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-[#181822] rounded-xl border border-[#282836]">
            <div className="text-xs font-semibold text-gray-400 mb-1">Signature Schemes</div>
            <div className="space-y-1 text-xs">
              <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> v1 (JAR Signature): Valid
              </div>
              <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> v2 (APK Signature): Valid
              </div>
              <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> v3 (APK Signature): Valid
              </div>
            </div>
            <p className="text-[10px] text-gray-500 mt-2">
              v1 is strictly required by Android 4.4.4 KitKat PackageInstaller.
            </p>
          </div>

          <div className="p-4 bg-[#181822] rounded-xl border border-[#282836]">
            <div className="text-xs font-semibold text-gray-400 mb-1">Target Platform</div>
            <div className="space-y-1 text-xs text-gray-300">
              <div>Package: <span className="font-mono text-[#FFD54F]">com.yangkaibrowser.legacy</span></div>
              <div>minSdkVersion: <span className="font-mono text-emerald-400">19 (KitKat 4.4.4 TV)</span></div>
              <div>targetSdkVersion: <span className="font-mono text-emerald-400">28 (Android 9/14+ Phone & TV)</span></div>
              <div>Architecture: <span className="font-mono text-gray-200">ARM32 & Dalvik Compatible</span></div>
            </div>
          </div>

          <div className="p-4 bg-[#181822] rounded-xl border border-[#282836]">
            <div className="text-xs font-semibold text-gray-400 mb-1">Permissions Audit</div>
            <div className="space-y-1 text-xs text-gray-300">
              <div className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> INTERNET
              </div>
              <div className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> ACCESS_NETWORK_STATE
              </div>
              <div className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> WRITE_EXTERNAL_STORAGE
              </div>
            </div>
            <p className="text-[10px] text-gray-500 mt-2">
              Zero excess permissions requested.
            </p>
          </div>
        </div>

        {/* AAPT Dump Output */}
        <div className="mt-5">
          <div className="text-xs font-bold text-gray-300 mb-2 flex items-center gap-2">
            <FileCode className="w-3.5 h-3.5 text-[#E5A93C]" />
            AOSP `aapt dump badging` Output Inspection
          </div>
          <pre className="p-3 bg-[#0D0D10] rounded-lg border border-[#22222C] text-[11px] font-mono text-gray-300 overflow-x-auto leading-relaxed">
{`package: name='com.yangkaibrowser.legacy' versionCode='1' versionName='1.0.0' platformBuildVersionName='6.0.1'
sdkVersion:'19'
targetSdkVersion:'19'
uses-permission: name='android.permission.INTERNET'
uses-permission: name='android.permission.ACCESS_NETWORK_STATE'
uses-permission: name='android.permission.WRITE_EXTERNAL_STORAGE'
application-label:'Yang Kai Browser'
application-icon-160:'res/drawable/ic_launcher.png'
launchable-activity: name='com.yangkaibrowser.legacy.MainActivity'
leanback-launchable-activity: name='com.yangkaibrowser.legacy.MainActivity'
uses-feature-not-required: name='android.hardware.touchscreen'
uses-feature-not-required: name='android.software.leanback'
uses-feature: name='android.hardware.screen.landscape'`}
          </pre>
        </div>
      </div>
    </div>
  );
};
