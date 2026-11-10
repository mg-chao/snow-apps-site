import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { it } from 'node:test';
import { loadFrontMatter } from '@rspress/shared/node-utils';
import { seoBuildPlugin } from '../scripts/seo-build.ts';
import { blogPosts, relatedPosts, releaseCalendarDate } from '../theme/blog.ts';
import { guideSearchHref } from '../theme/guide-search.ts';
import { canonicalUrl, pageBreadcrumbs } from '../theme/seo.ts';

const root = path.resolve('docs');
const pages = ['en', 'zh'].flatMap((lang) =>
  readdirSync(path.join(root, lang, 'blog')).map((file) => {
    const filepath = path.join(root, lang, 'blog', file);
    const { frontmatter } = loadFrontMatter(
      readFileSync(filepath, 'utf8'),
      filepath,
      root,
    );
    return {
      title: frontmatter.title,
      description: frontmatter.description,
      lang,
      routePath: `${lang === 'zh' ? '/zh' : ''}/blog/${file.replace(/\.mdx?$/, '')}`,
      frontmatter,
    };
  }),
);

it('discovers bilingual article metadata, excluding the landing page', () => {
  const en = blogPosts(pages, 'en');
  const zh = blogPosts(pages, 'zh');
  assert.ok(en.length >= 10);
  assert.deepEqual(
    zh.map((post) => post.routePath.replace('/zh', '')),
    en.map((post) => post.routePath),
  );
  for (const lang of ['en', 'zh']) {
    const posts = blogPosts(pages, lang);
    assert.ok(posts.filter((post) => post.category === 'releases').length >= 3);
    assert.ok(posts.filter((post) => post.category === 'answers').length >= 7);
    for (const post of posts) {
      assert.match(post.date, /^\d{4}-\d{2}-\d{2}$/);
      assert.ok(post.description && post.platforms && post.productVersion);
      assert.equal(
        relatedPosts(post, posts).length,
        post.related.length,
        post.routePath,
      );
    }
  }
});

it('automatically includes a new article from page metadata and orders dates', () => {
  const extra = {
    title: 'A future article',
    description: 'A new task',
    lang: 'en',
    routePath: '/blog/new-task',
    frontmatter: {
      blog: true,
      category: 'answers',
      date: '2027-01-02',
      productVersion: '2.0',
      platforms: 'Windows',
      related: [],
    },
  };
  assert.equal(
    blogPosts([...pages, extra], 'en')[0].routePath,
    '/blog/new-task.html',
  );
  assert.equal(
    blogPosts([...pages, extra], 'zh').length,
    blogPosts(pages, 'zh').length,
  );
  assert.equal(
    blogPosts([...pages, extra], 'en').length,
    blogPosts(pages, 'en').length + 1,
  );
});

it('uses direct bilingual .html routes in search and three-level article breadcrumbs', () => {
  for (const prefix of ['', '/zh']) {
    assert.equal(
      canonicalUrl(`${prefix}/blog`),
      `https://snowshot.top${prefix}/blog/index.html`,
    );
    assert.equal(
      guideSearchHref(`${prefix}/blog/new-task#steps`),
      `${prefix}/blog/new-task.html#steps`,
    );
    const crumbs = pageBreadcrumbs(
      `${prefix}/blog/new-task`,
      prefix ? 'zh' : 'en',
      'Task',
    );
    assert.equal(crumbs.length, 3);
    assert.equal(crumbs[1].href, `${prefix}/blog/index.html`);
  }
});

it('keeps release calendar dates consistent across server and client timezones', () => {
  assert.equal(releaseCalendarDate('2026-11-08T16:14:35Z', 'zh'), '2026-11-09');
  assert.equal(releaseCalendarDate('2026-11-08T16:14:35Z', 'en'), '2026-11-08');
});

it('stores canonical search-index routes before the first search can bypass client hooks', () => {
  const pages = [
    '/blog/new-task',
    '/zh/blog/new-task',
    '/guides/',
    '/zh/guides/task',
  ].map((routePath) => ({
    routePath,
    content: 'A useful task description',
    toc: [],
  }));
  const plugin = seoBuildPlugin();
  const originalRoutes = pages.map((page) => page.routePath);
  plugin.modifySearchIndexData(pages);
  assert.deepEqual(
    pages.map((page) => page.routePath),
    [
      '/blog/new-task.html',
      '/zh/blog/new-task.html',
      '/guides/index.html',
      '/zh/guides/task.html',
    ],
  );
  assert.ok(
    pages.every((page) => page.content === 'A useful task description'),
  );
  const serializedIndex = JSON.stringify(pages);
  for (const page of pages) plugin.extendPageData(page);
  assert.deepEqual(
    pages.map((page) => page.routePath),
    originalRoutes,
  );
  assert.ok(
    JSON.parse(serializedIndex).every((page) =>
      page.routePath.endsWith('.html'),
    ),
  );
});
