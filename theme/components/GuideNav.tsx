import { NoSSR, useLang, useLocation, useNav } from '@rspress/core/runtime';
import {
  IconSmallMenu,
  Nav as OriginalNav,
  NavList,
  NavTitle,
  Search,
  SocialLinks,
  SvgWrapper,
} from '@rspress/core/theme-original';
import type { ComponentProps } from 'react';
import { SwitchAppearance } from './SwitchAppearance';
import './GuideNav.css';

/** Keep language and appearance controls outside the mobile menu trigger. */
export function Nav(props: ComponentProps<typeof OriginalNav>) {
  const { pathname } = useLocation();
  const items = useNav();
  const lang = useLang();
  if (
    !/^\/(?:zh\/)?(?:(?:guides|blog)(?:\/|$)|changelog(?:\.html)?\/?$)/.test(
      pathname,
    )
  ) {
    return <OriginalNav {...props} />;
  }
  return (
    <header className="rp-nav snow-guide-nav">
      <div className="rp-nav__left">
        {props.beforeNavTitle}
        {props.navTitle ?? <NavTitle />}
        {props.afterNavTitle}
      </div>
      <div className="rp-nav__right">
        {props.beforeNavMenu}
        <Search />
        <div className="snow-guide-nav__links">
          {props.beforeRightNavItems}
          <NavList items={items} />
          {props.afterRightNavItems}
        </div>
        {props.afterNavMenu}
        <NoSSR>
          <SwitchAppearance />
        </NoSSR>
        <div className="snow-guide-nav__social">
          <SocialLinks />
        </div>
        <details className="snow-guide-nav__mobile">
          <summary aria-label={lang === 'zh' ? '网站导航' : 'Site navigation'}>
            <SvgWrapper icon={IconSmallMenu} />
          </summary>
          <div className="snow-guide-nav__mobile-links">
            <NavList items={items} />
          </div>
        </details>
      </div>
    </header>
  );
}
