import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { describe, it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';
import {
  releaseAssets,
  releaseDownloadUrl,
  releaseVersion,
} from '../theme/components/DownloadPage/releaseLinks.ts';

const require = createRequire(import.meta.url);
const source = readFileSync(
  new URL('../theme/components/DownloadPage/index.tsx', import.meta.url),
  'utf8',
);
const compiled = transpileModule(source, {
  compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
}).outputText;

function render(locale, platform) {
  const exports = {};
  runInNewContext(compiled, {
    exports,
    require(name) {
      switch (name) {
        case '@rspress/core/theme-original':
          return { IconArrowDown: () => null };
        case '../../platform':
          return { useResolvedDownloadPlatform: () => platform };
        case './MirrorLink':
          return { MirrorLink: () => null };
        case './releaseLinks':
          return { releaseAssets, releaseDownloadUrl };
        default:
          return require(name);
      }
    },
  });
  return renderToStaticMarkup(createElement(exports.DownloadPage, { locale }));
}

describe('Snow Shot Mini downloads', () => {
  for (const locale of ['en', 'zh']) {
    const host = locale === 'zh' ? 'gitee.com' : 'github.com';

    it(`renders both Windows Mini packages and all full packages in ${locale}`, () => {
      const html = render(locale, 'windows');
      assert.equal((html.match(/<article /g) ?? []).length, 4);
      assert.match(html, /snow-download-card--mini/);
      assert.match(html, /snow-download-grid--paired/);
      for (const asset of [
        'windowsOnline',
        'windowsOffline',
        'windowsPortable',
        'windowsMiniOnline',
        'windowsMiniPortable',
      ]) {
        assert.ok(html.includes(`href="${releaseDownloadUrl(locale, asset)}"`));
        const url = new URL(releaseDownloadUrl(locale, asset));
        assert.equal(url.hostname, host);
        assert.equal(
          url.pathname,
          `/mg-chao/snow-apps/releases/download/v${releaseVersion}_snow-shot/${releaseAssets[asset]}`,
        );
      }
      assert.ok(!html.includes('-macos-arm64.dmg'));
      assert.ok(
        !html.includes(
          `snow-shot-mini-${releaseVersion}-windows-x64-offline.exe`,
        ),
      );
    });

    it(`renders the full and Mini Apple Silicon disk images in ${locale}`, () => {
      const html = render(locale, 'macos');
      assert.equal((html.match(/<article /g) ?? []).length, 2);
      assert.match(html, /snow-download-card--mini/);
      for (const asset of ['macosDmg', 'macosMiniDmg']) {
        assert.ok(html.includes(`href="${releaseDownloadUrl(locale, asset)}"`));
        assert.equal(new URL(releaseDownloadUrl(locale, asset)).hostname, host);
      }
      assert.match(html, /macOS 15/);
      assert.ok(!html.includes('-windows-x64-'));
      assert.ok(!html.includes('-macos-x64.dmg'));
    });
  }
});
