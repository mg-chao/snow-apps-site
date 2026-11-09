import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { describe, it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import Markdown, { defaultUrlTransform } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';

const require = createRequire(import.meta.url);
const snapshot = JSON.parse(
  readFileSync(
    new URL('../theme/components/ChangelogPage/releases.json', import.meta.url),
    'utf8',
  ),
);

function loadModule(filename, modules) {
  const source = readFileSync(
    new URL(`../theme/components/ChangelogPage/${filename}`, import.meta.url),
    'utf8',
  );
  const compiled = transpileModule(source, {
    compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
  }).outputText;
  const exports = {};
  runInNewContext(compiled, {
    exports,
    URL,
    require(name) {
      return modules[name] ?? require(name);
    },
  });
  return exports;
}

function loadModel(releases) {
  return loadModule('model.ts', {
    './releases.json': { __esModule: true, default: { ...snapshot, releases } },
  });
}

function render(locale, releases = snapshot.releases) {
  const { ChangelogPage } = loadModule('index.tsx', {
    './style.css': {},
    './model': loadModel(releases),
    'react-markdown': {
      __esModule: true,
      default: Markdown,
      defaultUrlTransform,
    },
    'remark-gfm': { __esModule: true, default: remarkGfm },
    '@rspress/core/runtime': { useHead: () => {} },
  });
  return renderToStaticMarkup(createElement(ChangelogPage, { locale }));
}

function release(overrides = {}) {
  return {
    tag: 'v2.0.0_snow-shot',
    version: '2.0.0',
    name: 'Snow Shot 2.0.0',
    publishedAt: '2026-11-08T16:14:35Z',
    url: 'https://github.com/mg-chao/snow-shot/releases/tag/v2.0.0_snow-shot',
    prerelease: false,
    notes: {
      zh: '- 截图支持滚动长图与 PDF 导出。',
      en: '- Capture scrolling screenshots and export PDFs.',
    },
    notesLanguage: { zh: 'zh', en: 'en' },
    ...overrides,
  };
}

describe('release discovery', () => {
  const stable = release();
  const preview = release({
    tag: 'v2.1.0-beta_snow-shot',
    version: '2.1.0-beta',
    name: 'Snow Shot 2.1.0 beta',
    prerelease: true,
    notes: { zh: '- 修复 OCR 识别。', en: '- Improve OCR recognition.' },
  });
  const older = release({
    tag: 'v1.9.0_snow-shot',
    version: '1.9.0',
    name: 'Snow Shot 1.9.0',
    notes: { zh: '- 录屏性能改进。', en: '- Improve recording performance.' },
  });
  const model = loadModel([preview, stable, older]);
  const tags = (releases) => Array.from(releases, (item) => item.tag);

  it('separates stable and preview channels without changing source order', () => {
    assert.deepEqual(tags(model.filterReleases('stable', '')), [
      stable.tag,
      older.tag,
    ]);
    assert.deepEqual(tags(model.filterReleases('preview', '')), [preview.tag]);
    assert.deepEqual(tags(model.filterReleases('all', '')), [
      preview.tag,
      stable.tag,
      older.tag,
    ]);
    assert.equal(model.latestRelease.tag, stable.tag);
  });

  it('matches version tags and both languages independently of the displayed locale', () => {
    assert.deepEqual(tags(model.filterReleases('all', '2.0.0')), [stable.tag]);
    assert.deepEqual(tags(model.filterReleases('all', '滚动长图')), [
      stable.tag,
    ]);
    assert.deepEqual(tags(model.filterReleases('all', 'SCROLLING')), [
      stable.tag,
    ]);
    assert.deepEqual(tags(model.filterReleases('stable', 'OCR')), []);
    assert.deepEqual(tags(model.filterReleases('preview', 'ocr')), [
      preview.tag,
    ]);
  });

  it('requires every whitespace-separated search word and handles an empty query', () => {
    assert.deepEqual(tags(model.filterReleases('all', '  截图\tPDF\n  ')), [
      stable.tag,
    ]);
    assert.deepEqual(
      tags(model.filterReleases('all', 'scrolling recognition')),
      [],
    );
    assert.deepEqual(tags(model.filterReleases('all', ' \t\n ')), [
      preview.tag,
      stable.tag,
      older.tag,
    ]);
    assert.deepEqual(
      tags(model.filterReleases('all', 'unreleased-feature')),
      [],
    );
  });

  it('uses the tag for a unique, stable permalink rather than the display version', () => {
    assert.equal(model.releaseId(stable), 'release-v2.0.0_snow-shot');
    assert.notEqual(
      model.releaseId({ tag: 'v0.1.3-beta-20250527-01' }),
      model.releaseId({ tag: 'v0.1.3-beta-20250527-02' }),
    );
  });

  it('formats publication dates in Beijing time even when UTC is still the previous day', () => {
    assert.equal(
      model.formatReleaseDate('2026-11-08T15:59:59Z', 'en'),
      'Nov 8, 2026',
    );
    assert.equal(
      model.formatReleaseDate('2026-11-08T16:00:00Z', 'en'),
      'Nov 9, 2026',
    );
    assert.equal(
      model.formatReleaseDate('2026-11-08T16:00:00Z', 'zh'),
      '2026年11月9日',
    );
    assert.equal(
      model.formatReleaseDate('2026-12-31T20:00:00Z', 'zh'),
      '2027年1月1日',
    );
  });
});

describe('release note rendering', () => {
  for (const locale of ['en', 'zh']) {
    it(`server-renders the latest published notes and history links in ${locale}`, () => {
      const html = render(locale);
      const latest = snapshot.releases.find((item) => !item.prerelease);
      const articles = [
        ...html.matchAll(/<article\b[^>]*>[\s\S]*?<\/article>/g),
      ].map((match) => match[0]);
      assert.equal(articles.length, 8);
      assert.match(articles[0], new RegExp(`id="release-${latest.tag}"`));
      assert.ok(articles[0].includes(`href="${latest.url}"`));
      assert.ok(
        articles[0].includes(`<time dateTime="${latest.publishedAt}">`),
      );
      assert.equal((html.match(/<h1\b/g) ?? []).length, 1);
      assert.ok(
        articles[0].includes(
          locale === 'zh'
            ? '可将系统中选中的图片直接导入编辑器'
            : 'Open selected images directly in the editor',
        ),
      );
      assert.ok(
        !articles[0].includes(
          locale === 'zh'
            ? 'Open selected images directly in the editor'
            : '可将系统中选中的图片直接导入编辑器',
        ),
      );
      assert.match(articles[0], /<ul>[\s\S]*<li>/);
      assert.ok(!html.includes('macOS 快速安装'));
      assert.ok(!html.includes('Download guide'));
      assert.ok(!html.includes('install-snow-shot-macos.sh'));
      assert.ok(
        html.includes(`href="${locale === 'zh' ? '/zh' : ''}/download.html"`),
      );
    });
  }

  it('keeps original-language fallbacks readable with the correct language metadata', () => {
    const english = release({
      notes: { zh: '- Original English note.', en: '- Original English note.' },
      notesLanguage: { zh: 'en', en: 'en' },
    });
    const chinese = release({
      notes: { zh: '- 原始中文说明。', en: '- 原始中文说明。' },
      notesLanguage: { zh: 'zh', en: 'zh' },
    });
    const zh = render('zh', [english]);
    assert.match(zh, /class="snow-release__notes" lang="en"/);
    assert.match(zh, /<li>Original English note\.<\/li>/);
    const en = render('en', [chinese]);
    assert.match(en, /class="snow-release__notes" lang="zh"/);
    assert.match(en, /<li>原始中文说明。<\/li>/);
  });

  it('keeps Markdown readable while preventing extra page titles and executable HTML', () => {
    const markdown =
      '# Historical title\n\n## Improvements\n\n- **Sharper** previews\n\n[Commit](/mg-chao/snow-shot/commit/abc123)\n\n[Unsafe](javascript:alert%281%29)\n\n<script>alert(1)</script>\n\n![Preview](https://example.com/preview.png)';
    const html = render('en', [
      release({ notes: { en: markdown, zh: markdown } }),
    ]);
    assert.equal((html.match(/<h1\b/g) ?? []).length, 1);
    assert.match(html, /<h3>Historical title<\/h3>/);
    assert.match(html, /<h3>Improvements<\/h3>/);
    assert.match(html, /<strong>Sharper<\/strong>/);
    assert.match(
      html,
      /href="https:\/\/github.com\/mg-chao\/snow-shot\/commit\/abc123"/,
    );
    assert.ok(!html.includes('javascript:'));
    assert.ok(!html.includes('<script>'));
    assert.match(html, /<img[^>]+loading="lazy"/);
  });

  it('provides a useful fallback when a release has no notes', () => {
    const empty = release({ notes: { en: '', zh: '' } });
    assert.match(render('en', [empty]), /No release notes were provided/);
    assert.match(render('zh', [empty]), /此版本未附更新说明/);
  });

  it('renders historical GitHub tables and automatic links without losing their structure', () => {
    const markdown =
      '| Feature | Status |\n| --- | --- |\n| OCR | Improved |\n\nhttps://github.com/mg-chao/snow-shot/issues/123';
    const html = render('en', [
      release({ notes: { en: markdown, zh: markdown } }),
    ]);
    assert.match(html, /class="snow-release__table"><table>/);
    assert.match(html, /<th>Feature<\/th>/);
    assert.match(html, /<td>OCR<\/td>/);
    assert.match(
      html,
      /href="https:\/\/github.com\/mg-chao\/snow-shot\/issues\/123"/,
    );
  });
});
