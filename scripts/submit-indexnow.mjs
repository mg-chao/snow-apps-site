import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { siteOrigin } from '../theme/seo.ts';

export function indexNowPayload(sitemap, key) {
  if (!/^[a-zA-Z0-9-]{8,128}$/.test(key)) {
    throw new Error('Invalid IndexNow verification key.');
  }
  const urls = [
    ...new Set(
      [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]),
    ),
  ];
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
      url.hash
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

export async function submitIndexNow(key, request = fetch) {
  const options = { signal: AbortSignal.timeout(30000), redirect: 'error' };
  const keyResponse = await request(`${siteOrigin}/indexnow.txt`, options);
  if (!keyResponse.ok || (await keyResponse.text()).trim() !== key) {
    throw new Error(
      'The public IndexNow key does not match this checkout. Deploy first.',
    );
  }
  const sitemapResponse = await request(`${siteOrigin}/sitemap.xml`, options);
  if (!sitemapResponse.ok)
    throw new Error('The public sitemap is unavailable.');
  const payload = indexNowPayload(await sitemapResponse.text(), key);
  const response = await request('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(30000),
    redirect: 'error',
  });
  if (response.status !== 200 && response.status !== 202) {
    throw new Error(
      `IndexNow returned HTTP ${response.status}; do not retry in a tight loop.`,
    );
  }
  return { status: response.status, submitted: payload.urlList.length };
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  const key = readFileSync(
    new URL('../docs/public/indexnow.txt', import.meta.url),
    'utf8',
  ).trim();
  const result = await submitIndexNow(key);
  console.log(
    `IndexNow received ${result.submitted} URLs (HTTP ${result.status}).${result.status === 202 ? ' Key validation is pending.' : ''} Receipt does not guarantee indexing or ranking.`,
  );
}
