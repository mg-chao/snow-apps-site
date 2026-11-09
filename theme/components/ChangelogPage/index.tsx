import './style.css';
import { useHead } from '@rspress/core/runtime';
import { useCallback, useEffect, useRef, useState } from 'react';
import Markdown, { defaultUrlTransform } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  type Channel,
  type Locale,
  type Release,
  filterReleases,
  formatReleaseDate,
  latestRelease,
  releaseId,
  releases,
} from './model';

const batchSize = 8;
const sourceUrl = 'https://github.com/mg-chao/snow-shot/releases';

const copy = {
  zh: {
    eyebrow: 'SNOW SHOT / CHANGELOG',
    title: '每一次更新，',
    accent: '都更顺手。',
    intro:
      '新功能、小改进，还有那些不易察觉的修复。这里记录 Snow Shot 一步步变好的过程。',
    latest: '最新正式版',
    download: '下载最新版',
    downloadShort: '下载最新版',
    jump: '阅读本次更新',
    jumpShort: '本次更新',
    history: '版本记录',
    historyNote: '新的变化，从这里开始。',
    source: 'GitHub Releases',
    stable: '正式版',
    preview: '预览版',
    all: '全部',
    channelLabel: '版本类型',
    search: '搜索版本或更新内容',
    placeholder: '搜索版本、功能或修复…',
    clear: '清除搜索',
    results: (count: number) => `${count} 个版本`,
    shown: (count: number, total: number) =>
      `已显示 ${count} / ${total} 个版本`,
    more: '加载更多版本',
    end: '你已读完这些版本的更新。',
    empty: '没有找到匹配的更新',
    emptyNote: '试试其他关键词，或切换版本类型继续查找。',
    reset: '重置筛选',
    original: '在 GitHub 查看原文',
    permalink: (version: string) => `前往 ${version} 的固定链接`,
    noNotes: '此版本未附更新说明，可前往 GitHub 查看详情。',
    previewNote: '预览版本用于体验开发中的变化，日常使用建议选择正式版。',
    closing: '下一个好用的细节，也许来自你的建议。',
    feedback: '反馈问题与想法',
    allHistory: '完整发布记录',
  },
  en: {
    eyebrow: 'SNOW SHOT / CHANGELOG',
    title: 'A little better.',
    accent: 'Every release.',
    intro:
      'New features, thoughtful improvements, and the fixes you might never notice. Follow the progress of Snow Shot, one release at a time.',
    latest: 'Latest stable release',
    download: 'Get the latest version',
    downloadShort: 'Download',
    jump: 'Read the release notes',
    jumpShort: 'Release notes',
    history: 'Release history',
    historyNote: 'Small changes. Steady progress.',
    source: 'GitHub Releases',
    stable: 'Stable',
    preview: 'Preview',
    all: 'All',
    channelLabel: 'Release channel',
    search: 'Search versions or release notes',
    placeholder: 'Search versions, features, or fixes…',
    clear: 'Clear search',
    results: (count: number) =>
      `${count} ${count === 1 ? 'release' : 'releases'}`,
    shown: (count: number, total: number) =>
      `Showing ${count} of ${total} releases`,
    more: 'Load more releases',
    end: 'You’re all caught up with these releases.',
    empty: 'No matching releases',
    emptyNote: 'Try another keyword or switch the release channel.',
    reset: 'Reset filters',
    original: 'View original on GitHub',
    permalink: (version: string) => `Permalink to ${version}`,
    noNotes: 'No release notes were provided. Visit GitHub for more details.',
    previewNote:
      'Preview releases offer a look at work in progress. Choose a stable release for everyday use.',
    closing: 'The next thoughtful detail could start with your idea.',
    feedback: 'Share feedback & ideas',
    allHistory: 'Full release archive',
  },
};

function Arrow({ diagonal = false }: { diagonal?: boolean }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none">
      <path d={diagonal ? 'M6 18 18 6M6 6h12v12' : 'M4 12h16m-6-6 6 6-6 6'} />
    </svg>
  );
}

function ReleaseNotes({
  release,
  locale,
}: {
  release: Release;
  locale: Locale;
}) {
  const language = release.notesLanguage[locale];
  return (
    <div
      className="snow-release__notes"
      lang={language === 'mixed' ? undefined : language}
    >
      <Markdown
        skipHtml
        remarkPlugins={[remarkGfm]}
        urlTransform={(url) => {
          const safe = defaultUrlTransform(url);
          try {
            return safe ? new URL(safe, release.url).href : '';
          } catch {
            return '';
          }
        }}
        components={{
          h1: ({ children }) => <h3>{children}</h3>,
          h2: ({ children }) => <h3>{children}</h3>,
          h3: ({ children }) => <h3>{children}</h3>,
          h4: ({ children }) => <h4>{children}</h4>,
          table: ({ children }) => (
            <div className="snow-release__table">
              <table>{children}</table>
            </div>
          ),
          img: ({ node: _node, ...props }) => (
            <img {...props} loading="lazy" alt={props.alt ?? ''} />
          ),
        }}
      >
        {release.notes[locale] || copy[locale].noNotes}
      </Markdown>
    </div>
  );
}

export function ChangelogPage({ locale }: { locale: Locale }) {
  const title =
    locale === 'zh' ? '更新日志 · Snow Shot' : 'Changelog · Snow Shot';
  useHead({ title, meta: [{ property: 'og:title', content: title }] });
  const t = copy[locale];
  const [channel, setChannel] = useState<Channel>('stable');
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(batchSize);
  const [pendingAnchor, setPendingAnchor] = useState<string | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const nextReleaseRef = useRef<HTMLElement>(null);
  const focusNext = useRef(false);
  const filtered = filterReleases(channel, query);
  const visible = filtered.slice(0, limit);

  const revealRelease = useCallback((release: Release) => {
    const nextChannel = release.prerelease ? 'preview' : 'stable';
    const index = filterReleases(nextChannel, '').findIndex(
      (item) => item.tag === release.tag,
    );
    setChannel(nextChannel);
    setQuery('');
    setLimit(Math.max(batchSize, index + 1));
    setPendingAnchor(releaseId(release));
  }, []);

  // A shared URL can point to a preview or a release beyond the first batch.
  // Reveal it before scrolling, including when the hash changes on this page.
  useEffect(() => {
    const reveal = () => {
      let id: string;
      try {
        id = decodeURIComponent(window.location.hash.slice(1));
      } catch {
        return;
      }
      const target = releases.find((release) => releaseId(release) === id);
      if (!target) return;
      revealRelease(target);
    };
    reveal();
    window.addEventListener('hashchange', reveal);
    return () => {
      window.removeEventListener('hashchange', reveal);
    };
  }, [revealRelease]);

  useEffect(() => {
    if (!pendingAnchor) return;
    const frame = requestAnimationFrame(() => {
      document
        .getElementById(pendingAnchor)
        ?.scrollIntoView({ block: 'start' });
      setPendingAnchor(null);
    });
    return () => cancelAnimationFrame(frame);
  }, [pendingAnchor]);

  useEffect(() => {
    if (focusNext.current && limit > batchSize) {
      nextReleaseRef.current?.focus({ preventScroll: true });
      focusNext.current = false;
    }
  }, [limit]);

  function reset() {
    setQuery('');
    setChannel('stable');
    setLimit(batchSize);
  }

  return (
    <main className="snow-changelog" lang={locale}>
      <div className="snow-changelog__shell">
        <header className="snow-changelog__hero">
          <div>
            <p className="snow-changelog__eyebrow">{t.eyebrow}</p>
            <h1>
              {t.title}
              <br />
              <span>{t.accent}</span>
            </h1>
            <p className="snow-changelog__intro">{t.intro}</p>
          </div>
          {latestRelease && (
            <aside className="snow-changelog__latest" aria-label={t.latest}>
              <div className="snow-changelog__latest-label">
                <span />
                {t.latest}
              </div>
              <strong>v{latestRelease.version}</strong>
              <time dateTime={latestRelease.publishedAt}>
                {formatReleaseDate(latestRelease.publishedAt, locale)}
              </time>
              <a
                className="snow-button snow-button--primary"
                href={locale === 'zh' ? '/zh/download.html' : '/download.html'}
              >
                <span className="snow-changelog__wide-label">{t.download}</span>
                <span className="snow-changelog__compact-label">
                  {t.downloadShort}
                </span>
                <Arrow />
              </a>
              <a
                className="snow-changelog__latest-jump"
                href={`#${releaseId(latestRelease)}`}
                onClick={() => latestRelease && revealRelease(latestRelease)}
              >
                <span className="snow-changelog__wide-label">{t.jump}</span>
                <span className="snow-changelog__compact-label">
                  {t.jumpShort}
                </span>
                <span aria-hidden="true">↓</span>
              </a>
            </aside>
          )}
        </header>

        <section
          className="snow-changelog__history"
          aria-labelledby="snow-release-history"
        >
          <aside className="snow-changelog__sidebar">
            <h2 id="snow-release-history">{t.history}</h2>
            <p className="snow-changelog__history-note">{t.historyNote}</p>
            <div className="snow-changelog__source">
              <a href={sourceUrl}>
                {t.source}
                <Arrow diagonal />
              </a>
            </div>
          </aside>
          <div className="snow-changelog__feed">
            <div className="snow-changelog__controls">
              <fieldset className="snow-changelog__channels">
                <legend className="snow-changelog__sr-only">
                  {t.channelLabel}
                </legend>
                {(['stable', 'preview', 'all'] as const).map((value) => (
                  <button
                    type="button"
                    key={value}
                    aria-pressed={channel === value}
                    onClick={() => {
                      setChannel(value);
                      setLimit(batchSize);
                    }}
                  >
                    {t[value]}
                  </button>
                ))}
              </fieldset>
              <div className="snow-changelog__search">
                <svg aria-hidden="true" viewBox="0 0 24 24" fill="none">
                  <circle cx="10.5" cy="10.5" r="6.5" />
                  <path d="m16 16 4 4" />
                </svg>
                <label
                  className="snow-changelog__sr-only"
                  htmlFor="snow-release-search"
                >
                  {t.search}
                </label>
                <input
                  ref={searchRef}
                  id="snow-release-search"
                  type="search"
                  value={query}
                  placeholder={t.placeholder}
                  autoComplete="off"
                  onChange={(event) => {
                    setQuery(event.target.value);
                    setLimit(batchSize);
                  }}
                />
                {query && (
                  <button
                    type="button"
                    aria-label={t.clear}
                    onClick={() => {
                      setQuery('');
                      setLimit(batchSize);
                      searchRef.current?.focus();
                    }}
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            <div className="snow-changelog__result-count" role="status">
              {t.results(filtered.length)}
            </div>
            {channel === 'preview' && (
              <p className="snow-changelog__preview-note">{t.previewNote}</p>
            )}
            {visible.length === 0 ? (
              <div className="snow-changelog__empty">
                <span aria-hidden="true">⌕</span>
                <h3>{t.empty}</h3>
                <p>{t.emptyNote}</p>
                <button type="button" onClick={reset}>
                  {t.reset}
                  <Arrow />
                </button>
              </div>
            ) : (
              <div className="snow-changelog__timeline">
                {visible.map((release, index) => (
                  <article
                    key={release.tag}
                    id={releaseId(release)}
                    tabIndex={-1}
                    ref={
                      index === limit - batchSize ? nextReleaseRef : undefined
                    }
                    className={`snow-release${release.tag === latestRelease?.tag ? ' snow-release--latest' : ''}`}
                    aria-labelledby={`${releaseId(release)}-title`}
                  >
                    <div className="snow-release__heading">
                      <h2 id={`${releaseId(release)}-title`}>
                        <a
                          href={`#${releaseId(release)}`}
                          aria-label={t.permalink(release.version)}
                          onClick={() => revealRelease(release)}
                        >
                          v{release.version}
                          <span aria-hidden="true">#</span>
                        </a>
                      </h2>
                      {release.tag === latestRelease?.tag && (
                        <span className="snow-release__badge snow-release__badge--latest">
                          {t.latest}
                        </span>
                      )}
                      {release.prerelease && (
                        <span className="snow-release__badge">{t.preview}</span>
                      )}
                      <time dateTime={release.publishedAt}>
                        {formatReleaseDate(release.publishedAt, locale)}
                      </time>
                    </div>
                    <ReleaseNotes release={release} locale={locale} />
                    <a className="snow-release__original" href={release.url}>
                      {t.original}
                      <Arrow diagonal />
                    </a>
                  </article>
                ))}
              </div>
            )}
            {visible.length > 0 && (
              <div className="snow-changelog__pagination">
                <p>{t.shown(visible.length, filtered.length)}</p>
                {limit < filtered.length ? (
                  <button
                    type="button"
                    onClick={() => {
                      focusNext.current = true;
                      setLimit(limit + batchSize);
                    }}
                  >
                    {t.more}
                    <span aria-hidden="true">↓</span>
                  </button>
                ) : (
                  <span>{t.end}</span>
                )}
              </div>
            )}
          </div>
        </section>
        <footer className="snow-changelog__closing">
          <p>{t.closing}</p>
          <div>
            <a href="https://github.com/mg-chao/snow-shot/issues">
              {t.feedback}
              <Arrow diagonal />
            </a>
            <a href={sourceUrl}>
              {t.allHistory}
              <Arrow diagonal />
            </a>
          </div>
        </footer>
      </div>
    </main>
  );
}
