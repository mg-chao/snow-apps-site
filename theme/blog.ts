import { canonicalUrl } from './seo.ts';

export type BlogCategory = 'releases' | 'answers';
export type BlogPost = {
  title: string;
  description: string;
  routePath: string;
  lang: string;
  date: string;
  category: BlogCategory;
  productVersion: string;
  platforms: string;
  related: string[];
  releaseDate?: string;
};

type Page = {
  title: string;
  description?: string;
  routePath: string;
  lang: string;
  frontmatter: Record<string, unknown>;
};

/** Rspress's page index is the only source of article metadata. */
export function blogPosts(pages: Page[], lang: string): BlogPost[] {
  return pages
    .filter((page) => page.lang === lang && page.frontmatter.blog === true)
    .map((page) => ({
      title: page.title,
      description: page.description ?? '',
      routePath: new URL(canonicalUrl(page.routePath)).pathname,
      lang: page.lang,
      date: String(page.frontmatter.date),
      category: page.frontmatter.category as BlogCategory,
      productVersion: String(page.frontmatter.productVersion),
      platforms: String(page.frontmatter.platforms),
      related: (page.frontmatter.related as string[]) ?? [],
      releaseDate: page.frontmatter.releaseDate as string | undefined,
    }))
    .sort(
      (a, b) =>
        b.date.localeCompare(a.date) || a.routePath.localeCompare(b.routePath),
    );
}

export function relatedPosts(post: BlogPost, posts: BlogPost[]) {
  return post.related.flatMap((slug) =>
    posts.filter(
      (item) =>
        item.routePath.endsWith(`/${slug}.html`) &&
        item.routePath !== post.routePath,
    ),
  );
}

/** Release times remain UTC in metadata; display the reader's stated calendar. */
export function releaseCalendarDate(value: string, lang: string) {
  const parts = new Intl.DateTimeFormat('en', {
    timeZone: lang === 'zh' ? 'Asia/Shanghai' : 'UTC',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(new Date(value));
  const part = (type: string) =>
    parts.find((entry) => entry.type === type)?.value;
  return `${part('year')}-${part('month')}-${part('day')}`;
}
