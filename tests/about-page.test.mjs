import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';

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

  it(`offers both QQ groups with their join links and numbers in ${locale}`, () => {
    const html = renderToStaticMarkup(
      createElement(exports.AboutPage, { locale }),
    );
    const links = [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].filter(
      (match) => match[1].includes('class="snow-about__group"'),
    );
    assert.equal(links.length, 2);
    for (const [name, number, href] of [
      ['3', '1037819112', 'https://qm.qq.com/q/Ts3cwNdykW'],
      ['4', '1131891935', 'https://qm.qq.com/q/GfZvSHi6E'],
    ]) {
      const link = links.find((match) => match[1].includes(`href="${href}"`));
      assert.ok(link, `QQ group ${name} has its exact join link`);
      assert.ok(
        link[2].includes(
          `${locale === 'zh' ? 'QQ 交流群' : 'QQ Group'} ${name}`,
        ),
      );
      assert.ok(link[2].includes(`<span>${number}</span>`));
      assert.ok(link[1].includes('target="_blank"'));
      assert.ok(link[1].includes('rel="noopener noreferrer"'));
    }
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
