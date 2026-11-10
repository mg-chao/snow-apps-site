import { useLang, useLocation } from '@rspress/core/runtime';
import { languageHref } from '../locale';
import './SiteLanguageSwitch.css';

/** Keep readers on the corresponding page when they change language. */
export function SiteLanguageSwitch() {
  const { pathname, search, hash } = useLocation();
  const lang = useLang();
  const isZh = lang === 'zh';
  const target = isZh ? 'en' : 'zh';
  return (
    <a
      className="snow-site-language"
      href={languageHref(`${pathname}${search}${hash}`, target)}
      onClick={(event) => {
        // Download selectors can update history without a router navigation.
        event.currentTarget.href = languageHref(window.location.href, target);
      }}
      lang={target}
      hrefLang={target}
      rel="alternate"
      title={isZh ? 'Read this page in English' : '阅读此页面的中文版'}
    >
      {isZh ? 'English' : '简体中文'}
    </a>
  );
}
