import {
  useHead,
  useLang,
  useLocation,
  usePage,
  usePages,
} from '@rspress/core/runtime';
import { useEffect } from 'react';
import manropeLatin from '../fonts/files/manrope-latin-wght-normal.woff2?url';
import {
  applicationSchema,
  articleSchema,
  breadcrumbSchema,
  canonicalUrl,
  defaultLanguageUrl,
  pageBreadcrumbs,
  siteOrigin,
  websiteSchema,
} from '../seo';

export function SeoMetadata() {
  const { pathname } = useLocation();
  const { page } = usePage();
  const { pages } = usePages();
  const locale = useLang() === 'zh' ? 'zh' : 'en';
  const isMissing = page.pageType === '404';
  const breadcrumbs = pageBreadcrumbs(pathname, locale, page.title);
  // Build hooks extend the page index; compiled MDX frontmatter is independent.
  const metadata = pages.find(
    (item) => canonicalUrl(item.routePath) === canonicalUrl(pathname),
  )?.frontmatter;
  const article =
    page.frontmatter.blog === true
      ? articleSchema({
          title: page.title,
          description: page.description,
          path: pathname,
          locale,
          date: String(page.frontmatter.date),
          modified: metadata?.lastModified as string | undefined,
          image: metadata?.image as string | undefined,
        })
      : undefined;
  const socialImage = article?.image ?? `${siteOrigin}/images/app-icon.webp`;

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
          {
            key: 'manrope-latin',
            rel: 'preload',
            as: 'font',
            type: 'font/woff2',
            crossorigin: 'anonymous',
            href: manropeLatin,
          },
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
            content: socialImage,
          },
          {
            property: 'og:image:alt',
            content: article ? page.title : 'Snow Shot app icon',
          },
          { property: 'og:type', content: article ? 'article' : 'website' },
          {
            name: 'twitter:card',
            content: article?.image ? 'summary_large_image' : 'summary',
          },
          ...(article
            ? [
                {
                  property: 'article:published_time',
                  content: article.datePublished,
                },
                ...(article.dateModified
                  ? [
                      {
                        property: 'article:modified_time',
                        content: article.dateModified,
                      },
                    ]
                  : []),
              ]
            : []),
        ],
    script:
      page.pageType === 'home'
        ? [
            {
              key: 'snow-shot-software',
              type: 'application/ld+json',
              innerHTML: JSON.stringify(applicationSchema(locale)),
            },
            {
              key: 'snow-shot-website',
              type: 'application/ld+json',
              innerHTML: JSON.stringify(websiteSchema()),
            },
          ]
        : !isMissing && breadcrumbs.length > 1
          ? [
              {
                key: 'snow-shot-breadcrumbs',
                type: 'application/ld+json',
                innerHTML: JSON.stringify(breadcrumbSchema(breadcrumbs)),
              },
              ...(article
                ? [
                    {
                      key: 'snow-shot-article',
                      type: 'application/ld+json',
                      innerHTML: JSON.stringify(article),
                    },
                  ]
                : []),
            ]
          : [],
  });
  return null;
}
