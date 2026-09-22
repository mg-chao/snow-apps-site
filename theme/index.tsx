// Learn how to customize the theme: https://rspress.rs/guide/basic/custom-theme
import './index.css';

import { useLang } from '@rspress/core/runtime';
import { Layout as OriginalLayout } from '@rspress/core/theme-original';

export * from '@rspress/core/theme-original';
export { DownloadPage } from './components/DownloadPage';
export { HomeLayout } from './components/HomeLayout';
export { SwitchAppearance } from './components/SwitchAppearance';

function SnowNavTitle() {
  return (
    <a aria-label="Snow Shot home" className="snow-nav-brand" href="/">
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
      <OriginalLayout
        navTitle={<SnowNavTitle />}
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
