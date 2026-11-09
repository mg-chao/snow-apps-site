import { useLang, useLocation } from '@rspress/core/runtime';
import { defaultLanguageUrl } from '../seo';
import './GuideLanguages.css';

/** Keep readers on the corresponding page when they change language. */
export function GuideLanguages() {
  const { pathname, search, hash } = useLocation();
  const lang = useLang();
  if (!/^\/(?:zh\/)?(?:guides(?:\/|$)|changelog(?:\.html)?\/?$)/.test(pathname))
    return null;
  const isZh = lang === 'zh';
  const englishPath = new URL(defaultLanguageUrl(pathname)).pathname;
  const suffix = /\/changelog(?:\.html)?\/?$/.test(pathname)
    ? `${search}${hash}`
    : '';
  return (
    <a
      className="snow-guide-language"
      href={`${isZh ? englishPath : `/zh${englishPath}`}${suffix}`}
      lang={isZh ? 'en' : 'zh'}
      hrefLang={isZh ? 'en' : 'zh'}
      rel="alternate"
      title={isZh ? 'Read this page in English' : '阅读此页面的中文版'}
    >
      {isZh ? 'English' : '简体中文'}
    </a>
  );
}
