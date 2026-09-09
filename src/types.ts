export interface TabItem {
  id: string;
  url: string;
  title: string;
  isEvicted: boolean;
  history: string[];
  historyIndex: number;
}

export type MemoryState = 'NORMAL' | 'WARNING' | 'CRITICAL' | 'EMERGENCY';

export interface KeyLog {
  name: string;
  keyCode: number;
  action: 'ACTION_DOWN' | 'ACTION_UP';
  time: string;
}

export interface ApkDetails {
  filename: string;
  filesize: string;
  bytes: number;
  sha256: string;
  sdkMin: number;
  sdkTarget: number;
  signatures: string[];
  package: string;
  versionName: string;
  versionCode: number;
}
