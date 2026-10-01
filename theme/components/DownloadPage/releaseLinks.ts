const giteeRepository = 'https://gitee.com/mg-chao/snow-apps';
const githubRepository = 'https://github.com/mg-chao/snow-apps';

export const giteeReleases = `${giteeRepository}/releases/latest`;
export const githubReleases = `${githubRepository}/releases/latest`;

// scripts/publish-release.ps1 synchronizes this with the target Snow Shot release.
export const releaseVersion = '1.1.9';
const releaseTag = `v${releaseVersion}_snow-shot`;

export const releaseAssets = {
  windowsOnline: `snow-shot-${releaseVersion}-windows-x64-online.exe`,
  windowsOffline: `snow-shot-${releaseVersion}-windows-x64-offline.exe`,
  windowsPortable: `snow-shot-${releaseVersion}-windows-x64-portable.zip`,
  macosDmg: `snow-shot-${releaseVersion}-macos-arm64.dmg`,
  windowsMiniOnline: `snow-shot-mini-${releaseVersion}-windows-x64-online.exe`,
  windowsMiniPortable: `snow-shot-mini-${releaseVersion}-windows-x64-portable.zip`,
  macosMiniDmg: `snow-shot-mini-${releaseVersion}-macos-arm64.dmg`,
} as const;

export type ReleaseAsset = keyof typeof releaseAssets;

export function releaseDownloadUrl(locale: 'en' | 'zh', asset: ReleaseAsset) {
  const repository = locale === 'zh' ? giteeRepository : githubRepository;
  return `${repository}/releases/download/${releaseTag}/${releaseAssets[asset]}`;
}
