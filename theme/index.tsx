// Learn how to customize the theme: https://rspress.rs/guide/basic/custom-theme
import './index.css';
import './components/GuideHome/style.css';

import { useLang } from '@rspress/core/runtime';
import { Layout as OriginalLayout } from '@rspress/core/theme-original';
import { SeoMetadata } from './components/SeoMetadata';
import { PageBreadcrumbs } from './components/PageBreadcrumbs';
import { LanguageSuggestion } from './components/LanguageSuggestion';
import { BlogArticleMeta, BlogRelated } from './components/Blog';
import { footerSections } from './site-structure';

export * from '@rspress/core/theme-original';
export { AboutPage } from './components/AboutPage';
export { DownloadPage } from './components/DownloadPage';
export { HomeLayout } from './components/HomeLayout';
export { SwitchAppearance } from './components/SwitchAppearance';
export { SiteHeader as Nav } from './components/SiteHeader';

function SnowNavTitle() {
  const lang = useLang();

  return (
    <a
      aria-label={lang === 'zh' ? 'Snow Shot 首页' : 'Snow Shot home'}
      className="snow-nav-brand"
      href={lang === 'zh' ? '/zh/index.html' : '/index.html'}
    >
      <img
        alt=""
        aria-hidden="true"
        className="snow-logo-mark"
        src="/app-icon.svg"
      />
      <span>Snow Shot</span>
    </a>
  );
}

export function Layout() {
  return (
    <>
      <div id="top" />
      <SeoMetadata />
      <OriginalLayout
        navTitle={<SnowNavTitle />}
        afterNav={
          <>
            <LanguageSuggestion />
            <PageBreadcrumbs placement="custom" />
          </>
        }
        beforeDocContent={
          <>
            <PageBreadcrumbs placement="doc" />
            <BlogArticleMeta />
          </>
        }
        afterDocContent={<BlogRelated />}
        bottom={<SnowGlobalFooter />}
      />
    </>
  );
}

function SnowGlobalFooter() {
  const lang = useLang();
  const isZh = lang === 'zh';

  return (
    <footer className="snow-home__footer snow-global-footer">
      <nav
        className="snow-footer-nav"
        aria-label={isZh ? '网站目录' : 'Site directory'}
      >
        {footerSections(isZh ? 'zh' : 'en').map((section) => (
          <div key={section.title}>
            <h2>{section.title}</h2>
            <ul>
              {section.links.map((link) => (
                <li key={link.href}>
                  <a href={link.href}>{link.label}</a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      <div className="snow-home__footer-main">
        <div className="snow-home__footer-brand">
          <img
            alt=""
            aria-hidden="true"
            className="snow-logo-mark"
            src="/app-icon.svg"
          />
          <span>Snow Shot</span>
        </div>
        <span>
          {isZh
            ? '优雅截图，出色工作。'
            : 'Screenshot simply. Work excellently.'}
        </span>
        <a href="#top">{isZh ? '返回顶部 ↑' : 'Back to top ↑'}</a>
      </div>
      <div className="snow-home__footer-legal">
        <span>© 2025 Snow Apps</span>
        <a href="https://github.com/mg-chao/snow-shot">
          {isZh ? '官方 GitHub 仓库' : 'Official GitHub repository'}
        </a>
        <a href={isZh ? '/zh/privacy.html' : '/privacy.html'}>
          {isZh ? '隐私政策' : 'Privacy policy'}
        </a>
        <a href={isZh ? '/zh/terms.html' : '/terms.html'}>
          {isZh ? '用户协议' : 'Terms of service'}
        </a>
        <a
          href="https://beian.miit.gov.cn/"
          target="_blank"
          rel="noopener noreferrer"
          className="snow-home__footer-icp"
        >
          赣ICP备2021006312号-3
        </a>
      </div>
    </footer>
  );
}
