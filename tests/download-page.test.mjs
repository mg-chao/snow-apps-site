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
function loadComponent(filename, modules, globals = {}) {
  const source = readFileSync(
    new URL(`../theme/components/DownloadPage/${filename}`, import.meta.url),
    'utf8',
  );
  const compiled = transpileModule(source, {
    compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
  }).outputText;
  const exports = {};
  runInNewContext(compiled, {
    ...globals,
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

function render(
  locale,
  platform,
  architecture = platform === 'macos' ? 'arm64' : 'x64',
) {
  const exports = loadComponent('index.tsx', {
    '@rspress/core/theme-original': { IconArrowDown: () => null },
    '../../platform': {
      useResolvedDownloadTarget: () => ({ platform, architecture }),
    },
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

describe('architecture-specific downloads', () => {
  for (const locale of ['en', 'zh']) {
    const host = locale === 'zh' ? 'gitee.com' : 'github.com';

    it(`renders every native Windows ARM64 package in ${locale}`, () => {
      const html = render(locale, 'windows', 'arm64');
      assert.equal((html.match(/class="snow-download-card /g) ?? []).length, 4);
      assert.match(html, /<option value="windows-arm64" selected="">/);
      for (const asset of [
        'windowsArm64Online',
        'windowsArm64Offline',
        'windowsArm64Portable',
        'windowsArm64MiniOnline',
        'windowsArm64MiniPortable',
      ]) {
        const url = releaseDownloadUrl(locale, asset);
        assert.equal(new URL(url).hostname, host);
        assert.ok(html.includes(`href="${url}"`));
        assert.match(releaseAssets[asset], /-windows-arm64-/);
        assert.ok(html.includes(releaseAssets[asset]));
      }
      assert.ok(!html.includes('-windows-x64-'));
      assert.ok(!html.includes('-macos-'));
      assert.ok(
        !html.includes(
          `snow-shot-mini-${releaseVersion}-windows-arm64-offline.exe`,
        ),
      );
    });

    it(`renders the Intel Mac package without a Mini download in ${locale}`, () => {
      const html = render(locale, 'macos', 'x64');
      const filename = `snow-shot-${releaseVersion}-macos-x86_64.dmg`;
      assert.equal(releaseAssets.macosX64Dmg, filename);
      assert.equal((html.match(/class="snow-download-card /g) ?? []).length, 1);
      assert.match(html, /snow-download-grid--single/);
      assert.match(html, /<option value="macos-x64" selected="">/);
      assert.ok(
        html.includes(`href="${releaseDownloadUrl(locale, 'macosX64Dmg')}"`),
      );
      assert.equal(
        new URL(releaseDownloadUrl(locale, 'macosX64Dmg')).hostname,
        host,
      );
      assert.ok(html.includes(filename));
      assert.ok(!html.includes('-macos-arm64.dmg'));
      assert.ok(!html.includes('-macos-x64.dmg'));
      assert.ok(!html.includes('snow-download-card--mini'));
      assert.ok(!html.includes('<option value="mini">'));
      assert.ok(!html.includes('id="snow-macos-install-edition"'));
      assert.ok(!html.includes('--edition mini'));
      assert.match(html, /macOS 15/);
      assert.ok(
        html.includes(
          `href="${releaseDownloadUrl(locale, 'macosInstallScript')}"`,
        ),
      );
    });

    it(`offers all four systems and chip guidance when detection is unavailable in ${locale}`, () => {
      const html = render(locale, 'macos', null);
      for (const system of [
        'windows-x64',
        'windows-arm64',
        'macos-arm64',
        'macos-x64',
      ]) {
        assert.ok(html.includes(`<option value="${system}"`));
      }
      assert.ok(html.includes('aria-describedby="snow-download-system-hint"'));
      assert.ok(html.includes('id="snow-download-system-hint"'));
      assert.ok(
        !render(locale, 'macos', 'x64').includes(
          'id="snow-download-system-hint"',
        ),
      );
    });
  }

  it('keeps a manual selection when CPU hints arrive and preserves the URL context', () => {
    let override = null;
    let detected = { platform: 'windows', architecture: null };
    let remembered;
    const exports = loadComponent(
      'index.tsx',
      {
        '@rspress/core/theme-original': { IconArrowDown: () => null },
        react: {
          useState: () => [
            override,
            (next) => {
              override = next;
            },
          ],
        },
        '../../platform': { useResolvedDownloadTarget: () => detected },
        './MacInstallOption': macInstall,
        './MirrorLink': { MirrorLink: () => null },
        './releaseLinks': releaseLinks,
      },
      {
        URL,
        window: {
          location: {
            href: 'https://snowshot.top/zh/download?source=home&os=windows#packages',
          },
          history: {
            replaceState: (_state, _title, url) => {
              remembered = url;
            },
          },
        },
      },
    );

    function findElement(node, predicate) {
      if (!node || typeof node !== 'object') return null;
      if (predicate(node)) return node;
      const children = node.props?.children;
      for (const child of Array.isArray(children)
        ? children.flat()
        : [children]) {
        const found = findElement(child, predicate);
        if (found) return found;
      }
      return null;
    }

    const tree = exports.DownloadPage({ locale: 'zh' });
    const selector = findElement(
      tree,
      (node) => node.type?.name === 'SystemSelect',
    );
    const select = findElement(
      selector.type(selector.props),
      (node) => node.type === 'select',
    );
    select.props.onChange({ target: { value: 'macos-x64' } });
    assert.equal(
      remembered,
      '/zh/download?source=home&os=macos&arch=x64#packages',
    );
    detected = { platform: 'windows', architecture: 'arm64' };
    const html = renderToStaticMarkup(
      createElement(exports.DownloadPage, { locale: 'zh' }),
    );
    assert.match(html, /<option value="macos-x64" selected="">/);
    assert.ok(html.includes(releaseAssets.macosX64Dmg));
    assert.ok(!html.includes('-windows-arm64-'));
  });
});

describe('macOS terminal installation', () => {
  it('uses the full edition for Intel even if the previous selection was Mini', () => {
    const { MacInstallOption } = loadComponent('MacInstallOption.tsx', {
      react: { useState: () => ['mini', () => {}] },
      './releaseLinks': releaseLinks,
    });
    const html = renderToStaticMarkup(
      createElement(MacInstallOption, {
        locale: 'en',
        architecture: 'x64',
      }),
    );
    assert.ok(html.includes('--edition full'));
    assert.ok(!html.includes('--edition mini'));
    assert.ok(!html.includes('id="snow-macos-install-edition"'));
  });

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
