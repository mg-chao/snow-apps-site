import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  utimesSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { it } from 'node:test';
import { contentMetadata } from '../scripts/content-metadata.ts';
import {
  buildManifest,
  contentFingerprint,
  pageFingerprint,
} from '../scripts/seo-manifest.ts';
import { rehypeImages } from '../scripts/rehype-images.ts';
import { sitemapXml } from '../scripts/seo-build.ts';
import {
  changedUrls,
  snapshotWebsite,
  submitIndexNow,
  urlPayload,
} from '../scripts/submit-indexnow.mjs';
import { articleSchema } from '../theme/seo.ts';

const origin = 'https://snowshot.top';
const key = 'test-indexnow-123456';
const page = (slug, hash) => [
  `${origin}/${slug}.html`,
  { hash: hash.repeat(64) },
];
const manifest = (...pages) => ({
  schema: 1,
  pages: Object.fromEntries(pages),
});

it('dates survive a fresh checkout and include actual imported component/image changes', () => {
  const root = mkdtempSync(join(tmpdir(), 'snow-seo-history-'));
  const git = (...args) =>
    execFileSync('git', args, {
      cwd: root,
      encoding: 'utf8',
      env: {
        ...process.env,
        GIT_AUTHOR_DATE: '2026-01-01T10:00:00Z',
        GIT_COMMITTER_DATE: '2026-01-01T10:00:00Z',
      },
    });
  try {
    mkdirSync(join(root, 'docs/en'), { recursive: true });
    mkdirSync(join(root, 'theme'), { recursive: true });
    const doc = join(root, 'docs/en/task.mdx');
    const component = join(root, 'theme/Example.tsx');
    writeFileSync(
      doc,
      "import { Example } from '../../theme/Example';\n# Task\n<Example />",
    );
    writeFileSync(component, 'export const Example = () => null;');
    git('init', '-q');
    git('add', '.');
    git(
      '-c',
      'user.name=SEO test',
      '-c',
      'user.email=seo@example.test',
      'commit',
      '-qm',
      'initial',
    );
    // Checkout timestamps must not masquerade as content modification dates.
    utimesSync(doc, new Date('2026-04-01'), new Date('2026-04-01'));
    assert.equal(
      contentMetadata(root)(doc).lastModified,
      '2026-01-01T10:00:00.000Z',
    );
    writeFileSync(
      component,
      'export const Example = () => "Updated instructions";',
    );
    utimesSync(component, new Date('2026-02-01'), new Date('2026-02-01'));
    assert.equal(
      contentMetadata(root)(doc).lastModified,
      '2026-02-01T00:00:00.000Z',
    );
    const xml = sitemapXml(
      ['/task'],
      new Map([[`${origin}/task.html`, '2026-02-01T08:00:00+08:00']]),
    );
    assert.match(xml, /<lastmod>2026-02-01T00:00:00.000Z<\/lastmod>/);
    assert.equal(sitemapXml(['/task'], new Map()), sitemapXml(['/task']));
  } finally {
    assert.ok(root.startsWith(join(tmpdir(), 'snow-seo-history-')));
    rmSync(root, { recursive: true, force: true });
  }
});

it('fingerprints ignore script/stylesheet rebuilds but retain text, schema and image changes', () => {
  const html =
    '<link rel="stylesheet" href="/a.css"><script src="/a.js"></script><h1>Task</h1><script type="application/ld+json">{"name":"Task"}</script>';
  assert.equal(
    pageFingerprint(html),
    pageFingerprint(html.replaceAll('/a.', '/b.')),
  );
  assert.notEqual(
    pageFingerprint(html),
    pageFingerprint(html.replace('<h1>Task', '<h1>New task')),
  );
  assert.notEqual(
    pageFingerprint(html),
    pageFingerprint(html.replace('"name":"Task"', '"name":"Changed"')),
  );
  const root = mkdtempSync(join(tmpdir(), 'snow-seo-manifest-'));
  try {
    mkdirSync(join(root, 'images'));
    writeFileSync(
      join(root, 'index.html'),
      '<h1>Task</h1><img src="/images/example.svg">',
    );
    writeFileSync(join(root, 'images/example.svg'), '<svg>before</svg>');
    const before = buildManifest(root, [{ path: '/' }]);
    writeFileSync(join(root, 'images/example.svg'), '<svg>after</svg>');
    assert.deepEqual(
      changedUrls(before, buildManifest(root, [{ path: '/' }])),
      [`${origin}/index.html`],
    );
  } finally {
    assert.ok(root.startsWith(join(tmpdir(), 'snow-seo-manifest-')));
    rmSync(root, { recursive: true, force: true });
  }
});

it('IndexNow sends additions, modifications and removals, skipping unchanged pages', async () => {
  const before = manifest(
    page('keep', 'a'),
    page('edit', 'a'),
    page('remove', 'a'),
  );
  const after = manifest(
    page('keep', 'a'),
    page('edit', 'b'),
    page('new', 'c'),
  );
  assert.deepEqual(
    changedUrls(before, after),
    ['edit', 'new', 'remove'].map((x) => `${origin}/${x}.html`),
  );
  const calls = [];
  const request = async (url, options) => {
    calls.push([url, options]);
    if (url.endsWith('/indexnow.txt')) return new Response(key);
    if (url.endsWith('/seo-manifest.json')) return Response.json(after);
    if (url.endsWith('/remove.html')) return new Response('', { status: 404 });
    return new Response('', { status: 200 });
  };
  const result = await submitIndexNow(key, request, {
    previous: before,
    current: after,
  });
  assert.equal(result.submitted, 3);
  assert.equal(calls.at(-2)[1].method, 'HEAD');
  assert.deepEqual(JSON.parse(calls.at(-1)[1].body).urlList, result.urls);
  calls.length = 0;
  assert.equal(
    (await submitIndexNow(key, request, { previous: after, current: after }))
      .submitted,
    0,
  );
  assert.equal(
    calls.some(([url]) => url.includes('api.indexnow')),
    false,
  );
});

it('IndexNow refuses stale deployments and pages incorrectly claimed as deleted', async () => {
  const before = manifest(page('old', 'a'));
  const after = manifest(page('new', 'b'));
  const request = async (url) => {
    if (url.endsWith('/indexnow.txt')) return new Response(key);
    if (url.endsWith('/seo-manifest.json')) return Response.json(before);
    throw new Error('Must not submit');
  };
  await assert.rejects(
    submitIndexNow(key, request, { previous: before, current: after }),
    /Deploy first/,
  );
  await assert.rejects(
    submitIndexNow(
      key,
      async (url) => {
        if (url.endsWith('/seo-manifest.json')) return Response.json(after);
        if (url.endsWith('/old.html')) return new Response('Still here');
        return request(url);
      },
      { previous: before, current: after },
    ),
    /still serves content/,
  );
  for (const url of [
    'https://other.test/a.html',
    `${origin}/task`,
    `${origin}/task.html?x=1`,
  ]) {
    assert.throws(() => urlPayload([url], key), /canonical/);
  }
});

it('IndexNow requires valid deployment snapshots before making any request', async () => {
  const current = manifest(page('index', 'a'));
  const request = async () => assert.fail('Must validate snapshots first');
  for (const settings of [
    {},
    { current },
    { previous: current },
    { previous: current, current: manifest() },
  ]) {
    await assert.rejects(
      submitIndexNow(key, request, settings),
      /pre-deployment snapshot/,
    );
  }
  for (const pages of [true, 'invalid', []]) {
    await assert.rejects(
      submitIndexNow(key, request, {
        previous: { schema: 1, pages },
        current,
      }),
      /Invalid SEO manifest/,
    );
  }
});

it('IndexNow bounds retries, honors Retry-After and does not retry permanent errors', async () => {
  const current = manifest(page('index', 'a'));
  let posts = 0;
  const waits = [];
  const request = async (url) => {
    if (url.endsWith('/indexnow.txt')) return new Response(key);
    if (url.endsWith('/seo-manifest.json')) return Response.json(current);
    posts++;
    return new Response('', {
      status: posts === 1 ? 429 : 202,
      headers: { 'Retry-After': '2' },
    });
  };
  const settings = {
    previous: manifest(),
    current,
    sleep: async (ms) => waits.push(ms),
  };
  const result = await submitIndexNow(key, request, settings);
  assert.equal(result.status, 202);
  assert.equal(result.attempts, 2);
  assert.deepEqual(waits, [2000]);
  posts = 0;
  await assert.rejects(
    submitIndexNow(
      key,
      async (url) => {
        if (url.includes('api.indexnow')) {
          posts++;
          return new Response('', { status: 403 });
        }
        return request(url);
      },
      settings,
    ),
    /HTTP 403/,
  );
  assert.equal(posts, 1);
});

it('captures a legacy live site before its first manifest deployment', async () => {
  const result = await snapshotWebsite(async (url) => {
    if (url.endsWith('/seo-manifest.json'))
      return new Response('', { status: 404 });
    if (url.endsWith('/sitemap.xml')) return new Response(sitemapXml(['/']));
    return new Response('<h1>Legacy content</h1>');
  });
  assert.equal(
    result.pages[`${origin}/index.html`].hash,
    contentFingerprint('<h1>Legacy content</h1>', []),
  );
  await assert.rejects(
    snapshotWebsite(async () => new Response('', { status: 503 })),
    /HTTP 503/,
  );
});

it('legacy snapshots and build manifests fingerprint unchanged illustrated pages identically', async () => {
  const root = mkdtempSync(join(tmpdir(), 'snow-seo-legacy-'));
  try {
    mkdirSync(join(root, 'images'));
    const html = '<h1>Task</h1><img src="/images/example.svg">';
    const illustration = '<svg>illustration</svg>';
    writeFileSync(join(root, 'index.html'), html);
    writeFileSync(join(root, 'images/example.svg'), illustration);
    const before = await snapshotWebsite(async (url) => {
      if (url.endsWith('/seo-manifest.json'))
        return new Response('', { status: 404 });
      if (url.endsWith('/sitemap.xml')) return new Response(sitemapXml(['/']));
      if (url.endsWith('/images/example.svg'))
        return new Response(illustration);
      return new Response(html);
    });
    assert.deepEqual(
      changedUrls(before, buildManifest(root, [{ path: '/' }])),
      [],
    );
  } finally {
    assert.ok(root.startsWith(join(tmpdir(), 'snow-seo-legacy-')));
    rmSync(root, { recursive: true, force: true });
  }
});

it('sets intrinsic image sizes and defers only subsequent content images', () => {
  const img = () => ({
    type: 'element',
    tagName: 'img',
    properties: { src: '/images/app-icon.webp' },
  });
  const first = img(),
    second = img();
  const tree = {
    type: 'root',
    children: [first, { type: 'element', tagName: 'p', children: [second] }],
  };
  rehypeImages()(tree);
  assert.ok(first.properties.width > 0 && first.properties.height > 0);
  assert.equal(first.properties.loading, 'eager');
  assert.equal(second.properties.loading, 'lazy');
  assert.equal(second.properties.decoding, 'async');
});

it('article metadata keeps real dates, publisher identity and the article illustration', () => {
  const schema = articleSchema({
    title: 'OCR help',
    path: '/zh/blog/ocr',
    locale: 'zh',
    date: '2026-11-09',
    modified: '2026-11-10T12:00:00.000Z',
    image: '/images/blog/ocr.webp',
  });
  assert.equal(schema['@type'], 'BlogPosting');
  assert.equal(schema.author.url, `${origin}/zh/about.html`);
  assert.equal(schema.datePublished, '2026-11-09');
  assert.equal(schema.image, `${origin}/images/blog/ocr.webp`);
  assert.equal(schema.mainEntityOfPage, `${origin}/zh/blog/ocr.html`);
  assert.ok(!JSON.stringify(schema).includes('aggregateRating'));
});

it('publishing snapshots before deployment and notifies only after health checks', () => {
  const source = readFileSync(
    new URL('../scripts/publish-release.ps1', import.meta.url),
    'utf8',
  );
  assert.ok(
    source.indexOf("'indexnow', 'snapshot'") <
      source.indexOf('Invoke-SiteTool scp'),
  );
  assert.ok(
    source.indexOf("'indexnow', 'submit'") >
      source.indexOf('Public website receipt does not match'),
  );
  assert.ok(
    source.indexOf("'indexnow', 'submit'") >
      source.indexOf('Website health check failed'),
  );
  assert.match(source, /Website is deployed; IndexNow notification failed/);
});
