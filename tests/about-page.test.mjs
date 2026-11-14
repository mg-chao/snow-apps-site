import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';
import { siteLinks } from '../theme/site-structure.ts';

const require = createRequire(import.meta.url);
const source = readFileSync(
  new URL('../theme/components/AboutPage/index.tsx', import.meta.url),
  'utf8',
);
const compiled = transpileModule(source, {
  compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
}).outputText;
const exports = {};
const heads = [];
runInNewContext(compiled, {
  exports,
  require(name) {
    if (name === '../../site-structure') return { siteLinks };
    if (name === './style.css') return {};
    if (name === '@rspress/core/runtime') {
      return { useHead: (head) => heads.push(head) };
    }
    return require(name);
  },
});

for (const locale of ['en', 'zh']) {
  it(`keeps the browser and sharing titles consistent in ${locale}`, () => {
    renderToStaticMarkup(createElement(exports.AboutPage, { locale }));
    const head = heads.at(-1);
    const title = locale === 'zh' ? '关于 Snow Shot' : 'About Snow Shot';
    assert.equal(head.title, title);
    assert.equal(
      head.meta.find((meta) => meta.property === 'og:title')?.content,
      title,
    );
  });

  it(`offers only QQ Group 4 with its join link and number in ${locale}`, () => {
    const html = renderToStaticMarkup(
      createElement(exports.AboutPage, { locale }),
    );
    const links = [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].filter(
      (match) => match[1].includes('class="snow-about__group"'),
    );
    assert.equal(links.length, 1);
    const [link] = links;
    assert.ok(link[1].includes('href="https://qm.qq.com/q/GfZvSHi6E"'));
    assert.ok(
      link[2].includes(`${locale === 'zh' ? 'QQ 交流群' : 'QQ Group'} 4`),
    );
    assert.ok(link[2].includes('<span>1131891935</span>'));
    assert.ok(link[1].includes('target="_blank"'));
    assert.ok(link[1].includes('rel="noopener noreferrer"'));
    assert.ok(!html.includes('https://qm.qq.com/q/Ts3cwNdykW'));
  });

  it(`opens the local changelog in the current language while keeping contribution links external in ${locale}`, () => {
    const html = renderToStaticMarkup(
      createElement(exports.AboutPage, { locale }),
    );
    const links = [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].filter(
      (match) => match[1].includes('class="snow-about__resource"'),
    );
    assert.equal(links.length, 3);
    const changelogHref =
      locale === 'zh' ? '/zh/changelog.html' : '/changelog.html';
    const changelog = links.find((match) =>
      match[1].includes(`href="${changelogHref}"`),
    );
    assert.ok(changelog);
    assert.ok(!changelog[1].includes('target="_blank"'));
    for (const path of ['', '/issues']) {
      const external = links.find((match) =>
        match[1].includes(`href="https://github.com/mg-chao/snow-shot${path}"`),
      );
      assert.ok(external);
      assert.ok(external[1].includes('target="_blank"'));
      assert.ok(external[1].includes('rel="noopener noreferrer"'));
    }
  });
}
