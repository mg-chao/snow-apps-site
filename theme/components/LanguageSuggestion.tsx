import { useLang, useLocation, usePage } from '@rspress/core/runtime';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  isSiteLocale,
  languageHref,
  languagePreferenceKey,
  preferredLanguage,
} from '../locale';
import type { SiteLocale } from '../site-structure';
import './LanguageSuggestion.css';

export function LanguageSuggestion() {
  const locale = useLang() === 'zh' ? 'zh' : 'en';
  const { pathname, search, hash } = useLocation();
  const { page } = usePage();
  const [preferred, setPreferred] = useState<SiteLocale>();
  const chosenLanguage = useRef<SiteLocale | null>(null);
  const rememberLanguage = useCallback((language: SiteLocale) => {
    chosenLanguage.current = language;
    setPreferred(language);
    try {
      localStorage.setItem(languagePreferenceKey, language);
    } catch {
      // Keep the choice for this page when preference storage is unavailable.
    }
  }, []);

  useEffect(() => {
    const update = () => {
      let savedLanguage: string | null = chosenLanguage.current;
      try {
        savedLanguage ??= localStorage.getItem(languagePreferenceKey);
      } catch {
        // Browser preferences remain available without local storage.
      }
      let regionalLocale = '';
      try {
        regionalLocale = Intl.DateTimeFormat().resolvedOptions().locale;
      } catch {
        // The browser language list is sufficient if regional data is unavailable.
      }
      const language = preferredLanguage({
        savedLanguage,
        languages: navigator.languages?.length
          ? navigator.languages
          : [navigator.language],
        regionalLocale,
      });
      setPreferred(language);
      window.dispatchEvent(
        new CustomEvent('snow-shot:locale-debug', {
          detail: {
            revision: 'locale-suggestion-1',
            decision: 'language preference detected; URL preserved',
            preferredLanguage: language,
          },
        }),
      );
    };
    const selectLanguage = (event: MouseEvent) => {
      if (!(event.target instanceof Element)) return;
      const link = event.target.closest<HTMLAnchorElement>(
        'a[hreflang][rel~="alternate"]',
      );
      if (!link || new URL(link.href).origin !== location.origin) return;
      const language = link.getAttribute('hreflang');
      if (isSiteLocale(language)) rememberLanguage(language);
    };
    const syncPreference = (event: StorageEvent) => {
      if (event.key !== null && event.key !== languagePreferenceKey) return;
      chosenLanguage.current = null;
      update();
    };
    update();
    document.addEventListener('click', selectLanguage, true);
    window.addEventListener('languagechange', update);
    window.addEventListener('storage', syncPreference);
    return () => {
      document.removeEventListener('click', selectLanguage, true);
      window.removeEventListener('languagechange', update);
      window.removeEventListener('storage', syncPreference);
    };
  }, [rememberLanguage]);

  if (!preferred || preferred === locale || page.pageType === '404')
    return null;
  const isZh = preferred === 'zh';
  return (
    <aside
      className="snow-language-suggestion"
      aria-label={isZh ? '选择阅读语言' : 'Choose your reading language'}
      lang={preferred}
    >
      <p>
        {isZh
          ? '此页面也有简体中文版。'
          : 'This page is also available in English.'}
      </p>
      <div className="snow-language-suggestion__actions">
        <a
          href={languageHref(`${pathname}${search}${hash}`, preferred)}
          hrefLang={preferred}
          rel="alternate"
          onClick={(event) => {
            // Download selectors can update the URL without a router navigation.
            event.currentTarget.href = languageHref(location.href, preferred);
          }}
        >
          {isZh ? '切换到简体中文' : 'Read in English'}
        </a>
        <button type="button" onClick={() => rememberLanguage(locale)}>
          {isZh ? '继续阅读英文' : 'Keep reading in Chinese'}
        </button>
      </div>
    </aside>
  );
}
