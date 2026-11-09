import snapshot from './releases.json';

export type Locale = 'en' | 'zh';
export type Channel = 'stable' | 'preview' | 'all';
export type Release = (typeof snapshot.releases)[number];

export const releases = snapshot.releases;
export const latestRelease = releases.find((release) => !release.prerelease);

export function releaseId(release: Pick<Release, 'tag'>) {
  return `release-${release.tag}`;
}

export function filterReleases(channel: Channel, query: string) {
  const words = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  return releases.filter((release) => {
    if (channel === 'stable' && release.prerelease) return false;
    if (channel === 'preview' && !release.prerelease) return false;
    const text = [release.tag, release.name, ...Object.values(release.notes)]
      .join(' ')
      .toLocaleLowerCase();
    return words.every((word) => text.includes(word));
  });
}

export function formatReleaseDate(date: string, locale: Locale) {
  return new Intl.DateTimeFormat(locale === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: locale === 'zh' ? 'long' : 'short',
    day: 'numeric',
    timeZone: 'Asia/Shanghai',
  }).format(new Date(date));
}
