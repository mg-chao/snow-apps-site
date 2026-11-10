import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import type { RouteMeta, RspressPlugin } from '@rspress/core';
import { canonicalUrl } from '../theme/seo.ts';

export function sitemapXml(paths: string[]) {
  const urls = [
    ...new Set(
      paths
        .filter((path) => !/^\/(?:zh\/)?404(?:\.html)?$/.test(path))
        .map(canonicalUrl),
    ),
  ].sort();
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((url) => `  <url><loc>${url.replaceAll('&', '&amp;')}</loc></url>`).join('\n')}\n</urlset>\n`;
}

export function seoBuildPlugin(): RspressPlugin {
  let routes: RouteMeta[] = [];
  const originalSearchRoutes = new WeakMap<object, string>();
  return {
    name: 'snow-shot-sitemap',
    routeGenerated(generated) {
      routes = generated;
    },
    modifySearchIndexData(pages) {
      for (const page of pages) {
        // Initial index loading can return results before client search hooks.
        // Store directly addressable URLs so that path is canonical too.
        if (/^\/(?:zh\/)?(?:guides|blog)(?:\/|$)/.test(page.routePath)) {
          originalSearchRoutes.set(page, page.routePath);
          page.routePath = new URL(canonicalUrl(page.routePath)).pathname;
        }
        if (!/^\/(?:zh\/)?guides(?:\/|$)/.test(page.routePath)) continue;
        // JSX demonstrations belong in the page, not in search-result excerpts.
        const removed: { start: number; length: number }[] = [];
        page.content = page.content.replace(
          /^import .+ from .+;?\s*$|<GuideSteps\b[\s\S]*?\/>|<(?:ArrowDemo|GuideRecordingDemo)\b[^>]*\/>/gm,
          (match, offset: number) => {
            removed.push({ start: offset, length: match.length });
            return '';
          },
        );
        for (const heading of page.toc) {
          const before = removed.filter(
            (part) => part.start < heading.charIndex,
          );
          heading.charIndex -= before.reduce(
            (sum, part) => sum + part.length,
            0,
          );
        }
      }
    },
    extendPageData(page) {
      // Rspress serializes the search index before this hook, then reuses the
      // records for runtime page lookup. Rendering needs the original routes.
      const route = originalSearchRoutes.get(page);
      if (route) {
        page.routePath = route;
        originalSearchRoutes.delete(page);
      }
    },
    afterBuild(config, isProd) {
      if (!isProd) return;
      const output = resolve(config.outDir ?? 'doc_build');
      mkdirSync(output, { recursive: true });
      writeFileSync(
        resolve(output, 'sitemap.xml'),
        sitemapXml(routes.map((route) => route.routePath)),
      );
    },
  };
}
