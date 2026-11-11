import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { canonicalUrl } from '../theme/seo.ts';

export type SeoManifest = {
  schema: 1;
  pages: Record<string, { hash: string; lastmod?: string }>;
};

/** Ignore executable asset hashes: a new shared bundle is not a content edit. */
export function pageFingerprint(html: string) {
  const content = html
    .replace(
      /<script\b(?![^>]*type="application\/ld\+json")[^>]*>[\s\S]*?<\/script>/gi,
      '',
    )
    .replace(
      /<link\b[^>]*rel="(?:stylesheet|preload|modulepreload|prefetch)"[^>]*>/gi,
      '',
    );
  return createHash('sha256').update(content).digest('hex');
}

export function referencedImages(html: string) {
  return [
    ...new Set(
      [...html.matchAll(/<img\b[^>]*src="(\/images\/[^"?#]+)"/g)].map(
        (match) => match[1],
      ),
    ),
  ].sort();
}

export function contentFingerprint(html: string, images: Uint8Array[]) {
  const hash = createHash('sha256').update(pageFingerprint(html));
  for (const image of images) hash.update(image);
  return hash.digest('hex');
}

export function buildManifest(
  output: string,
  pages: { path: string; lastmod?: string }[],
): SeoManifest {
  return {
    schema: 1,
    pages: Object.fromEntries(
      pages.map(({ path, lastmod }) => {
        const url = canonicalUrl(path);
        const html = readFileSync(
          resolve(output, new URL(url).pathname.slice(1)),
          'utf8',
        );
        // Replacing an illustration at a stable URL is also a content change.
        const images = referencedImages(html).map((image) =>
          readFileSync(resolve(output, image.slice(1))),
        );
        return [
          url,
          {
            hash: contentFingerprint(html, images),
            ...(lastmod ? { lastmod } : {}),
          },
        ];
      }),
    ),
  };
}
