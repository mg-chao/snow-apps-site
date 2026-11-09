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
runInNewContext(compiled, {
  exports,
  require(name) {
    if (name === './style.css') return {};
    if (name === '@rspress/core/runtime') return { useHead() {} };
    return require(name);
  },
});

for (const locale of ['en', 'zh']) {
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
}
