export const siteOrigin = 'https://snowshot.top';
export const repositoryUrl = 'https://github.com/mg-chao/snow-shot';

// Match Rspress's existing .html routes, including directory index pages.
// Query parameters select a download variant, not a different document.
export function canonicalUrl(path: string) {
  let pathname = new URL(path, siteOrigin).pathname;
  // These document aliases are also redirected by the production web server.
  pathname = pathname.replace(
    /^(\/(?:zh\/)?(?:about|changelog|download|privacy|terms))\/$/,
    '$1',
  );
  if (
    pathname === '/zh' ||
    pathname === '/guides' ||
    pathname === '/zh/guides'
  ) {
    pathname += '/';
  }
  if (pathname.endsWith('/')) pathname += 'index.html';
  else if (!pathname.endsWith('.html')) pathname += '.html';
  return `${siteOrigin}${pathname}`;
}

export function defaultLanguageUrl(path: string) {
  const pathname =
    new URL(path, siteOrigin).pathname.replace(/^\/zh(?=\/|$)/, '') || '/';
  return canonicalUrl(pathname);
}

export function applicationSchema(locale: 'en' | 'zh') {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    '@id': `${siteOrigin}/#snow-shot`,
    name: 'Snow Shot',
    alternateName: 'SnowShot',
    url: canonicalUrl(locale === 'zh' ? '/zh/' : '/'),
    sameAs: repositoryUrl,
    downloadUrl: `${repositoryUrl}/releases/latest`,
    applicationCategory: 'UtilitiesApplication',
    operatingSystem: 'Windows, macOS 15 or later',
    license: `${repositoryUrl}/blob/main/snow_shot/COPYRIGHT`,
    image: `${siteOrigin}/images/app-icon.webp`,
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      locale === 'zh'
        ? '免费开源截图工具，支持 Windows 和 macOS，提供截图标注、滚动长截图、本地文本识别、贴图与录屏。'
        : 'Free, open-source screenshot tool for Windows and macOS with annotation, scrolling capture, local text recognition, pinning and screen recording.',
  };
}
