// Inlined into the HTML head so language selection happens before rendering.
(() => {
  const storageKey = 'snow-shot-language';
  const supportedLanguages = ['en', 'zh'];
  const report = (decision, details = {}) => {
    if (!window.__SNOW_SHOT_LOCALE_DEBUG__) return;
    window.dispatchEvent(
      new CustomEvent('snow-shot:locale-debug', {
        detail: {
          revision: 'locale-debug-4',
          decision,
          ...details,
        },
      }),
    );
  };
  report('language detection started');

  // Only an explicit language-menu choice is persisted. A visit is not a choice.
  document.addEventListener(
    'click',
    (event) => {
      if (!(event.target instanceof Element)) return;
      const link = event.target.closest('a[hreflang][rel~="alternate"]');
      if (
        !link ||
        new URL(link.href, location.href).origin !== location.origin
      ) {
        return;
      }
      const language = link.getAttribute('hreflang');
      if (!supportedLanguages.includes(language)) return;
      try {
        localStorage.setItem(storageKey, language);
        report('manual language choice saved', { language });
      } catch (error) {
        report('manual language choice could not be saved', {
          language,
          error: error.message,
        });
        // The menu still works when browser settings prevent storing preferences.
      }
    },
    true,
  );

  if (/bot|spider|crawl|lighthouse/i.test(navigator.userAgent)) {
    report('skipped: crawler user agent');
    return;
  }

  // An explicit locale in the URL takes precedence over automatic selection.
  const firstSegment = location.pathname.split('/')[1];
  if (supportedLanguages.includes(firstSegment)) {
    report('kept explicit URL language', { language: firstSegment });
    return;
  }

  let preferredLanguage;
  let source = 'saved site preference';
  try {
    preferredLanguage = localStorage.getItem(storageKey);
  } catch (error) {
    report('saved preference could not be read', { error: error.message });
    // Browser language detection must also work with storage disabled.
  }

  if (!supportedLanguages.includes(preferredLanguage)) {
    source = 'browser preferences';
    const languages = navigator.languages?.length
      ? navigator.languages
      : [navigator.language];
    const browserLanguages = languages.map(
      (language) => language.toLowerCase().split('-')[0],
    );
    const regionalLanguage = Intl.DateTimeFormat()
      .resolvedOptions()
      .locale.toLowerCase()
      .split('-')[0];
    report('automatic language inputs', { browserLanguages, regionalLanguage });

    // Chromium can expose an English-only content-language list while its
    // regional locale is Chinese. That locale is an independent signal;
    // an explicit site preference was already handled above.
    if (regionalLanguage === 'zh') {
      preferredLanguage = 'zh';
      source = 'Chinese regional locale';
    } else {
      preferredLanguage = browserLanguages.find((language) =>
        supportedLanguages.includes(language),
      );
    }
  }

  if (preferredLanguage === 'zh') {
    const target = `/zh${location.pathname}${location.search}${location.hash}`;
    report('redirecting to Chinese', { preferredLanguage, source, target });
    location.replace(target);
  } else {
    report('staying on English', {
      preferredLanguage: preferredLanguage ?? 'en (fallback)',
      source,
    });
  }
})();
