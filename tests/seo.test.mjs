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
  canonicalUrl,
  defaultLanguageUrl,
} from '../theme/seo.ts';

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
  assert.equal(rules.length, 27);
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
    assert.equal(data.sameAs, 'https://github.com/mg-chao/snow-apps');
    assert.equal(data.offers.price, '0');
    assert.ok(!('aggregateRating' in data));
    assert.ok(
      data.url.includes(locale === 'zh' ? '/zh/index.html' : '/index.html'),
    );
  }
});

const key = 'test-indexnow-123456';
const sitemap = sitemapXml(['/', '/zh/']);

it('refuses empty, invalid-key or unowned-host IndexNow submissions', () => {
  assert.throws(() => indexNowPayload('<urlset/>', key), /Expected/);
  assert.throws(() => indexNowPayload(sitemap, 'bad'), /key/);
  assert.throws(
    () =>
      indexNowPayload('<loc>https://github.com/mg-chao/snow-apps</loc>', key),
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
    if (url.endsWith('/sitemap.xml')) return new Response(sitemap);
    return new Response('', { status: 202 });
  };
  assert.deepEqual(await submitIndexNow(key, request), {
    status: 202,
    submitted: 2,
  });
  assert.equal(calls.length, 3);
  assert.equal(calls[2].options.method, 'POST');
  assert.deepEqual(JSON.parse(calls[2].options.body).urlList, [
    'https://snowshot.top/index.html',
    'https://snowshot.top/zh/index.html',
  ]);
  let requests = 0;
  await assert.rejects(
    submitIndexNow(key, async () => {
      requests++;
      return new Response('different-key');
    }),
    /Deploy first/,
  );
  assert.equal(requests, 1);
});

it('reports failed submissions rather than treating any 2xx/4xx response as success', async () => {
  await assert.rejects(
    submitIndexNow(key, async (url) => {
      if (url.endsWith('/indexnow.txt')) return new Response(key);
      if (url.endsWith('/sitemap.xml')) return new Response(sitemap);
      return new Response('', { status: 429 });
    }),
    /HTTP 429/,
  );
});
