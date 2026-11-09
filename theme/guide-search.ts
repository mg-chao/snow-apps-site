import { canonicalUrl, siteOrigin } from './seo';

export function guideSearchHref(href: string) {
  const url = new URL(href, siteOrigin);
  if (
    url.origin !== siteOrigin ||
    !/^\/(?:zh\/)?(?:guides|blog)(?:\/|$)/.test(url.pathname)
  ) {
    return href;
  }
  return new URL(canonicalUrl(url.pathname)).pathname + url.search + url.hash;
}

export function afterSearch<T extends { result: { link: string }[] }>(
  _query: string,
  groups: T[],
) {
  // Rspress appends onSearch's return value as custom results. afterSearch
  // receives the final result set, so normalize its links in place.
  for (const group of groups) {
    for (const item of group.result) item.link = guideSearchHref(item.link);
  }
}
