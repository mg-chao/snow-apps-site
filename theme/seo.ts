import { type SiteLink, type SiteLocale, siteLinks } from './site-structure.ts';

export const siteOrigin = 'https://snowshot.top';
export const repositoryUrl = 'https://github.com/mg-chao/snow-shot';

export function articleAuthor(locale: 'en' | 'zh') {
  return {
    '@type': 'Organization',
    name: 'Snow Apps',
    url: canonicalUrl(locale === 'zh' ? '/zh/about.html' : '/about.html'),
  };
}

export function articleSchema(article: {
  title: string;
  description?: string;
  path: string;
  locale: 'en' | 'zh';
  date: string;
  modified?: string;
  image?: string;
}) {
  const url = canonicalUrl(article.path);
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    '@id': `${url}#article`,
    mainEntityOfPage: url,
    url,
    headline: article.title,
    description: article.description,
    inLanguage: article.locale === 'zh' ? 'zh-CN' : 'en',
    author: articleAuthor(article.locale),
    publisher: articleAuthor(article.locale),
    datePublished: article.date,
    ...(article.modified ? { dateModified: article.modified } : {}),
    ...(article.image
      ? { image: new URL(article.image, siteOrigin).href }
      : {}),
  };
}

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
    pathname === '/zh/guides' ||
    pathname === '/blog' ||
    pathname === '/zh/blog'
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

export function websiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${siteOrigin}/#website`,
    url: `${siteOrigin}/`,
    name: 'Snow Shot',
    alternateName: 'SnowShot',
    inLanguage: ['en', 'zh-CN'],
  };
}

export function pageBreadcrumbs(
  path: string,
  locale: SiteLocale,
  title: string,
): SiteLink[] {
  const links = siteLinks(locale);
  const url = canonicalUrl(path);
  if (url === canonicalUrl(links.home.href) || !title) return [];
  const items = [links.home];
  if (
    /^\/(?:zh\/)?guides\//.test(new URL(url).pathname) &&
    url !== canonicalUrl(links.guides.href)
  ) {
    items.push(links.guides);
  }
  if (
    /^\/(?:zh\/)?blog\//.test(new URL(url).pathname) &&
    url !== canonicalUrl(links.blog.href)
  ) {
    items.push(links.blog);
  }
  items.push({ label: title, href: new URL(url).pathname });
  return items;
}

export function breadcrumbSchema(items: SiteLink[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.label,
      item: canonicalUrl(item.href),
    })),
  };
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
