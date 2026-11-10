import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';
import { languageHref } from '../theme/locale.ts';
import { siteLinks } from '../theme/site-structure.ts';

const require = createRequire(import.meta.url);
let locale = 'en';
let location = { pathname: '/', search: '', hash: '' };
const currentWindow = { location: { href: 'http://localhost/' } };

function loadComponent(file, mocks = {}) {
  const source = readFileSync(new URL(file, import.meta.url), 'utf8');
  const compiled = transpileModule(source, {
    compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
  }).outputText;
  const exports = {};
  runInNewContext(compiled, {
    exports,
    window: currentWindow,
    require(name) {
      if (name.endsWith('.css')) return {};
      if (name === '@rspress/core/runtime') {
        return {
          useLang: () => locale,
          useLocation: () => location,
          useNav: () => {
            const links = siteLinks(locale);
            return ['guides', 'download', 'blog', 'changelog', 'about'].map(
              (key) => ({ text: links[key].label, link: links[key].href }),
            );
          },
          NoSSR: ({ children }) => children,
        };
      }
      return mocks[name] ?? require(name);
    },
  });
  return exports;
}

const { SiteLanguageSwitch } = loadComponent(
  '../theme/components/SiteLanguageSwitch.tsx',
  { '../locale': { languageHref } },
);
const { SiteHeader } = loadComponent('../theme/components/SiteHeader.tsx', {
  './SiteLanguageSwitch': { SiteLanguageSwitch },
  './SwitchAppearance': {
    SwitchAppearance: () =>
      createElement('button', { role: 'switch', type: 'button' }),
  },
  '@rspress/core/theme-original': {
    NavTitle: () => createElement('a', {}, 'Snow Shot'),
    Search: () => createElement('button', { type: 'button' }, 'Search'),
    SocialLinks: () => createElement('a', {}, 'GitHub'),
    SvgWrapper: () => null,
    NavList: ({ items }) =>
      createElement(
        'ul',
        {},
        items.map((item) =>
          createElement(
            'li',
            { key: item.link },
            createElement('a', { href: item.link }, item.text),
          ),
        ),
      ),
  },
});

for (const language of ['en', 'zh']) {
  const prefix = language === 'zh' ? '/zh' : '';
  for (const path of [
    '/index.html',
    '/download.html',
    '/about.html',
    '/privacy.html',
    '/terms.html',
    '/changelog.html',
    '/guides/index.html',
    '/guides/capture/scrolling.html',
    '/blog/index.html',
    '/blog/scrolling-capture-fixes.html',
  ]) {
    it(`provides one language switch and appearance control on ${prefix}${path}`, () => {
      locale = language;
      location = { pathname: `${prefix}${path}`, search: '', hash: '' };
      const html = renderToStaticMarkup(createElement(SiteHeader));
      assert.match(html, /<header class="rp-nav snow-site-header">/);
      assert.equal((html.match(/rel="alternate"/g) ?? []).length, 1);
      assert.equal((html.match(/role="switch"/g) ?? []).length, 1);
      const target = language === 'zh' ? 'en' : 'zh';
      assert.ok(
        html.includes(`href="${languageHref(`${prefix}${path}`, target)}"`),
      );
      // Desktop and mobile navigation keep the same localized destinations.
      for (const key of ['guides', 'download', 'blog', 'changelog', 'about']) {
        const href = siteLinks(language)[key].href;
        assert.equal(html.split(`href="${href}"`).length - 1, 2, href);
      }
    });
  }

  it(`preserves query parameters and fragments when switching from ${language}`, () => {
    locale = language;
    location = {
      pathname: `${prefix}/download.html`,
      search: '?os=windows&arch=x64',
      hash: '#packages',
    };
    const link = SiteLanguageSwitch();
    const targetPrefix = language === 'zh' ? '' : '/zh';
    assert.equal(
      link.props.href,
      `${targetPrefix}/download.html?os=windows&arch=x64#packages`,
    );
    // Download selectors update history without updating useLocation.
    currentWindow.location.href = `http://localhost${prefix}/download.html?os=macos&arch=arm64#mini`;
    const anchor = { href: link.props.href };
    link.props.onClick({ currentTarget: anchor });
    assert.equal(
      anchor.href,
      `${targetPrefix}/download.html?os=macos&arch=arm64#mini`,
    );
  });
}
