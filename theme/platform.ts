import { useSyncExternalStore } from 'react';

export type DownloadPlatform = 'windows' | 'macos';
export type DownloadArchitecture = 'x64' | 'arm64';
export type DownloadTarget = {
  platform: DownloadPlatform;
  architecture: DownloadArchitecture | null;
};

type NavigatorWithHints = Navigator & {
  userAgentData?: {
    platform?: string;
    getHighEntropyValues?: (hints: string[]) => Promise<{
      architecture?: string;
      bitness?: string;
    }>;
  };
};

function navigatorSource(): string {
  const nav = navigator as NavigatorWithHints;
  return `${nav.userAgentData?.platform ?? ''} ${nav.platform} ${nav.userAgent}`;
}

function isIosDevice(): boolean {
  const nav = navigator as NavigatorWithHints;
  return (
    /iPhone|iPad|iPod/i.test(nav.userAgent) ||
    (nav.platform === 'MacIntel' && nav.maxTouchPoints > 1)
  );
}

export function detectPreviewOs(): DownloadPlatform {
  if (typeof navigator === 'undefined') {
    return 'windows';
  }

  return /Mac|iPhone|iPad|iPod/i.test(navigatorSource()) ? 'macos' : 'windows';
}

export function detectDownloadPlatform(): DownloadPlatform {
  if (typeof navigator === 'undefined') {
    return 'windows';
  }

  if (isIosDevice()) {
    return 'windows';
  }

  return /Mac/i.test(navigatorSource()) ? 'macos' : 'windows';
}

export function readPlatformQuery(): DownloadPlatform | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const value = new URLSearchParams(window.location.search).get('os');
  return value === 'windows' || value === 'macos' ? value : null;
}

export function readArchitectureQuery(): DownloadArchitecture | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const value = new URLSearchParams(window.location.search).get('arch');
  return value === 'x64' || value === 'arm64' ? value : null;
}

let hintedArchitecture: DownloadArchitecture | null = null;
let hintsRequested = false;
const architectureListeners = new Set<() => void>();

function isDesktopDevice(): boolean {
  return (
    typeof navigator !== 'undefined' &&
    !isIosDevice() &&
    !/Android/i.test(navigatorSource()) &&
    /Windows|Win32|Win64|Mac/i.test(navigatorSource())
  );
}

export function detectDownloadArchitecture(): DownloadArchitecture | null {
  if (!isDesktopDevice()) {
    return null;
  }

  if (hintedArchitecture) {
    return hintedArchitecture;
  }

  const source = navigatorSource();
  if (/\b(?:arm64|aarch64)\b/i.test(source)) {
    return 'arm64';
  }
  // MacIntel and "Intel Mac OS X" are also reported by Apple silicon browsers.
  if (
    detectDownloadPlatform() === 'windows' &&
    /\b(?:Win64|WOW64|x64|x86_64|AMD64)\b/i.test(source)
  ) {
    return 'x64';
  }
  return null;
}

async function requestArchitectureHints() {
  if (hintsRequested || !isDesktopDevice()) {
    return;
  }
  hintsRequested = true;
  const data = (navigator as NavigatorWithHints).userAgentData;
  if (!data?.getHighEntropyValues) {
    return;
  }

  try {
    const hints = await data.getHighEntropyValues(['architecture', 'bitness']);
    if (hints.bitness === '64') {
      if (/^(?:arm|arm64|aarch64)$/i.test(hints.architecture ?? '')) {
        hintedArchitecture = 'arm64';
      } else if (/^(?:x86|x64|x86_64|amd64)$/i.test(hints.architecture ?? '')) {
        hintedArchitecture = 'x64';
      }
    }
    if (hintedArchitecture) {
      for (const listener of architectureListeners) {
        listener();
      }
    }
  } catch {
    // Browsers may deny CPU hints; keep the manual architecture choice available.
  }
}

function subscribeArchitecture(listener: () => void) {
  architectureListeners.add(listener);
  void requestArchitectureHints();
  return () => {
    architectureListeners.delete(listener);
  };
}

const serverArchitecture = () => null;

function useDownloadArchitecture(): DownloadArchitecture | null {
  return useSyncExternalStore(
    subscribeArchitecture,
    detectDownloadArchitecture,
    serverArchitecture,
  );
}

function subscribePlatform() {
  return () => undefined;
}

const serverPlatform = () => 'windows' as const;

export function usePreviewOs(): DownloadPlatform {
  return useSyncExternalStore(
    subscribePlatform,
    detectPreviewOs,
    serverPlatform,
  );
}

export function useDownloadPlatform(): DownloadPlatform {
  return useSyncExternalStore(
    subscribePlatform,
    detectDownloadPlatform,
    serverPlatform,
  );
}

function resolveDownloadPlatform(): DownloadPlatform {
  return readPlatformQuery() ?? detectDownloadPlatform();
}

export function useResolvedDownloadPlatform(): DownloadPlatform {
  return useSyncExternalStore(
    subscribePlatform,
    resolveDownloadPlatform,
    serverPlatform,
  );
}

export function useDownloadTarget(): DownloadTarget {
  const platform = useDownloadPlatform();
  const architecture = useDownloadArchitecture();
  return { platform, architecture };
}

export function useResolvedDownloadTarget(): DownloadTarget {
  const platform = useResolvedDownloadPlatform();
  const detected = useDownloadTarget();
  const architecture =
    readArchitectureQuery() ??
    (platform === detected.platform ? detected.architecture : null);
  return { platform, architecture };
}

export function downloadPageUrl(locale: 'en' | 'zh', target: DownloadTarget) {
  const params = new URLSearchParams({ os: target.platform });
  if (target.architecture) {
    params.set('arch', target.architecture);
  }
  return `${locale === 'zh' ? '/zh/download' : '/download'}?${params}`;
}
