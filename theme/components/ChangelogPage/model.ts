import snapshot from './releases.json';

export type Locale = 'en' | 'zh';
export type Channel = 'stable' | 'preview' | 'all';
export type Release = (typeof snapshot.releases)[number];

// Normalize legacy names on display, including after a release snapshot refresh.
function normalizeCaptureTerms(notes: string) {
  return notes
    .replace(/智能选择|智能选区|控件截图/g, '智能框选')
    .replace(/\bsmart selection\b/gi, 'Smart Selection');
}

export const releases = snapshot.releases.map((release) => ({
  ...release,
  notes: {
    zh: normalizeCaptureTerms(release.notes.zh),
    en: normalizeCaptureTerms(release.notes.en),
  },
}));
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
