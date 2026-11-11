import { useLang, useLocation, usePage, usePages } from '@rspress/core/runtime';
import { useState } from 'react';
import {
  type BlogCategory,
  type BlogPost,
  blogPosts,
  releaseCalendarDate,
  relatedPosts,
} from '../../blog';
import { articleAuthor, canonicalUrl } from '../../seo';
import './style.css';

function categoryLabel(category: BlogCategory, zh: boolean) {
  return category === 'releases'
    ? zh
      ? '版本解读'
      : 'Release insights'
    : zh
      ? '问题答疑'
      : 'Questions & tutorials';
}

function PostMeta({ post }: { post: BlogPost }) {
  const zh = post.lang === 'zh';
  const author = articleAuthor(zh ? 'zh' : 'en');
  const modified = post.modified
    ? releaseCalendarDate(post.modified, post.lang)
    : undefined;
  return (
    <div className="snow-blog-meta">
      <span className="snow-blog-tag">{categoryLabel(post.category, zh)}</span>
      <a href={author.url}>{author.name}</a>
      <span>
        {zh ? '撰写于 ' : 'Written '}
        <time dateTime={post.date}>{post.date}</time>
      </span>
      {modified && modified > post.date && (
        <span>
          {zh ? '更新于 ' : 'Updated '}
          <time dateTime={post.modified}>{modified}</time>
        </span>
      )}
      {post.releaseDate && (
        <span>
          {zh ? '产品发布：' : 'Released: '}
          <time dateTime={post.releaseDate}>
            {releaseCalendarDate(post.releaseDate, post.lang)}
          </time>
        </span>
      )}
    </div>
  );
}

export function BlogIndex() {
  const lang = useLang();
  const zh = lang === 'zh';
  const { pages } = usePages();
  const posts = blogPosts(pages, lang);
  const [category, setCategory] = useState<BlogCategory | 'all'>('all');
  const visible = posts.filter(
    (post) => category === 'all' || post.category === category,
  );
  return (
    <section
      className="snow-blog-index"
      aria-label={zh ? '博客文章' : 'Blog articles'}
    >
      <section
        className="snow-blog-filters"
        aria-label={zh ? '文章分类' : 'Article categories'}
      >
        {(['all', 'releases', 'answers'] as const).map((value) => (
          <button
            type="button"
            key={value}
            aria-pressed={value === category}
            onClick={() => setCategory(value)}
          >
            {value === 'all'
              ? zh
                ? '全部文章'
                : 'All articles'
              : categoryLabel(value, zh)}
            <span>
              {value === 'all'
                ? posts.length
                : posts.filter((post) => post.category === value).length}
            </span>
          </button>
        ))}
      </section>
      <p aria-live="polite" className="snow-blog-count">
        {zh ? `${visible.length} 篇文章` : `${visible.length} articles`}
      </p>
      <div className="snow-blog-grid">
        {visible.map((post) => (
          <article className="snow-blog-card" key={post.routePath}>
            <PostMeta post={post} />
            <h2>
              <a href={post.routePath}>{post.title}</a>
            </h2>
            <p>{post.description}</p>
            <a className="snow-blog-read" href={post.routePath}>
              {zh ? '阅读全文 →' : 'Read article →'}
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}

export function BlogArticleMeta() {
  const { page } = usePage();
  const { pages } = usePages();
  const { pathname } = useLocation();
  const lang = useLang();
  if (page.frontmatter.blog !== true) return null;
  const post = blogPosts(pages, lang).find(
    (item) => item.routePath === new URL(canonicalUrl(pathname)).pathname,
  );
  return post ? <PostMeta post={post} /> : null;
}

export function BlogRelated() {
  const { page } = usePage();
  const { pages } = usePages();
  const { pathname } = useLocation();
  const lang = useLang();
  if (page.frontmatter.blog !== true) return null;
  const posts = blogPosts(pages, lang);
  const post = posts.find(
    (item) => item.routePath === new URL(canonicalUrl(pathname)).pathname,
  );
  if (!post) return null;
  return (
    <aside
      className="snow-blog-related"
      aria-label={lang === 'zh' ? '相关文章' : 'Related articles'}
    >
      <h2>{lang === 'zh' ? '接着阅读' : 'Keep reading'}</h2>
      <ul>
        {relatedPosts(post, posts).map((item) => (
          <li key={item.routePath}>
            <a href={item.routePath}>{item.title}</a>
          </li>
        ))}
      </ul>
      <a href={lang === 'zh' ? '/zh/blog/index.html' : '/blog/index.html'}>
        {lang === 'zh' ? '查看全部博客文章 →' : 'Browse all articles →'}
      </a>
    </aside>
  );
}
