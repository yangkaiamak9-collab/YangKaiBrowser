import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  RotateCw,
  Home,
  MousePointer,
  Compass,
  Menu as MenuIcon,
  Layers,
  Activity,
  AlertTriangle,
  CheckCircle,
  Database,
  Cpu,
  Trash2,
  Tv,
  ExternalLink,
  ShieldCheck,
  Search
} from 'lucide-react';
import type { TabItem, MemoryState, KeyLog } from '../types';

interface TvSimulatorProps {
  onDownloadApk: () => void;
}

export const TvSimulator: React.FC<TvSimulatorProps> = ({ onDownloadApk }) => {
  // Tabs State (Max 3 tabs enforced)
  const [tabs, setTabs] = useState<TabItem[]>([
    {
      id: 'tab-1',
      url: 'file:///android_asset/homepage.html',
      title: 'Yang Kai Home',
      isEvicted: false,
      history: ['file:///android_asset/homepage.html'],
      historyIndex: 0,
    }
  ]);
  const [activeTabIndex, setActiveTabIndex] = useState<number>(0);
  const [addressInput, setAddressInput] = useState<string>('file:///android_asset/homepage.html');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);

  // Virtual Cursor State
  const [isCursorMode, setIsCursorMode] = useState<boolean>(false);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 320, y: 200 });
  const [cursorSpeed] = useState<number>(25);

  // TV D-Pad Focus state (which toolbar element is focused)
  const [focusedToolbarIndex, setFocusedToolbarIndex] = useState<number>(4); // 4 = Address bar

  // Memory & Heap Simulation
  const [usedHeapMB, setUsedHeapMB] = useState<number>(18);
  const maxHeapMB = 128;
  const memoryState: MemoryState =
    usedHeapMB > 110 ? 'EMERGENCY' :
    usedHeapMB > 98 ? 'CRITICAL' :
    usedHeapMB > 80 ? 'WARNING' : 'NORMAL';

  // Remote Key Event Log
  const [lastEvent, setLastEvent] = useState<KeyLog>({
    name: 'KEYCODE_DPAD_CENTER',
    keyCode: 23,
    action: 'ACTION_DOWN',
    time: 'Ready',
  });
  const [showForensicsOverlay, setShowForensicsOverlay] = useState<boolean>(false);

  // Dialog Modals
  const [activeModal, setActiveModal] = useState<'menu' | 'tabs' | 'history' | 'bookmarks' | 'diagnostics' | 'exit' | null>(null);

  // History & Bookmarks stored locally
  const [bookmarks, setBookmarks] = useState<{ title: string; url: string }[]>([
    { title: 'DuckDuckGo Lite', url: 'https://html.duckduckgo.com/html/' },
    { title: 'Wikipedia Mobile', url: 'https://en.m.wikipedia.org' },
    { title: 'Internet Archive', url: 'https://archive.org' }
  ]);
  const [historyList, setHistoryList] = useState<{ title: string; url: string; time: string }[]>([
    { title: 'Yang Kai Home', url: 'file:///android_asset/homepage.html', time: '14:20' }
  ]);

  const tvScreenRef = useRef<HTMLDivElement>(null);
  const currentTab = tabs[activeTabIndex] || tabs[0];

  // Auto-evict inactive tabs if memory reaches CRITICAL or EMERGENCY
  useEffect(() => {
    if (memoryState === 'CRITICAL' || memoryState === 'EMERGENCY') {
      setTabs(prev =>
        prev.map((t, idx) =>
          idx !== activeTabIndex ? { ...t, isEvicted: true } : t
        )
      );
    }
  }, [memoryState, activeTabIndex]);

  // Handle URL navigation
  const navigateTo = (targetUrl: string, title?: string) => {
    let resolved = targetUrl.trim();
    if (!resolved) resolved = 'file:///android_asset/homepage.html';
    else if (resolved.toLowerCase() === 'home' || resolved === 'about:blank') {
      resolved = 'file:///android_asset/homepage.html';
    } else if (!resolved.startsWith('http://') && !resolved.startsWith('https://') && !resolved.startsWith('file:///')) {
      if (resolved.includes('.') && !resolved.includes(' ')) {
        resolved = 'https://' + resolved;
      } else {
        resolved = 'https://html.duckduckgo.com/html/?q=' + encodeURIComponent(resolved);
      }
    }

    setIsLoading(true);
    setProgress(30);
    setAddressInput(resolved);

    setTimeout(() => {
      setProgress(75);
      setTimeout(() => {
        setIsLoading(false);
        setProgress(100);
        setTimeout(() => setProgress(0), 200);

        const pageTitle = title || (resolved.includes('duckduckgo') ? 'Search Results' : resolved.replace(/^https?:\/\//, ''));

        setTabs(prev => {
          const updated = [...prev];
          const tab = updated[activeTabIndex];
          const newHist = tab.history.slice(0, tab.historyIndex + 1);
          newHist.push(resolved);
          updated[activeTabIndex] = {
            ...tab,
            url: resolved,
            title: pageTitle,
            isEvicted: false,
            history: newHist,
            historyIndex: newHist.length - 1,
          };
          return updated;
        });

        setHistoryList(prev => [
          { title: pageTitle, url: resolved, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
          ...prev.slice(0, 49)
        ]);

        // Simulating memory variation based on loaded page
        setUsedHeapMB(prev => Math.min(120, Math.max(14, prev + Math.floor(Math.random() * 8) - 3)));
      }, 250);
    }, 200);
  };

  const handleBack = () => {
    if (activeModal) {
      setActiveModal(null);
      return;
    }
    if (currentTab.historyIndex > 0) {
      const prevIdx = currentTab.historyIndex - 1;
      const prevUrl = currentTab.history[prevIdx];
      setAddressInput(prevUrl);
      setTabs(prev => {
        const copy = [...prev];
        copy[activeTabIndex] = {
          ...copy[activeTabIndex],
          url: prevUrl,
          historyIndex: prevIdx,
        };
        return copy;
      });
    } else {
      setActiveModal('exit');
    }
  };

  const handleForward = () => {
    if (currentTab.historyIndex < currentTab.history.length - 1) {
      const nextIdx = currentTab.historyIndex + 1;
      const nextUrl = currentTab.history[nextIdx];
      setAddressInput(nextUrl);
      setTabs(prev => {
        const copy = [...prev];
        copy[activeTabIndex] = {
          ...copy[activeTabIndex],
          url: nextUrl,
          historyIndex: nextIdx,
        };
        return copy;
      });
    }
  };

  // Add new Tab (Max 3)
  const handleAddNewTab = () => {
    if (tabs.length >= 3) {
      alert('RAM Protection Policy: Strictly limited to 3 tabs on 512MB RAM');
      return;
    }
    const newTab: TabItem = {
      id: 'tab-' + (tabs.length + 1),
      url: 'file:///android_asset/homepage.html',
      title: 'New Tab',
      isEvicted: false,
      history: ['file:///android_asset/homepage.html'],
      historyIndex: 0,
    };
    setTabs(prev => [...prev, newTab]);
    setActiveTabIndex(tabs.length);
    setAddressInput('file:///android_asset/homepage.html');
    setUsedHeapMB(prev => Math.min(120, prev + 12));
    setActiveModal(null);
  };

  const handleSelectTab = (index: number) => {
    setActiveTabIndex(index);
    const target = tabs[index];
    setAddressInput(target.url);
    if (target.isEvicted) {
      // Re-hydrate evicted tab
      setTabs(prev =>
        prev.map((t, idx) => (idx === index ? { ...t, isEvicted: false } : t))
      );
      setUsedHeapMB(prev => Math.min(120, prev + 10));
    }
    setActiveModal(null);
  };

  const handleCloseTab = (index: number) => {
    if (tabs.length <= 1) return;
    const remaining = tabs.filter((_, idx) => idx !== index);
    setTabs(remaining);
    setActiveTabIndex(prev => (prev >= remaining.length ? remaining.length - 1 : prev));
    setAddressInput(remaining[0].url);
    setUsedHeapMB(prev => Math.max(14, prev - 12));
  };

  // Key Event Dispatcher (Simulating RemoteManager.java)
  const dispatchKey = (name: string, keyCode: number) => {
    setLastEvent({
      name,
      keyCode,
      action: 'ACTION_DOWN',
      time: new Date().toLocaleTimeString(),
    });

    if (isCursorMode) {
      if (keyCode === 19) setCursorPos(p => ({ ...p, y: Math.max(30, p.y - cursorSpeed) })); // UP
      else if (keyCode === 20) setCursorPos(p => ({ ...p, y: Math.min(420, p.y + cursorSpeed) })); // DOWN
      else if (keyCode === 21) setCursorPos(p => ({ ...p, x: Math.max(20, p.x - cursorSpeed) })); // LEFT
      else if (keyCode === 22) setCursorPos(p => ({ ...p, x: Math.min(760, p.x + cursorSpeed) })); // RIGHT
      else if (keyCode === 23 || keyCode === 66) {
        // Virtual Cursor Click at coordinates
        handleCursorClickAt(cursorPos.x, cursorPos.y);
      } else if (keyCode === 4) {
        handleBack();
      } else if (keyCode === 82) {
        setActiveModal('menu');
      }
      return;
    }

    // Standard D-Pad Focus Mode
    if (keyCode === 21) {
      // DPAD_LEFT
      setFocusedToolbarIndex(prev => Math.max(0, prev - 1));
    } else if (keyCode === 22) {
      // DPAD_RIGHT
      setFocusedToolbarIndex(prev => Math.min(7, prev + 1));
    } else if (keyCode === 23 || keyCode === 66) {
      // DPAD_CENTER / ENTER
      triggerFocusedAction();
    } else if (keyCode === 4) {
      // BACK
      handleBack();
    } else if (keyCode === 82) {
      // MENU
      setActiveModal('menu');
    }
  };

  const triggerFocusedAction = () => {
    switch (focusedToolbarIndex) {
      case 0: handleBack(); break;
      case 1: handleForward(); break;
      case 2: navigateTo(currentTab.url); break;
      case 3: navigateTo('file:///android_asset/homepage.html'); break;
      case 4: navigateTo(addressInput); break;
      case 5: setActiveModal('tabs'); break;
      case 6: setIsCursorMode(!isCursorMode); break;
      case 7: setActiveModal('menu'); break;
    }
  };

  const handleCursorClickAt = (x: number, y: number) => {
    // If clicking in toolbar
    if (y < 60) {
      if (x > 20 && x < 70) handleBack();
      else if (x > 75 && x < 135) handleForward();
      else if (x > 140 && x < 185) navigateTo(currentTab.url);
      else if (x > 190 && x < 235) navigateTo('file:///android_asset/homepage.html');
      else if (x > 540 && x < 610) setActiveModal('tabs');
      else if (x > 615 && x < 695) setIsCursorMode(false);
      else if (x > 700 && x < 745) setActiveModal('menu');
    } else {
      // In webview body
      if (currentTab.url === 'file:///android_asset/homepage.html') {
        if (y > 140 && y < 220) {
          if (x > 40 && x < 170) navigateTo('https://html.duckduckgo.com/html/', 'DuckDuckGo Lite');
          else if (x > 180 && x < 310) navigateTo('https://m.youtube.com', 'YouTube Mobile');
          else if (x > 320 && x < 450) navigateTo('https://en.m.wikipedia.org', 'Wikipedia');
          else if (x > 460 && x < 590) navigateTo('https://archive.org', 'Internet Archive');
          else if (x > 600 && x < 730) navigateTo('https://news.ycombinator.com', 'Hacker News');
        } else if (y > 270 && y < 350) {
          if (x > 40 && x < 170) setActiveModal('bookmarks');
          else if (x > 180 && x < 310) setActiveModal('history');
          else if (x > 320 && x < 450) navigateTo('file:///android_asset/diagnostics.html', 'Diagnostics');
          else if (x > 460 && x < 590) setActiveModal('menu');
        }
      }
    }
  };

  // Keyboard navigation capture
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // Prevent scrolling the page when interacting with TV
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter', 'Backspace', 'Escape'].includes(e.key)) {
        if (document.activeElement?.tagName === 'INPUT' && e.key !== 'Escape') {
          return;
        }
        e.preventDefault();
      }

      if (e.key === 'ArrowUp') dispatchKey('KEYCODE_DPAD_UP', 19);
      else if (e.key === 'ArrowDown') dispatchKey('KEYCODE_DPAD_DOWN', 20);
      else if (e.key === 'ArrowLeft') dispatchKey('KEYCODE_DPAD_LEFT', 21);
      else if (e.key === 'ArrowRight') dispatchKey('KEYCODE_DPAD_RIGHT', 22);
      else if (e.key === 'Enter') dispatchKey('KEYCODE_DPAD_CENTER', 23);
      else if (e.key === 'Backspace' || e.key === 'Escape') dispatchKey('KEYCODE_BACK', 4);
      else if (e.key.toLowerCase() === 'm') dispatchKey('KEYCODE_MENU', 82);
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isCursorMode, cursorPos, focusedToolbarIndex, activeModal, currentTab, addressInput]);

  return (
    <div id="tv_simulator_root" className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* 16:9 TV Display Screen */}
      <div className="lg:col-span-8 flex flex-col items-center">
        {/* TV Bezel / Frame */}
        <div className="w-full bg-[#0A0A0C] p-3 rounded-2xl border-4 border-[#24242A] shadow-2xl relative">
          {/* Top Brand Logo on Bezel */}
          <div className="flex items-center justify-between px-3 pb-2 text-xs text-[#8A8A96]">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse inline-block" />
              <span className="font-bold text-[#E5A93C] tracking-wide">YANG KAI TV BOX (TTX-V005)</span>
              <span className="text-[10px] bg-[#1E1E24] px-1.5 py-0.5 rounded text-gray-300">ARM32 • API 19 • 512MB RAM</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-gray-400">HDMI 1080p@60Hz</span>
              <button
                id="btn_toggle_forensics"
                onClick={() => setShowForensicsOverlay(!showForensicsOverlay)}
                className="text-[10px] bg-[#24242A] hover:bg-[#34343E] text-[#E5A93C] px-2 py-0.5 rounded border border-[#3A3A46]"
              >
                {showForensicsOverlay ? 'Hide Key Forensics' : 'Show Key Forensics'}
              </button>
            </div>
          </div>

          {/* Actual 16:9 Native TV Screen */}
          <div
            ref={tvScreenRef}
            tabIndex={0}
            className="w-full aspect-[16/10] bg-[#121214] rounded-lg overflow-hidden flex flex-col relative border border-[#202026] select-none outline-none focus:ring-1 focus:ring-[#E5A93C]"
          >
            {/* 1. Android KitKat Browser Toolbar */}
            <div className="h-12 bg-[#1A1A1E] border-b border-[#282832] flex items-center px-2 gap-1.5 shrink-0 z-10">
              <button
                id="tv_btn_back"
                onClick={handleBack}
                className={`h-8 px-2.5 rounded text-xs font-semibold flex items-center gap-1 transition-all ${
                  focusedToolbarIndex === 0
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F] scale-105'
                    : 'bg-[#24242A] text-gray-200 border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Back
              </button>

              <button
                id="tv_btn_forward"
                onClick={handleForward}
                className={`h-8 px-2.5 rounded text-xs font-semibold flex items-center gap-1 transition-all ${
                  focusedToolbarIndex === 1
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F] scale-105'
                    : 'bg-[#24242A] text-gray-200 border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <ArrowRight className="w-3.5 h-3.5" />
              </button>

              <button
                id="tv_btn_reload"
                onClick={() => navigateTo(currentTab.url)}
                className={`h-8 w-8 rounded text-xs font-semibold flex items-center justify-center transition-all ${
                  focusedToolbarIndex === 2
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F] scale-105'
                    : 'bg-[#24242A] text-[#E5A93C] border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <RotateCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>

              <button
                id="tv_btn_home"
                onClick={() => navigateTo('file:///android_asset/homepage.html')}
                className={`h-8 w-8 rounded text-xs font-semibold flex items-center justify-center transition-all ${
                  focusedToolbarIndex === 3
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F] scale-105'
                    : 'bg-[#24242A] text-[#E5A93C] border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <Home className="w-3.5 h-3.5" />
              </button>

              {/* Address Bar */}
              <div className="flex-1 flex items-center gap-1">
                <input
                  id="tv_input_address"
                  type="text"
                  value={addressInput}
                  onChange={(e) => setAddressInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') navigateTo(addressInput);
                  }}
                  onFocus={() => setFocusedToolbarIndex(4)}
                  placeholder="Enter URL or search query..."
                  className={`w-full h-8 px-3 text-xs rounded transition-all bg-[#141418] text-white placeholder-gray-500 outline-none ${
                    focusedToolbarIndex === 4
                      ? 'border-2 border-[#FFD54F] ring-1 ring-[#FFD54F]/50'
                      : 'border border-[#383844]'
                  }`}
                />
                <button
                  id="tv_btn_go"
                  onClick={() => navigateTo(addressInput)}
                  className="h-8 px-3 rounded text-xs font-bold bg-[#E5A93C] hover:bg-[#FFD54F] text-[#121214]"
                >
                  Go
                </button>
              </div>

              <button
                id="tv_btn_tabs"
                onClick={() => setActiveModal('tabs')}
                className={`h-8 px-2.5 rounded text-xs font-semibold flex items-center gap-1 transition-all ${
                  focusedToolbarIndex === 5
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F] scale-105'
                    : 'bg-[#24242A] text-[#E5A93C] border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <Layers className="w-3.5 h-3.5" /> Tabs ({tabs.length})
              </button>

              <button
                id="tv_btn_cursor_toggle"
                onClick={() => setIsCursorMode(!isCursorMode)}
                className={`h-8 px-2.5 rounded text-xs font-semibold flex items-center gap-1 transition-all ${
                  isCursorMode
                    ? 'bg-[#E5A93C] text-[#121214] font-bold border-2 border-[#FFD54F]'
                    : focusedToolbarIndex === 6
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F]'
                    : 'bg-[#24242A] text-gray-300 border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <MousePointer className="w-3.5 h-3.5" /> {isCursorMode ? 'Pointer' : 'D-Pad'}
              </button>

              <button
                id="tv_btn_menu"
                onClick={() => setActiveModal('menu')}
                className={`h-8 w-8 rounded text-xs font-semibold flex items-center justify-center transition-all ${
                  focusedToolbarIndex === 7
                    ? 'bg-[#2D2D38] border-2 border-[#FFD54F] text-[#FFD54F] scale-105'
                    : 'bg-[#24242A] text-gray-200 border border-[#3A3A44] hover:bg-[#2F2F38]'
                }`}
              >
                <MenuIcon className="w-4 h-4" />
              </button>
            </div>

            {/* Progress Bar */}
            {progress > 0 && progress < 100 && (
              <div className="h-0.5 bg-[#121214] w-full">
                <div
                  className="h-full bg-gradient-to-r from-[#E5A93C] to-[#FFD54F] transition-all duration-150"
                  style={{ width: `${progress}%` }}
                />
              </div>
            )}

            {/* 2. Web Content Area */}
            <div className="flex-1 bg-[#121214] text-white p-6 overflow-y-auto relative flex flex-col items-center justify-start">
              {currentTab.isEvicted ? (
                /* Evicted Tab Display */
                <div className="my-auto text-center max-w-md p-6 bg-[#1A1A22] rounded-xl border border-amber-500/40">
                  <Cpu className="w-12 h-12 text-[#E5A93C] mx-auto mb-3 animate-pulse" />
                  <h3 className="text-lg font-bold text-[#E5A93C]">Tab Background Memory Evicted</h3>
                  <p className="text-xs text-gray-400 mt-2 leading-relaxed">
                    Under memory pressure ({usedHeapMB}MB heap), Yang Kai Browser automatically evicted this inactive WebView instance to protect the 512MB hardware limit.
                  </p>
                  <p className="text-xs text-gray-300 mt-2 font-mono bg-[#121216] p-2 rounded">
                    URL: {currentTab.url}
                  </p>
                  <button
                    onClick={() => handleSelectTab(activeTabIndex)}
                    className="mt-4 px-4 py-2 bg-[#E5A93C] hover:bg-[#FFD54F] text-[#121214] font-bold text-xs rounded"
                  >
                    Restore & Reload Tab
                  </button>
                </div>
              ) : currentTab.url === 'file:///android_asset/homepage.html' ? (
                /* Real Local Homepage Asset Rendering */
                <div className="w-full max-w-2xl text-center">
                  <div className="mb-5">
                    <h1 className="text-2xl font-black text-[#E5A93C] tracking-wider flex items-center justify-center gap-2">
                      <span>🐉</span> YANG KAI BROWSER
                    </h1>
                    <p className="text-xs text-gray-400 mt-1">
                      Hardware-Specific Autonomous Legacy TV Browser
                    </p>
                    <span className="inline-block mt-2 bg-[#1C1C24] text-[#FFD54F] border border-[#3A3A46] text-[10px] px-3 py-1 rounded-full font-mono">
                      Target: Android 4.4.4 KitKat • API 19 • 512MB RAM • ARM32
                    </span>
                  </div>

                  {/* Section: Web Portals */}
                  <div className="text-left mb-4">
                    <h2 className="text-xs font-bold text-[#E5A93C] uppercase tracking-wider pb-1 border-b border-[#282834] mb-3">
                      ⚡ Quick Access Web Portals
                    </h2>
                    <div className="grid grid-cols-5 gap-2">
                      <button
                        onClick={() => navigateTo('https://html.duckduckgo.com/html/', 'DuckDuckGo Lite')}
                        className="p-3 bg-[#1C1C24] hover:bg-[#282834] border border-[#2D2D3A] hover:border-[#FFD54F] rounded-lg text-center transition-all group"
                      >
                        <Search className="w-5 h-5 mx-auto mb-1 text-amber-400 group-hover:scale-110 transition-transform" />
                        <span className="text-[11px] font-bold block text-gray-200">DuckDuckGo</span>
                        <span className="text-[9px] text-gray-500">Lite Engine</span>
                      </button>

                      <button
                        onClick={() => navigateTo('https://m.youtube.com', 'YouTube Mobile')}
                        className="p-3 bg-[#1C1C24] hover:bg-[#282834] border border-[#2D2D3A] hover:border-[#FFD54F] rounded-lg text-center transition-all group"
                      >
                        <Tv className="w-5 h-5 mx-auto mb-1 text-red-500 group-hover:scale-110 transition-transform" />
                        <span className="text-[11px] font-bold block text-gray-200">YouTube</span>
                        <span className="text-[9px] text-gray-500">Mobile Web</span>
                      </button>

                      <button
                        onClick={() => navigateTo('https://en.m.wikipedia.org', 'Wikipedia')}
                        className="p-3 bg-[#1C1C24] hover:bg-[#282834] border border-[#2D2D3A] hover:border-[#FFD54F] rounded-lg text-center transition-all group"
                      >
                        <Compass className="w-5 h-5 mx-auto mb-1 text-blue-400 group-hover:scale-110 transition-transform" />
                        <span className="text-[11px] font-bold block text-gray-200">Wikipedia</span>
                        <span className="text-[9px] text-gray-500">Fast Mobile</span>
                      </button>

                      <button
                        onClick={() => navigateTo('https://archive.org', 'Internet Archive')}
                        className="p-3 bg-[#1C1C24] hover:bg-[#282834] border border-[#2D2D3A] hover:border-[#FFD54F] rounded-lg text-center transition-all group"
                      >
                        <Database className="w-5 h-5 mx-auto mb-1 text-emerald-400 group-hover:scale-110 transition-transform" />
                        <span className="text-[11px] font-bold block text-gray-200">Archive.org</span>
                        <span className="text-[9px] text-gray-500">Universal Web</span>
                      </button>

                      <button
                        onClick={() => navigateTo('https://news.ycombinator.com', 'Hacker News')}
                        className="p-3 bg-[#1C1C24] hover:bg-[#282834] border border-[#2D2D3A] hover:border-[#FFD54F] rounded-lg text-center transition-all group"
                      >
                        <Activity className="w-5 h-5 mx-auto mb-1 text-orange-500 group-hover:scale-110 transition-transform" />
                        <span className="text-[11px] font-bold block text-gray-200">Hacker News</span>
                        <span className="text-[9px] text-gray-500">HTML Lite</span>
                      </button>
                    </div>
                  </div>

                  {/* Section: Local Utilities */}
                  <div className="text-left">
                    <h2 className="text-xs font-bold text-[#E5A93C] uppercase tracking-wider pb-1 border-b border-[#282834] mb-3">
                      🛠️ Local Browser Utilities (Offline Capable)
                    </h2>
                    <div className="grid grid-cols-4 gap-2">
                      <button
                        onClick={() => setActiveModal('bookmarks')}
                        className="p-2.5 bg-[#181820] hover:bg-[#242430] border border-[#2A2A36] hover:border-[#FFD54F] rounded text-left flex items-center gap-2"
                      >
                        <span className="text-base">⭐</span>
                        <div>
                          <div className="text-[11px] font-bold text-gray-200">Bookmarks</div>
                          <div className="text-[9px] text-gray-500">Stored in SQLite</div>
                        </div>
                      </button>

                      <button
                        onClick={() => setActiveModal('history')}
                        className="p-2.5 bg-[#181820] hover:bg-[#242430] border border-[#2A2A36] hover:border-[#FFD54F] rounded text-left flex items-center gap-2"
                      >
                        <span className="text-base">🕒</span>
                        <div>
                          <div className="text-[11px] font-bold text-gray-200">History</div>
                          <div className="text-[9px] text-gray-500">Max 300 items</div>
                        </div>
                      </button>

                      <button
                        onClick={() => navigateTo('file:///android_asset/diagnostics.html', 'Diagnostics')}
                        className="p-2.5 bg-[#181820] hover:bg-[#242430] border border-[#2A2A36] hover:border-[#FFD54F] rounded text-left flex items-center gap-2"
                      >
                        <span className="text-base">🩺</span>
                        <div>
                          <div className="text-[11px] font-bold text-gray-200">Diagnostics</div>
                          <div className="text-[9px] text-gray-500">Hardware Audit</div>
                        </div>
                      </button>

                      <button
                        onClick={() => setActiveModal('menu')}
                        className="p-2.5 bg-[#181820] hover:bg-[#242430] border border-[#2A2A36] hover:border-[#FFD54F] rounded text-left flex items-center gap-2"
                      >
                        <span className="text-base">⚙️</span>
                        <div>
                          <div className="text-[11px] font-bold text-gray-200">Menu & Tools</div>
                          <div className="text-[9px] text-gray-500">Settings & RAM</div>
                        </div>
                      </button>
                    </div>
                  </div>

                  <p className="mt-5 text-[10px] text-gray-500 font-mono">
                    100% Standalone • Zero Analytics • Zero Cloud Telemetry • Preserves 512MB RAM
                  </p>
                </div>
              ) : currentTab.url === 'file:///android_asset/diagnostics.html' ? (
                /* Hardware Diagnostics Screen */
                <div className="w-full max-w-xl text-left bg-[#16161C] p-4 rounded-xl border border-[#282834]">
                  <div className="flex items-center justify-between pb-3 border-b border-[#282834] mb-3">
                    <h2 className="text-sm font-bold text-[#E5A93C] flex items-center gap-2">
                      <span>🩺</span> TTX-V005 Legacy TV Hardware Diagnostics
                    </h2>
                    <span className="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-700">
                      SYS HEALTH: OK
                    </span>
                  </div>

                  <table className="w-full text-xs text-left mb-4">
                    <thead>
                      <tr className="border-b border-[#282834] text-gray-400">
                        <th className="pb-1.5 font-medium">Subsystem</th>
                        <th className="pb-1.5 font-medium">Target Specification</th>
                        <th className="pb-1.5 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#22222A]">
                      <tr>
                        <td className="py-2 text-gray-300">Android OS</td>
                        <td className="py-2 text-gray-400">4.4.4 KitKat (API 19)</td>
                        <td className="py-2 text-emerald-400 font-bold">TARGETED</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-gray-300">CPU Architecture</td>
                        <td className="py-2 text-gray-400">ARM Cortex-A7 (32-bit `armeabi-v7a`)</td>
                        <td className="py-2 text-emerald-400 font-bold">COMPATIBLE</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-gray-300">Physical Memory</td>
                        <td className="py-2 text-gray-400">512 MB Physical RAM</td>
                        <td className="py-2 text-emerald-400 font-bold">PROTECTED ({usedHeapMB}MB used)</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-gray-300">Web Engine</td>
                        <td className="py-2 text-gray-400">KitKat System WebView (Chromium 33)</td>
                        <td className="py-2 text-emerald-400 font-bold">ACTIVE</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-gray-300">D-Pad Remote</td>
                        <td className="py-2 text-gray-400">Standard IR Remote (KeyCodes 19-23)</td>
                        <td className="py-2 text-emerald-400 font-bold">CONNECTED</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-gray-300">Virtual Cursor</td>
                        <td className="py-2 text-gray-400">Synthetic MotionEvents Layer</td>
                        <td className="py-2 text-emerald-400 font-bold">AVAILABLE</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-gray-300">Max Tabs Policy</td>
                        <td className="py-2 text-gray-400">3 Tabs Max with Eviction</td>
                        <td className="py-2 text-emerald-400 font-bold">ENFORCED</td>
                      </tr>
                    </tbody>
                  </table>

                  <button
                    onClick={() => navigateTo('file:///android_asset/homepage.html')}
                    className="px-3 py-1.5 bg-[#24242E] hover:bg-[#323240] text-[#E5A93C] text-xs font-bold rounded border border-[#3A3A4A]"
                  >
                    ◀ Return to Homepage
                  </button>
                </div>
              ) : (
                /* External Web Page Simulation */
                <div className="w-full max-w-xl text-left bg-[#16161C] p-4 rounded-xl border border-[#282834]">
                  <div className="flex items-center justify-between pb-2 border-b border-[#282834] mb-3">
                    <span className="text-xs font-bold text-gray-200 truncate flex items-center gap-1.5">
                      <ExternalLink className="w-3.5 h-3.5 text-[#E5A93C]" /> {currentTab.title}
                    </span>
                    <span className="text-[10px] text-gray-400 font-mono">{currentTab.url}</span>
                  </div>

                  <div className="p-3 bg-[#111116] rounded border border-[#24242E] text-xs text-gray-300 space-y-2">
                    <p className="text-emerald-400 font-medium">✓ Securely Rendered via System WebView</p>
                    <p>Page successfully loaded on simulated KitKat Chromium 33 rendering pipeline.</p>
                    <div className="flex gap-2 pt-2">
                      <button
                        onClick={() => {
                          setBookmarks(prev => [...prev, { title: currentTab.title, url: currentTab.url }]);
                          alert('Bookmark saved to local SQLite database!');
                        }}
                        className="px-2.5 py-1 bg-[#242430] hover:bg-[#303040] text-amber-300 text-xs rounded border border-[#3E3E50]"
                      >
                        ⭐ Bookmark This Page
                      </button>
                      <button
                        onClick={() => navigateTo('file:///android_asset/homepage.html')}
                        className="px-2.5 py-1 bg-[#242430] hover:bg-[#303040] text-gray-300 text-xs rounded border border-[#3E3E50]"
                      >
                        🏠 Return Home
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 3. Virtual Cursor Pointer Layer */}
            {isCursorMode && (
              <div
                className="absolute pointer-events-none transition-all duration-75 z-30"
                style={{
                  left: `${cursorPos.x}px`,
                  top: `${cursorPos.y}px`,
                  transform: 'translate(-50%, -50%)',
                }}
              >
                <div className="w-6 h-6 rounded-full bg-[#E5A93C]/20 border-2 border-[#FFD54F] flex items-center justify-center shadow-lg animate-pulse">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#FFD54F]" />
                </div>
              </div>
            )}

            {/* 4. Bottom Status Bar */}
            <div className="h-6 bg-[#18181E] border-t border-[#252530] flex items-center justify-between px-3 text-[11px] shrink-0 z-10">
              <div className="flex items-center gap-2">
                <span className="font-bold text-[#E5A93C]">🐉 Yang Kai v1.0.0</span>
                <span className="text-gray-500">|</span>
                <span className="text-gray-400">KitKat 4.4.4 (API 19)</span>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={`font-mono font-medium ${
                    memoryState === 'NORMAL' ? 'text-emerald-400' :
                    memoryState === 'WARNING' ? 'text-amber-400' : 'text-red-400 animate-pulse'
                  }`}
                >
                  RAM: {memoryState} ({usedHeapMB}MB / {maxHeapMB}MB)
                </span>
                <span className="text-gray-500">|</span>
                <span className="text-[#FFD54F] font-bold">
                  {isCursorMode ? 'MODE: VIRTUAL CURSOR' : 'MODE: DPAD FOCUS'}
                </span>
              </div>
            </div>

            {/* 5. Key Event Forensics Overlay (Toggleable) */}
            {showForensicsOverlay && (
              <div className="absolute bottom-8 right-3 bg-[#0E0E12]/90 backdrop-blur border border-[#E5A93C]/50 rounded p-2.5 text-[10px] font-mono text-gray-200 z-20 shadow-xl max-w-[220px]">
                <div className="font-bold text-[#E5A93C] pb-1 border-b border-[#282834] mb-1">
                  REMOTE KEY FORENSICS
                </div>
                <div>Key: <span className="text-[#FFD54F]">{lastEvent.name}</span></div>
                <div>Code: <span className="text-white">{lastEvent.keyCode}</span></div>
                <div>Action: <span className="text-gray-400">{lastEvent.action}</span></div>
                <div>Time: <span className="text-gray-500">{lastEvent.time}</span></div>
              </div>
            )}

            {/* 6. Modals (Tabs, Menu, Bookmarks, History, Exit) */}
            {activeModal && (
              <div className="absolute inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-40">
                <div className="bg-[#1C1C24] border-2 border-[#E5A93C] rounded-xl p-5 max-w-sm w-full shadow-2xl text-left">
                  {activeModal === 'tabs' && (
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-[#2C2C38] mb-3">
                        <h3 className="text-sm font-bold text-[#E5A93C]">Tab Manager (Max 3 Tabs)</h3>
                        <button onClick={() => setActiveModal(null)} className="text-gray-400 hover:text-white text-xs">✕</button>
                      </div>
                      <div className="space-y-2 mb-4">
                        {tabs.map((tab, idx) => (
                          <div
                            key={tab.id}
                            className={`p-2.5 rounded flex items-center justify-between border ${
                              idx === activeTabIndex
                                ? 'bg-[#282838] border-[#FFD54F] text-[#FFD54F]'
                                : 'bg-[#16161E] border-[#2A2A36] text-gray-300'
                            }`}
                          >
                            <button
                              onClick={() => handleSelectTab(idx)}
                              className="text-xs font-semibold text-left truncate flex-1"
                            >
                              Tab {idx + 1}: {tab.title} {tab.isEvicted && '(Evicted)'}
                            </button>
                            {tabs.length > 1 && (
                              <button
                                onClick={() => handleCloseTab(idx)}
                                className="text-red-400 hover:text-red-300 px-1.5 py-0.5 text-xs ml-2"
                              >
                                ✕
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={handleAddNewTab}
                        disabled={tabs.length >= 3}
                        className={`w-full py-2 rounded text-xs font-bold transition-all ${
                          tabs.length < 3
                            ? 'bg-[#E5A93C] hover:bg-[#FFD54F] text-[#121214]'
                            : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        ➕ Open New Tab {tabs.length >= 3 && '(Max 3 Reached)'}
                      </button>
                    </div>
                  )}

                  {activeModal === 'menu' && (
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-[#2C2C38] mb-3">
                        <h3 className="text-sm font-bold text-[#E5A93C]">Browser Quick Menu</h3>
                        <button onClick={() => setActiveModal(null)} className="text-gray-400 hover:text-white text-xs">✕</button>
                      </div>
                      <div className="space-y-1.5 text-xs">
                        <button
                          onClick={() => {
                            setBookmarks(prev => [...prev, { title: currentTab.title, url: currentTab.url }]);
                            setActiveModal(null);
                            alert('Bookmark Saved!');
                          }}
                          className="w-full text-left p-2 rounded hover:bg-[#282838] text-gray-200 flex items-center gap-2"
                        >
                          ⭐ Add Current Page to Bookmarks
                        </button>
                        <button
                          onClick={() => setActiveModal('bookmarks')}
                          className="w-full text-left p-2 rounded hover:bg-[#282838] text-gray-200 flex items-center gap-2"
                        >
                          📖 Bookmarks Collection
                        </button>
                        <button
                          onClick={() => setActiveModal('history')}
                          className="w-full text-left p-2 rounded hover:bg-[#282838] text-gray-200 flex items-center gap-2"
                        >
                          🕒 Browsing History (SQLite)
                        </button>
                        <button
                          onClick={() => {
                            navigateTo('file:///android_asset/diagnostics.html');
                            setActiveModal(null);
                          }}
                          className="w-full text-left p-2 rounded hover:bg-[#282838] text-gray-200 flex items-center gap-2"
                        >
                          🩺 TV Hardware Diagnostics
                        </button>
                        <button
                          onClick={() => {
                            setUsedHeapMB(16);
                            setTabs(prev => prev.map((t, i) => (i === activeTabIndex ? t : { ...t, isEvicted: true })));
                            setActiveModal(null);
                            alert('App Cache and Background Tab Memory Cleared!');
                          }}
                          className="w-full text-left p-2 rounded hover:bg-[#282838] text-amber-300 flex items-center gap-2"
                        >
                          🧹 Clear Cache & Free Dalvik Heap
                        </button>
                      </div>
                    </div>
                  )}

                  {activeModal === 'bookmarks' && (
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-[#2C2C38] mb-3">
                        <h3 className="text-sm font-bold text-[#E5A93C]">Saved Bookmarks</h3>
                        <button onClick={() => setActiveModal(null)} className="text-gray-400 hover:text-white text-xs">✕</button>
                      </div>
                      <div className="max-h-48 overflow-y-auto space-y-1.5 text-xs mb-3">
                        {bookmarks.map((bm, i) => (
                          <div
                            key={i}
                            className="p-2 bg-[#14141C] hover:bg-[#242434] rounded flex items-center justify-between border border-[#252530]"
                          >
                            <button
                              onClick={() => {
                                navigateTo(bm.url, bm.title);
                                setActiveModal(null);
                              }}
                              className="text-left font-medium text-gray-200 truncate flex-1"
                            >
                              {bm.title}
                            </button>
                            <button
                              onClick={() => setBookmarks(bms => bms.filter((_, idx) => idx !== i))}
                              className="text-gray-500 hover:text-red-400 px-1"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeModal === 'history' && (
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-[#2C2C38] mb-3">
                        <h3 className="text-sm font-bold text-[#E5A93C]">History (Max 300)</h3>
                        <button onClick={() => setActiveModal(null)} className="text-gray-400 hover:text-white text-xs">✕</button>
                      </div>
                      <div className="max-h-48 overflow-y-auto space-y-1.5 text-xs mb-3">
                        {historyList.map((h, i) => (
                          <button
                            key={i}
                            onClick={() => {
                              navigateTo(h.url, h.title);
                              setActiveModal(null);
                            }}
                            className="w-full text-left p-2 bg-[#14141C] hover:bg-[#242434] rounded border border-[#252530]"
                          >
                            <div className="font-semibold text-gray-200 truncate">{h.title}</div>
                            <div className="text-[10px] text-gray-500 truncate">{h.url} • {h.time}</div>
                          </button>
                        ))}
                      </div>
                      <button
                        onClick={() => {
                          setHistoryList([]);
                          alert('History cleared');
                        }}
                        className="w-full py-1.5 bg-[#252532] text-xs text-red-400 rounded hover:bg-[#353545]"
                      >
                        Clear All History
                      </button>
                    </div>
                  )}

                  {activeModal === 'exit' && (
                    <div className="text-center">
                      <AlertTriangle className="w-10 h-10 text-[#E5A93C] mx-auto mb-2" />
                      <h3 className="text-base font-bold text-white mb-2">Exit Yang Kai Browser?</h3>
                      <p className="text-xs text-gray-400 mb-4">
                        Pressing Back reached root history. Do you want to return to your TV launcher?
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setActiveModal(null);
                            navigateTo('file:///android_asset/homepage.html');
                          }}
                          className="flex-1 py-2 bg-[#252532] text-gray-200 text-xs font-bold rounded"
                        >
                          Stay in Browser
                        </button>
                        <button
                          onClick={() => {
                            setActiveModal(null);
                            alert('Exited Yang Kai Browser to Android TV Launcher');
                          }}
                          className="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded"
                        >
                          Exit
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Keyboard instructions */}
        <div className="w-full mt-3 p-3 bg-[#16161C] border border-[#24242E] rounded-xl flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <span className="bg-[#242430] text-gray-200 px-2 py-0.5 rounded font-mono text-[11px]">Physical Keys:</span>
            <span>Use Arrow Keys (D-Pad), <kbd className="font-mono bg-[#202028] px-1 rounded">Enter</kbd> (OK), <kbd className="font-mono bg-[#202028] px-1 rounded">Backspace/Esc</kbd> (Back), <kbd className="font-mono bg-[#202028] px-1 rounded">M</kbd> (Menu)</span>
          </div>
          <button
            onClick={onDownloadApk}
            className="text-[#E5A93C] font-semibold hover:underline flex items-center gap-1"
          >
            Download Real APK (41.1 KB) →
          </button>
        </div>
      </div>

      {/* Hardware Virtual TV Remote Control Panel */}
      <div className="lg:col-span-4 flex flex-col items-center">
        <div className="w-full max-w-[280px] bg-[#141418] border-2 border-[#2C2C36] rounded-3xl p-5 shadow-2xl relative flex flex-col items-center">
          {/* Remote Top */}
          <div className="w-full flex items-center justify-between pb-4 border-b border-[#252530]">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
              <span className="text-xs font-bold text-gray-400 font-mono">IR REMOTE</span>
            </div>
            <span className="text-[10px] text-[#E5A93C] font-semibold tracking-wider">YANG KAI TV</span>
          </div>

          {/* Mode Switch Button */}
          <div className="w-full my-4">
            <button
              id="remote_btn_toggle_mode"
              onClick={() => setIsCursorMode(!isCursorMode)}
              className={`w-full py-2.5 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all ${
                isCursorMode
                  ? 'bg-gradient-to-r from-amber-500 to-yellow-400 text-black shadow-lg scale-102'
                  : 'bg-[#22222C] text-gray-300 border border-[#3A3A4A] hover:bg-[#2C2C38]'
              }`}
            >
              <MousePointer className="w-4 h-4" />
              {isCursorMode ? 'Virtual Pointer Active' : 'Switch to Virtual Pointer'}
            </button>
          </div>

          {/* D-Pad Controller Ring */}
          <div className="relative w-44 h-44 my-2 flex items-center justify-center">
            {/* Outer D-Pad Ring Background */}
            <div className="absolute inset-0 rounded-full bg-[#1F1F28] border-2 border-[#323242] shadow-inner" />

            {/* D-Pad UP (KeyCode 19) */}
            <button
              id="remote_dpad_up"
              onClick={() => dispatchKey('KEYCODE_DPAD_UP', 19)}
              className="absolute top-1 w-14 h-12 flex items-center justify-center text-gray-200 hover:text-[#FFD54F] active:scale-95 transition-transform"
              title="D-Pad UP (19)"
            >
              ▲
            </button>

            {/* D-Pad DOWN (KeyCode 20) */}
            <button
              id="remote_dpad_down"
              onClick={() => dispatchKey('KEYCODE_DPAD_DOWN', 20)}
              className="absolute bottom-1 w-14 h-12 flex items-center justify-center text-gray-200 hover:text-[#FFD54F] active:scale-95 transition-transform"
              title="D-Pad DOWN (20)"
            >
              ▼
            </button>

            {/* D-Pad LEFT (KeyCode 21) */}
            <button
              id="remote_dpad_left"
              onClick={() => dispatchKey('KEYCODE_DPAD_LEFT', 21)}
              className="absolute left-1 w-12 h-14 flex items-center justify-center text-gray-200 hover:text-[#FFD54F] active:scale-95 transition-transform"
              title="D-Pad LEFT (21)"
            >
              ◀
            </button>

            {/* D-Pad RIGHT (KeyCode 22) */}
            <button
              id="remote_dpad_right"
              onClick={() => dispatchKey('KEYCODE_DPAD_RIGHT', 22)}
              className="absolute right-1 w-12 h-14 flex items-center justify-center text-gray-200 hover:text-[#FFD54F] active:scale-95 transition-transform"
              title="D-Pad RIGHT (22)"
            >
              ▶
            </button>

            {/* D-Pad CENTER / OK (KeyCode 23) */}
            <button
              id="remote_dpad_center"
              onClick={() => dispatchKey('KEYCODE_DPAD_CENTER', 23)}
              className="w-16 h-16 rounded-full bg-gradient-to-br from-[#2D2D3A] to-[#1E1E28] border-2 border-[#FFD54F] text-[#FFD54F] font-black text-sm flex items-center justify-center shadow-lg active:scale-90 transition-transform z-10"
              title="OK / Center (23)"
            >
              OK
            </button>
          </div>

          {/* Action Row: BACK, HOME, MENU */}
          <div className="grid grid-cols-3 gap-2 w-full mt-4">
            <button
              id="remote_btn_back"
              onClick={() => dispatchKey('KEYCODE_BACK', 4)}
              className="py-2.5 bg-[#20202A] hover:bg-[#2C2C3A] text-gray-200 text-xs font-bold rounded-lg border border-[#343444] active:scale-95"
            >
              BACK
            </button>

            <button
              id="remote_btn_home"
              onClick={() => navigateTo('file:///android_asset/homepage.html')}
              className="py-2.5 bg-[#20202A] hover:bg-[#2C2C3A] text-[#E5A93C] text-xs font-bold rounded-lg border border-[#343444] active:scale-95"
            >
              HOME
            </button>

            <button
              id="remote_btn_menu"
              onClick={() => dispatchKey('KEYCODE_MENU', 82)}
              className="py-2.5 bg-[#20202A] hover:bg-[#2C2C3A] text-gray-200 text-xs font-bold rounded-lg border border-[#343444] active:scale-95"
            >
              MENU
            </button>
          </div>

          {/* Memory Stress Simulation Tool */}
          <div className="w-full mt-5 p-3 bg-[#181822] rounded-xl border border-[#282838] text-left">
            <div className="flex items-center justify-between text-xs font-bold text-gray-300 mb-2">
              <span className="flex items-center gap-1 text-[#E5A93C]">
                <Cpu className="w-3.5 h-3.5" /> RAM Test
              </span>
              <span className="text-[10px] font-mono text-gray-400">{usedHeapMB}MB / 128MB</span>
            </div>

            <div className="h-2 w-full bg-[#121218] rounded-full overflow-hidden mb-3">
              <div
                className={`h-full transition-all duration-300 ${
                  usedHeapMB > 100 ? 'bg-red-500' : usedHeapMB > 80 ? 'bg-amber-400' : 'bg-emerald-400'
                }`}
                style={{ width: `${(usedHeapMB / maxHeapMB) * 100}%` }}
              />
            </div>

            <div className="grid grid-cols-2 gap-1.5">
              <button
                onClick={() => setUsedHeapMB(prev => Math.min(125, prev + 25))}
                className="py-1 px-2 bg-[#262634] hover:bg-[#343446] text-amber-300 text-[10px] font-semibold rounded border border-[#3C3C4E]"
              >
                +25MB Pressure
              </button>
              <button
                onClick={() => setUsedHeapMB(18)}
                className="py-1 px-2 bg-[#262634] hover:bg-[#343446] text-emerald-300 text-[10px] font-semibold rounded border border-[#3C3C4E]"
              >
                Reset RAM
              </button>
            </div>
            <p className="text-[9px] text-gray-400 mt-2 leading-tight">
              Pushing above 98MB triggers automatic Dalvik background tab eviction.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
