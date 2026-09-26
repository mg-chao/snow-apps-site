import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { describe, it } from 'node:test';
import { runInNewContext } from 'node:vm';

const script = readFileSync(
  new URL('../scripts/locale-redirect.js', import.meta.url),
  'utf8',
);
const preferenceKey = 'snow-shot-language';

function visit({
  url = '/',
  languages = ['zh-CN', 'en'],
  language = languages?.[0] ?? 'zh-CN',
  intlLocale = 'en-US',
  storage = new Map(),
  blockedStorage = false,
  userAgent = 'Mozilla/5.0 Chrome/140.0.0.0',
} = {}) {
  const location = new URL(url, 'https://snow.example');
  let redirect;
  location.replace = (target) => {
    redirect = target;
  };
  let click;
  class Element {
    constructor(link) {
      this.link = link;
    }
    closest() {
      return this.link;
    }
  }
  const localStorage = {
    getItem(key) {
      return storage.get(key) ?? null;
    },
    setItem(key, value) {
      storage.set(key, value);
    },
  };
  const context = {
    window: {},
    location,
    navigator: { languages, language, userAgent },
    document: {
      addEventListener(type, listener) {
        assert.equal(type, 'click');
        click = listener;
      },
    },
    Element,
    URL,
    URLSearchParams,
    Intl: {
      DateTimeFormat: () => ({
        resolvedOptions: () => ({ locale: intlLocale }),
      }),
    },
    get localStorage() {
      if (blockedStorage) throw new Error('Storage access denied');
      return localStorage;
    },
  };
  runInNewContext(script, context);
  return {
    redirect,
    storage,
    selectLanguage(lang, href = lang === 'zh' ? '/zh/' : '/') {
      click({
        target: new Element({ href, getAttribute: () => lang }),
      });
    },
    clickOrdinaryLink() {
      click({ target: new Element(null) });
    },
  };
}

describe('browser language selection', () => {
  for (const language of ['zh', 'zh-CN', 'zh-TW', 'zh-Hans-CN', 'ZH-cn']) {
    it(`opens Chinese for ${language}`, () => {
      assert.equal(visit({ languages: [language, 'en'] }).redirect, '/zh/');
    });
  }

  it('redirects returning visitors with the old Rspress visited flag', () => {
    const storage = new Map([['rspress-visited', '1']]);
    assert.equal(visit({ storage }).redirect, '/zh/');
    assert.equal(visit({ storage }).redirect, '/zh/');
    assert.equal(storage.has(preferenceKey), false);
  });

  it('follows changed browser preferences on a later visit', () => {
    const storage = new Map();
    assert.equal(visit({ languages: ['en-US'], storage }).redirect, undefined);
    assert.equal(visit({ languages: ['zh-CN'], storage }).redirect, '/zh/');
  });

  it('uses the first supported language in browser preference order', () => {
    assert.equal(
      visit({ languages: ['fr-FR', 'zh-CN', 'en'] }).redirect,
      '/zh/',
    );
    assert.equal(visit({ languages: ['en-US', 'zh-CN'] }).redirect, undefined);
    assert.equal(
      visit({ languages: ['zh-CN', 'en'], language: 'en-US' }).redirect,
      '/zh/',
    );
  });

  it('uses Chinese for the reported Edge language and regional-locale mismatch', () => {
    const storage = new Map([['rspress-visited', '1']]);
    assert.equal(
      visit({
        url: '/index.html',
        languages: ['en-US', 'zh-CN'],
        language: 'en-US',
        intlLocale: 'zh-CN',
        storage,
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0',
      }).redirect,
      '/zh/index.html',
    );
    assert.equal(storage.has(preferenceKey), false);
  });

  for (const intlLocale of ['zh-TW', 'zh-Hans-CN', 'zh-Hant-HK']) {
    it(`recognizes the Chinese regional locale ${intlLocale}`, () => {
      assert.equal(
        visit({ languages: ['en-US', 'zh-CN'], intlLocale }).redirect,
        '/zh/',
      );
    });
  }

  for (const url of ['/', '/index.html', '/about.html?from=home#features']) {
    it(`uses the reported Chinese regional locale with an English-only list at ${url}`, () => {
      assert.equal(
        visit({
          url,
          languages: ['en-US', 'en'],
          language: 'en-US',
          intlLocale: 'zh-CN',
        }).redirect,
        `/zh${url}`,
      );
    });
  }

  it('uses the Chinese regional locale when the language list is unavailable', () => {
    assert.equal(
      visit({ languages: [], language: 'en-US', intlLocale: 'zh-CN' }).redirect,
      '/zh/',
    );
  });

  it('keeps browser preference order for an unsupported regional locale', () => {
    assert.equal(
      visit({ languages: ['en-US', 'zh-CN'], intlLocale: 'fr-FR' }).redirect,
      undefined,
    );
  });

  it('lets a saved English choice override the Chinese regional locale', () => {
    assert.equal(
      visit({
        languages: ['en-US', 'en'],
        intlLocale: 'zh-CN',
        storage: new Map([[preferenceKey, 'en']]),
      }).redirect,
      undefined,
    );
  });

  it('falls back to navigator.language when no language list is available', () => {
    assert.equal(visit({ languages: [], language: 'zh-CN' }).redirect, '/zh/');
    assert.equal(
      visit({ languages: null, language: 'zh-CN' }).redirect,
      '/zh/',
    );
  });

  it('keeps English for unsupported browser languages', () => {
    assert.equal(visit({ languages: ['fr-FR', 'ja'] }).redirect, undefined);
  });

  it('detects the language even when storage access throws', () => {
    const page = visit({ blockedStorage: true });
    assert.equal(page.redirect, '/zh/');
    assert.doesNotThrow(() => page.selectLanguage('en'));
  });

  it('ignores invalid saved preferences', () => {
    const storage = new Map([[preferenceKey, 'invalid']]);
    assert.equal(visit({ storage }).redirect, '/zh/');
  });
});

describe('routes and explicit language choices', () => {
  for (const url of [
    '/index.html',
    '/download',
    '/about.html?from=home#features',
  ]) {
    it(`preserves the entire URL when redirecting ${url}`, () => {
      assert.equal(visit({ url }).redirect, `/zh${url}`);
    });
  }

  for (const url of ['/zh', '/zh/', '/zh/index.html', '/zh/download.html']) {
    it(`honors the explicit Chinese URL ${url}`, () => {
      assert.equal(visit({ url, languages: ['en'] }).redirect, undefined);
      assert.equal(visit({ url }).redirect, undefined);
    });
  }

  it('remembers English chosen in the menu across page loads', () => {
    const page = visit({ url: '/zh/' });
    page.selectLanguage('en');
    assert.equal(page.storage.get(preferenceKey), 'en');
    assert.equal(visit({ storage: page.storage }).redirect, undefined);
    assert.equal(
      visit({ url: '/download.html', storage: page.storage }).redirect,
      undefined,
    );
  });

  it('remembers Chinese chosen in an English browser', () => {
    const page = visit({ languages: ['en'] });
    page.selectLanguage('zh');
    assert.equal(
      visit({ languages: ['en'], storage: page.storage }).redirect,
      '/zh/',
    );
  });

  it('honors explicit Chinese URLs even with a saved English preference', () => {
    const storage = new Map([[preferenceKey, 'en']]);
    assert.equal(visit({ url: '/zh/about.html', storage }).redirect, undefined);
  });

  it('does not save ordinary navigation or external language links as choices', () => {
    const page = visit();
    page.clickOrdinaryLink();
    page.selectLanguage('zh', 'https://external.example/zh/');
    page.selectLanguage('fr');
    assert.equal(page.storage.has(preferenceKey), false);
  });

  it('does not redirect crawlers', () => {
    assert.equal(visit({ userAgent: 'Googlebot' }).redirect, undefined);
  });
});
