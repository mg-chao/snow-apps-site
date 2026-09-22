import { useSyncExternalStore } from 'react';

export type DownloadPlatform = 'windows' | 'macos';

type NavigatorWithHints = Navigator & {
  userAgentData?: { platform?: string };
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
