import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { it } from 'node:test';
import { sitemapXml } from '../scripts/seo-build.ts';
import {
  indexNowPayload,
  submitIndexNow,
} from '../scripts/submit-indexnow.mjs';
import {
  applicationSchema,
  breadcrumbSchema,
  canonicalUrl,
  defaultLanguageUrl,
  pageBreadcrumbs,
  websiteSchema,
} from '../theme/seo.ts';
import { footerSections, siteLinks } from '../theme/site-structure.ts';
import { afterSearch, guideSearchHref } from '../theme/guide-search.ts';

it('keeps guide search results directly addressable while preserving sections and ranking', () => {
  assert.equal(
    guideSearchHref('/zh/guides/annotations/distance#scale'),
    '/zh/guides/annotations/distance.html#scale',
  );
  assert.equal(guideSearchHref('/zh/guides/'), '/zh/guides/index.html');
  assert.equal(guideSearchHref('/zh/download'), '/zh/download');
  const result = [
    {
      group: 'title',
      result: [{ link: '/zh/guides/annotations/distance', title: 'Distance' }],
    },
  ];
  assert.equal(afterSearch('distance', result), undefined);
  assert.equal(result.length, 1);
  assert.equal(
    result[0].result[0].link,
    '/zh/guides/annotations/distance.html',
  );
  assert.equal(result[0].result[0].title, 'Distance');
});

it('consolidates homepage, directory and download variants without query parameters', () => {
  for (const path of ['/', '/index', '/index.html']) {
    assert.equal(canonicalUrl(path), 'https://snowshot.top/index.html');
  }
  for (const path of ['/zh', '/zh/', '/zh/index.html']) {
    assert.equal(canonicalUrl(path), 'https://snowshot.top/zh/index.html');
  }
  for (const path of [
    '/download',
    '/download/',
    '/download.html',
    '/download?os=macos&arch=arm64#full',
  ]) {
    assert.equal(canonicalUrl(path), 'https://snowshot.top/download.html');
  }
  assert.equal(
    canonicalUrl('/zh/guides/'),
    'https://snowshot.top/zh/guides/index.html',
  );
  assert.equal(
    defaultLanguageUrl('/zh/guides/index.html'),
    'https://snowshot.top/guides/index.html',
  );
  assert.equal(
    defaultLanguageUrl('/zh/guides/annotations/arrows.html'),
    'https://snowshot.top/guides/annotations/arrows.html',
  );
  assert.equal(
    defaultLanguageUrl('/zh/download.html'),
    'https://snowshot.top/download.html',
  );
});

it('redirects every configured alias to its canonical route while retaining download parameters', () => {
  const config = readFileSync(
    new URL('../deploy/nginx-seo-redirects.conf', import.meta.url),
    'utf8',
  );
  const rules = [
    ...config.matchAll(
      /location = (\S+) \{ return 301 (\S+)\$is_args\$args; \}/g,
    ),
  ];
  assert.ok(rules.length >= 31);
  for (const prefix of ['', '/zh']) {
    for (const suffix of ['', '/', '/index']) {
      assert.ok(rules.some(([, alias]) => alias === `${prefix}/blog${suffix}`));
    }
  }
  for (const [, alias, destination] of rules) {
    assert.equal(destination, canonicalUrl(alias));
    assert.notEqual(
      new URL(destination).pathname,
      alias,
      `Redirect loop at ${alias}`,
    );
    assert.ok(!/api|setup|npm|plugins/.test(alias));
  }
});

it('consolidates changelog aliases and release fragments in both languages', () => {
  for (const prefix of ['', '/zh']) {
    for (const suffix of ['', '/', '.html', '.html#v1-5-2']) {
      assert.equal(
        canonicalUrl(`${prefix}/changelog${suffix}`),
        `https://snowshot.top${prefix}/changelog.html`,
      );
    }
  }
  assert.equal(
    defaultLanguageUrl('/zh/changelog.html#v1-5-2'),
    'https://snowshot.top/changelog.html',
  );
});

it('emits a unique sitemap of canonical pages excluding errors', () => {
  const xml = sitemapXml([
    '/',
    '/index.html',
    '/zh/',
    '/guides/',
    '/404',
    '/zh/404.html',
  ]);
  assert.equal((xml.match(/<loc>/g) ?? []).length, 3);
  assert.ok(!xml.includes('404'));
  assert.ok(xml.includes('https://snowshot.top/guides/index.html'));
});

it('identifies the official application and repository without invented ratings', () => {
  for (const locale of ['en', 'zh']) {
    const data = applicationSchema(locale);
    assert.equal(data.sameAs, 'https://github.com/mg-chao/snow-shot');
    assert.equal(data.offers.price, '0');
    assert.ok(!('aggregateRating' in data));
    assert.ok(
      data.url.includes(locale === 'zh' ? '/zh/index.html' : '/index.html'),
    );
  }
});

it('declares a consistent domain-level site name on either homepage', () => {
  const website = websiteSchema();
  assert.equal(website['@type'], 'WebSite');
  assert.equal(website.url, 'https://snowshot.top/');
  assert.equal(website.name, 'Snow Shot');
  assert.equal(website.alternateName, 'SnowShot');
});

it('uses real manual pages as breadcrumb parents without inventing directory routes', () => {
  for (const locale of ['en', 'zh']) {
    const prefix = locale === 'zh' ? '/zh' : '';
    const links = siteLinks(locale);
    assert.deepEqual(pageBreadcrumbs(`${prefix}/`, locale, 'Snow Shot'), []);
    assert.deepEqual(pageBreadcrumbs(links.home.href, locale, 'Snow Shot'), []);
    assert.deepEqual(pageBreadcrumbs(links.guides.href, locale, 'Manual'), [
      links.home,
      { label: 'Manual', href: links.guides.href },
    ]);
    const crumbs = pageBreadcrumbs(
      `${prefix}/guides/recognition/text.html?mode=offline#copy`,
      locale,
      'Text recognition',
    );
    assert.deepEqual(crumbs, [
      links.home,
      links.guides,
      {
        label: 'Text recognition',
        href: `${prefix}/guides/recognition/text.html`,
      },
    ]);
    const schema = breadcrumbSchema(crumbs);
    assert.equal(schema['@type'], 'BreadcrumbList');
    assert.deepEqual(
      schema.itemListElement.map((item) => item.position),
      [1, 2, 3],
    );
    assert.equal(
      schema.itemListElement[2].item,
      `https://snowshot.top${prefix}/guides/recognition/text.html`,
    );
    assert.equal(
      pageBreadcrumbs(`${prefix}/download?os=macos`, locale, 'Download').length,
      2,
    );
  }
});

it('keeps the footer directory mirrored between languages with unique canonical targets', () => {
  const english = footerSections('en').flatMap((section) => section.links);
  const chinese = footerSections('zh').flatMap((section) => section.links);
  assert.equal(new Set(english.map((link) => link.href)).size, english.length);
  assert.equal(english.length, chinese.length);
  for (const [index, link] of english.entries()) {
    assert.equal(chinese[index].href, `/zh${link.href}`);
    assert.notEqual(chinese[index].label, link.label);
    assert.equal(canonicalUrl(link.href), `https://snowshot.top${link.href}`);
  }
});

it('uses the same link labels in navigation, sidebars and shared page entries', () => {
  for (const locale of ['en', 'zh']) {
    const links = siteLinks(locale);
    const nav = JSON.parse(
      readFileSync(
        new URL(`../docs/${locale}/_nav.json`, import.meta.url),
        'utf8',
      ),
    );
    for (const [index, key] of [
      'guides',
      'download',
      'blog',
      'changelog',
      'about',
    ].entries()) {
      assert.equal(nav[index].text, links[key].label);
    }
    for (const [key, link] of Object.entries(links)) {
      const path = link.href.replace(/^\/zh\//, '/');
      if (!path.startsWith('/guides/')) continue;
      const directory = path.slice(0, path.lastIndexOf('/'));
      const page = path.slice(path.lastIndexOf('/') + 1, -5);
      const meta = JSON.parse(
        readFileSync(
          new URL(`../docs/${locale}${directory}/_meta.json`, import.meta.url),
          'utf8',
        ),
      );
      assert.equal(
        meta.find((item) => item.name === page)?.label,
        link.label,
        `${locale} ${key}`,
      );
    }
  }
});

const key = 'test-indexnow-123456';
const sitemap = sitemapXml(['/', '/zh/']);
const submission = {
  previous: { schema: 1, pages: {} },
  current: {
    schema: 1,
    pages: Object.fromEntries(
      [
        'https://snowshot.top/index.html',
        'https://snowshot.top/zh/index.html',
      ].map((url) => [url, { hash: 'a'.repeat(64) }]),
    ),
  },
};

it('refuses empty, invalid-key or unowned-host IndexNow submissions', () => {
  assert.throws(() => indexNowPayload('<urlset/>', key), /Expected/);
  assert.throws(() => indexNowPayload(sitemap, 'bad'), /key/);
  assert.throws(
    () =>
      indexNowPayload('<loc>https://github.com/mg-chao/snow-shot</loc>', key),
    /canonical/,
  );
  assert.throws(
    () =>
      indexNowPayload(
        '<loc>https://snowshot.top/download.html?os=macos</loc>',
        key,
      ),
    /canonical/,
  );
});

it('verifies the live key before sending URLs, and distinguishes 202 from indexing', async () => {
  const calls = [];
  const request = async (url, options) => {
    calls.push({ url, options });
    if (url.endsWith('/indexnow.txt')) return new Response(key);
    if (url.endsWith('/seo-manifest.json'))
      return Response.json(submission.current);
    return new Response('', { status: 202 });
  };
  assert.deepEqual(await submitIndexNow(key, request, submission), {
    status: 202,
    submitted: 2,
    attempts: 1,
    urls: [
      'https://snowshot.top/index.html',
      'https://snowshot.top/zh/index.html',
    ],
  });
  assert.equal(calls.length, 3);
  assert.equal(calls[2].options.method, 'POST');
  assert.deepEqual(JSON.parse(calls[2].options.body).urlList, [
    'https://snowshot.top/index.html',
    'https://snowshot.top/zh/index.html',
  ]);
  let requests = 0;
  await assert.rejects(
    submitIndexNow(
      key,
      async () => {
        requests++;
        return new Response('different-key');
      },
      submission,
    ),
    /Deploy first/,
  );
  assert.equal(requests, 1);
});

it('reports failed submissions rather than treating any 2xx/4xx response as success', async () => {
  await assert.rejects(
    submitIndexNow(
      key,
      async (url) => {
        if (url.endsWith('/indexnow.txt')) return new Response(key);
        if (url.endsWith('/seo-manifest.json'))
          return Response.json(submission.current);
        return new Response('', { status: 429 });
      },
      { ...submission, maxAttempts: 1 },
    ),
    /HTTP 429/,
  );
});
