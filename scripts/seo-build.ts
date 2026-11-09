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
  return {
    name: 'snow-shot-sitemap',
    routeGenerated(generated) {
      routes = generated;
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
