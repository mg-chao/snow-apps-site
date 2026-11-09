import { defaultLanguageUrl, siteOrigin } from './seo';
import type { SiteLocale } from './site-structure';

export const languagePreferenceKey = 'snow-shot-language';

export function isSiteLocale(language: string | null): language is SiteLocale {
  return language === 'en' || language === 'zh';
}

/** Preferences suggest a language; the requested URL always determines content. */
export function preferredLanguage({
  savedLanguage,
  languages,
  regionalLocale = '',
}: {
  savedLanguage?: string | null;
  languages: readonly string[];
  regionalLocale?: string;
}): SiteLocale | undefined {
  if (savedLanguage && isSiteLocale(savedLanguage)) return savedLanguage;
  // Chromium can report English content languages with a Chinese regional locale.
  if (regionalLocale.toLowerCase().split('-')[0] === 'zh') return 'zh';
  return languages
    .map((language) => language.toLowerCase().split('-')[0])
    .find(isSiteLocale);
}

export function languageHref(path: string, language: SiteLocale) {
  const url = new URL(path, siteOrigin);
  const englishPath = new URL(defaultLanguageUrl(path)).pathname;
  return `${language === 'zh' ? '/zh' : ''}${englishPath}${url.search}${url.hash}`;
}
