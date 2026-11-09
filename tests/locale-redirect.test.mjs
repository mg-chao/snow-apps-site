import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { languageHref, preferredLanguage } from '../theme/locale.ts';

describe('language suggestions', () => {
  for (const language of ['zh', 'zh-CN', 'zh-TW', 'zh-Hans-CN', 'ZH-cn']) {
    it(`recognizes ${language} as a Chinese preference`, () => {
      assert.equal(preferredLanguage({ languages: [language, 'en'] }), 'zh');
    });
  }

  it('uses the first supported browser language', () => {
    assert.equal(
      preferredLanguage({ languages: ['fr-FR', 'zh-CN', 'en'] }),
      'zh',
    );
    assert.equal(preferredLanguage({ languages: ['en-US', 'zh-CN'] }), 'en');
    assert.equal(preferredLanguage({ languages: ['fr-FR', 'ja'] }), undefined);
    assert.equal(preferredLanguage({ languages: [] }), undefined);
  });

  for (const regionalLocale of ['zh-CN', 'zh-TW', 'zh-Hans-CN', 'zh-Hant-HK']) {
    it(`recognizes ${regionalLocale} even with English-only browser languages`, () => {
      assert.equal(
        preferredLanguage({ languages: ['en-US'], regionalLocale }),
        'zh',
      );
    });
  }

  it('uses saved explicit choices before browser and regional preferences', () => {
    assert.equal(
      preferredLanguage({
        savedLanguage: 'en',
        languages: ['zh-CN'],
        regionalLocale: 'zh-CN',
      }),
      'en',
    );
    assert.equal(
      preferredLanguage({ savedLanguage: 'zh', languages: ['en'] }),
      'zh',
    );
  });

  it('ignores invalid preferences and unsupported regional locales', () => {
    assert.equal(
      preferredLanguage({ savedLanguage: 'invalid', languages: ['zh-CN'] }),
      'zh',
    );
    assert.equal(
      preferredLanguage({
        languages: ['en-US', 'zh-CN'],
        regionalLocale: 'fr-FR',
      }),
      'en',
    );
  });
});

describe('explicit language switch destinations', () => {
  for (const [path, english] of [
    ['/', '/index.html'],
    ['/index.html', '/index.html'],
    ['/zh', '/index.html'],
    ['/zh/', '/index.html'],
    [
      '/download?os=macos&arch=x64#packages',
      '/download.html?os=macos&arch=x64#packages',
    ],
    [
      '/zh/download.html?os=windows&arch=arm64#mini',
      '/download.html?os=windows&arch=arm64#mini',
    ],
    ['/zh/guides/', '/guides/index.html'],
    [
      '/guides/capture/scrolling.html#preview',
      '/guides/capture/scrolling.html#preview',
    ],
    ['/zh/changelog.html#v1-5-2', '/changelog.html#v1-5-2'],
  ]) {
    it(`preserves the document, parameters and fragment for ${path}`, () => {
      assert.equal(languageHref(path, 'en'), english);
      assert.equal(languageHref(path, 'zh'), `/zh${english}`);
    });
  }

  it('works with the current browser URL after download selectors change it', () => {
    assert.equal(
      languageHref(
        'http://localhost:4173/download.html?os=macos&arch=arm64#full',
        'zh',
      ),
      '/zh/download.html?os=macos&arch=arm64#full',
    );
  });
});
