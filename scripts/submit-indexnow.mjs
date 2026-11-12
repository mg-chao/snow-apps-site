import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { pathToFileURL } from 'node:url';
import { canonicalUrl, siteOrigin } from '../theme/seo.ts';
import {
  isBlogPage,
  pageFingerprints,
  referencedImages,
} from './seo-manifest.ts';

export function indexNowPayload(sitemap, key) {
  return urlPayload(
    [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]),
    key,
  );
}

export function urlPayload(values, key) {
  if (!/^[a-zA-Z0-9-]{8,128}$/.test(key)) {
    throw new Error('Invalid IndexNow verification key.');
  }
  const urls = [...new Set(values)];
  if (!urls.length || urls.length > 10000) {
    throw new Error('Expected 1–10000 sitemap URLs.');
  }
  for (const value of urls) {
    const url = new URL(value);
    if (
      url.origin !== siteOrigin ||
      url.username ||
      url.password ||
      url.search ||
      url.hash ||
      canonicalUrl(value) !== value
    ) {
      throw new Error(`Only canonical URLs on ${siteOrigin} can be submitted.`);
    }
  }
  return {
    host: new URL(siteOrigin).host,
    key,
    keyLocation: `${siteOrigin}/indexnow.txt`,
    urlList: urls,
  };
}

export function validateManifest(manifest) {
  if (
    manifest?.schema !== 1 ||
    !manifest.pages ||
    typeof manifest.pages !== 'object' ||
    Array.isArray(manifest.pages)
  ) {
    throw new Error('Invalid SEO manifest.');
  }
  for (const [url, page] of Object.entries(manifest.pages)) {
    urlPayload([url], 'manifest-validation');
    if (
      !/^[a-f0-9]{64}$/.test(page?.hash) ||
      (page.contentHash !== undefined &&
        !/^[a-f0-9]{64}$/.test(page.contentHash))
    )
      throw new Error(`Invalid page fingerprint: ${url}`);
  }
  return manifest;
}

export function changedUrls(previous, current) {
  validateManifest(previous);
  validateManifest(current);
  return [
    ...new Set([...Object.keys(previous.pages), ...Object.keys(current.pages)]),
  ]
    .filter((url) => {
      const before = previous.pages[url];
      const after = current.pages[url];
      if (before?.contentHash && after?.contentHash)
        return before.contentHash !== after.contentHash;
      return before?.hash !== after?.hash;
    })
    .sort();
}

/** Capture before deployment, including a first-upgrade fallback for older sites. */
export async function snapshotWebsite(request = fetch) {
  const options = {
    signal: AbortSignal.timeout(30000),
    redirect: 'error',
    cache: 'no-store',
  };
  const response = await request(`${siteOrigin}/seo-manifest.json`, options);
  let pages = {};
  let urls;
  if (response.ok) {
    ({ pages } = validateManifest(await response.json()));
    // Older manifests store the full hash only. Reuse it for other pages and
    // fetch the live blog pages once to get comparable date-independent hashes.
    urls = Object.keys(pages).filter(
      (url) => !pages[url].contentHash && isBlogPage(url),
    );
  } else if (response.status === 404) {
    const sitemap = await request(`${siteOrigin}/sitemap.xml`, options);
    if (!sitemap.ok) throw new Error('Cannot snapshot live sitemap.');
    ({ urlList: urls } = indexNowPayload(
      await sitemap.text(),
      'snapshot-validation',
    ));
  } else {
    throw new Error(`Cannot snapshot live manifest: HTTP ${response.status}`);
  }
  const images = new Map();
  const imageBytes = (path) => {
    if (!images.has(path)) {
      images.set(
        path,
        (async () => {
          const image = await request(`${siteOrigin}${path}`, {
            ...options,
            signal: AbortSignal.timeout(30000),
          });
          if (!image.ok)
            throw new Error(
              `Cannot snapshot image ${path}: HTTP ${image.status}`,
            );
          return new Uint8Array(await image.arrayBuffer());
        })(),
      );
    }
    return images.get(path);
  };
  // Bound concurrency so the first upgrade does not burst against production.
  for (let start = 0; start < urls.length; start += 4) {
    await Promise.all(
      urls.slice(start, start + 4).map(async (url) => {
        const page = await request(url, {
          ...options,
          signal: AbortSignal.timeout(30000),
        });
        if (!page.ok)
          throw new Error(`Cannot snapshot ${url}: HTTP ${page.status}`);
        const html = await page.text();
        const bytes = [];
        for (const path of referencedImages(html))
          bytes.push(await imageBytes(path));
        const fingerprints = pageFingerprints(url, html, bytes);
        if (pages[url] && pages[url].hash !== fingerprints.hash)
          throw new Error(`Live page does not match its manifest: ${url}`);
        pages[url] = { ...pages[url], ...fingerprints };
      }),
    );
  }
  return { schema: 1, pages };
}

export async function submitIndexNow(key, request = fetch, settings = {}) {
  if (
    !settings.previous ||
    !settings.current ||
    !Object.keys(settings.current.pages ?? {}).length
  ) {
    throw new Error(
      'Provide the pre-deployment snapshot and nonempty current build manifest.',
    );
  }
  validateManifest(settings.previous);
  validateManifest(settings.current);
  const options = { signal: AbortSignal.timeout(30000), redirect: 'error' };
  const keyResponse = await request(`${siteOrigin}/indexnow.txt`, options);
  if (!keyResponse.ok || (await keyResponse.text()).trim() !== key) {
    throw new Error(
      'The public IndexNow key does not match this checkout. Deploy first.',
    );
  }
  const live = await request(`${siteOrigin}/seo-manifest.json`, options);
  if (!live.ok) throw new Error('Deploy the SEO manifest before submitting.');
  const actual = validateManifest(await live.json());
  const expected = Object.entries(settings.current.pages);
  if (
    Object.keys(actual.pages).length !== expected.length ||
    expected.some(([url, page]) => {
      const deployed = actual.pages[url];
      return (
        deployed?.hash !== page.hash ||
        deployed?.contentHash !== page.contentHash ||
        deployed?.lastmod !== page.lastmod
      );
    })
  )
    throw new Error('Live content does not match this build. Deploy first.');
  const urls = changedUrls(settings.previous, settings.current);
  if (!urls.length)
    return { status: null, submitted: 0, attempts: 0, urls: [] };
  for (const url of urls.filter((value) => !settings.current.pages[value])) {
    const removed = await request(url, {
      ...options,
      method: 'HEAD',
      redirect: 'manual',
    });
    if (![301, 308, 404, 410].includes(removed.status))
      throw new Error(`Removed URL still serves content: ${url}`);
  }
  const payload = urlPayload(urls, key);
  const attempts = settings.maxAttempts ?? 3;
  const sleep =
    settings.sleep ?? ((ms) => new Promise((done) => setTimeout(done, ms)));
  for (let attempt = 1; attempt <= attempts; attempt++) {
    let response;
    try {
      response = await request('https://api.indexnow.org/indexnow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(30000),
        redirect: 'error',
      });
    } catch (error) {
      if (attempt === attempts) throw error;
      await sleep(1000 * 2 ** (attempt - 1));
      continue;
    }
    if (response.status === 200 || response.status === 202) {
      return {
        status: response.status,
        submitted: payload.urlList.length,
        attempts: attempt,
        urls: payload.urlList,
      };
    }
    const retry = response.headers.get('retry-after');
    const delay = retry
      ? /^\d+$/.test(retry)
        ? Number(retry) * 1000
        : Date.parse(retry) - Date.now()
      : 1000 * 2 ** (attempt - 1);
    if (
      attempt === attempts ||
      ![429, 500, 502, 503, 504].includes(response.status) ||
      !Number.isFinite(delay) ||
      delay > 30000
    ) {
      throw new Error(
        `IndexNow returned HTTP ${response.status}; retry later using the saved snapshot.`,
      );
    }
    await sleep(Math.max(1000, delay));
  }
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  const args = process.argv.slice(2);
  const option = (name) => args[args.indexOf(name) + 1];
  const save = (path, value) => {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
  };
  if (args[0] === 'snapshot' && args.includes('--output')) {
    save(option('--output'), await snapshotWebsite());
  } else if (
    args[0] === 'submit' &&
    args.includes('--previous') &&
    args.includes('--current') &&
    args.includes('--receipt')
  ) {
    const receipt = option('--receipt');
    try {
      const key = readFileSync(
        new URL('../docs/public/indexnow.txt', import.meta.url),
        'utf8',
      ).trim();
      const result = await submitIndexNow(key, fetch, {
        previous: JSON.parse(readFileSync(option('--previous'), 'utf8')),
        current: JSON.parse(readFileSync(option('--current'), 'utf8')),
      });
      save(receipt, { time: new Date().toISOString(), ...result });
      console.log(
        `IndexNow received ${result.submitted} changed URLs (HTTP ${result.status ?? 'not needed'}). Receipt does not guarantee indexing or ranking.`,
      );
    } catch (error) {
      save(receipt, { time: new Date().toISOString(), error: String(error) });
      throw error;
    }
  } else {
    throw new Error(
      'Usage: bun run indexnow snapshot --output previous.json; bun run indexnow submit --previous previous.json --current doc_build/seo-manifest.json --receipt receipt.json',
    );
  }
}
