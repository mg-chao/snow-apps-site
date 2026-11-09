import { useHead, useLang, useLocation, usePage } from '@rspress/core/runtime';
import { useEffect } from 'react';
import {
  applicationSchema,
  canonicalUrl,
  defaultLanguageUrl,
  siteOrigin,
} from '../seo';

export function SeoMetadata() {
  const { pathname } = useLocation();
  const { page } = usePage();
  const locale = useLang() === 'zh' ? 'zh' : 'en';
  const isMissing = page.pageType === '404';

  // Rspress renders these links for direct requests but leaves them unchanged
  // during client-side navigation. Keep the server-rendered pair in sync.
  useEffect(() => {
    if (isMissing) return;
    const english = defaultLanguageUrl(pathname);
    for (const lang of ['en', 'zh']) {
      document.head
        .querySelector(`link[rel="alternate"][hreflang="${lang}"]`)
        ?.setAttribute(
          'href',
          lang === 'en'
            ? english
            : english.replace(siteOrigin, `${siteOrigin}/zh`),
        );
    }
  }, [pathname, isMissing]);

  useHead({
    link: isMissing
      ? []
      : [
          { key: 'canonical', rel: 'canonical', href: canonicalUrl(pathname) },
          {
            key: 'x-default',
            rel: 'alternate',
            hreflang: 'x-default',
            href: defaultLanguageUrl(pathname),
          },
        ],
    meta: isMissing
      ? [{ name: 'robots', content: 'noindex' }]
      : [
          { property: 'og:url', content: canonicalUrl(pathname) },
          { property: 'og:site_name', content: 'Snow Shot' },
          {
            property: 'og:image',
            content: `${siteOrigin}/images/app-icon.webp`,
          },
          { property: 'og:image:alt', content: 'Snow Shot app icon' },
          { name: 'twitter:card', content: 'summary' },
        ],
    script:
      page.pageType === 'home'
        ? [
            {
              key: 'snow-shot-software',
              type: 'application/ld+json',
              innerHTML: JSON.stringify(applicationSchema(locale)),
            },
          ]
        : [],
  });
  return null;
}
