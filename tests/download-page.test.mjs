import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { describe, it } from 'node:test';
import { runInNewContext } from 'node:vm';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { JsxEmit, ModuleKind, transpileModule } from 'typescript';
import {
  macosInstallCommand,
  releaseAssets,
  releaseDownloadUrl,
  releaseVersion,
} from '../theme/components/DownloadPage/releaseLinks.ts';

const require = createRequire(import.meta.url);
function loadComponent(filename, modules) {
  const source = readFileSync(
    new URL(`../theme/components/DownloadPage/${filename}`, import.meta.url),
    'utf8',
  );
  const compiled = transpileModule(source, {
    compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
  }).outputText;
  const exports = {};
  runInNewContext(compiled, {
    exports,
    require(name) {
      return modules[name] ?? require(name);
    },
  });
  return exports;
}

const releaseLinks = { macosInstallCommand, releaseAssets, releaseDownloadUrl };
const macInstall = loadComponent('MacInstallOption.tsx', {
  './releaseLinks': releaseLinks,
});

function render(locale, platform) {
  const exports = loadComponent('index.tsx', {
    '@rspress/core/theme-original': { IconArrowDown: () => null },
    '../../platform': { useResolvedDownloadPlatform: () => platform },
    './MacInstallOption': macInstall,
    './MirrorLink': { MirrorLink: () => null },
    './releaseLinks': releaseLinks,
  });
  return renderToStaticMarkup(createElement(exports.DownloadPage, { locale }));
}

describe('Snow Shot Mini downloads', () => {
  for (const locale of ['en', 'zh']) {
    const host = locale === 'zh' ? 'gitee.com' : 'github.com';

    it(`renders both Windows Mini packages and all full packages in ${locale}`, () => {
      const html = render(locale, 'windows');
      assert.equal((html.match(/class="snow-download-card /g) ?? []).length, 4);
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
      assert.ok(!html.includes('install-snow-shot-macos.sh'));
      assert.ok(
        !html.includes(
          `snow-shot-mini-${releaseVersion}-windows-x64-offline.exe`,
        ),
      );
    });

    it(`renders the full and Mini Apple Silicon disk images in ${locale}`, () => {
      const html = render(locale, 'macos');
      assert.equal((html.match(/class="snow-download-card /g) ?? []).length, 2);
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

describe('macOS terminal installation', () => {
  for (const locale of ['en', 'zh']) {
    const language = locale === 'zh' ? 'zh-CN' : 'en';
    const host = locale === 'zh' ? 'gitee.com' : 'github.com';

    it(`exposes the release script and edition selector in ${locale}`, () => {
      const html = render(locale, 'macos');
      const scriptUrl = releaseDownloadUrl(locale, 'macosInstallScript');
      assert.equal(new URL(scriptUrl).hostname, host);
      assert.equal(
        new URL(scriptUrl).pathname,
        `/mg-chao/snow-apps/releases/download/v${releaseVersion}_snow-shot/install-snow-shot-macos.sh`,
      );
      assert.ok(html.includes(`href="${scriptUrl}"`));
      assert.ok(html.includes('class="snow-macos-install"'));
      assert.match(
        html,
        /<option value="full" selected="">Snow Shot<\/option>/,
      );
      assert.match(html, /<option value="mini">Snow Shot Mini<\/option>/);
      assert.match(html, /<textarea[^>]+readonly=""/i);
      assert.ok(
        html.includes(
          `bash install-snow-shot-macos.sh --edition full --lang ${language}`,
        ),
      );
      assert.ok(!html.includes('snowshot.top/setup/'));
    });

    for (const edition of ['full', 'mini']) {
      it(`downloads the script before installing ${edition} in ${locale}`, () => {
        const command = macosInstallCommand(locale, edition);
        const [download, install] = command.split(' &&\n');
        assert.ok(
          download.endsWith(releaseDownloadUrl(locale, 'macosInstallScript')),
        );
        assert.ok(download.includes('--fail --location'));
        assert.ok(download.includes("--proto '=https' --proto-redir '=https'"));
        assert.ok(download.includes('--output install-snow-shot-macos.sh'));
        assert.equal(
          install,
          `bash install-snow-shot-macos.sh --edition ${edition} --lang ${language}`,
        );
      });
    }
  }
});
