import { NoSSR, useLang, useLocation, useNav } from '@rspress/core/runtime';
import {
  IconSmallMenu,
  type NavProps,
  NavList,
  NavTitle,
  Search,
  SocialLinks,
  SvgWrapper,
} from '@rspress/core/theme-original';
import { useEffect, useRef } from 'react';
import { SiteLanguageSwitch } from './SiteLanguageSwitch';
import { SwitchAppearance } from './SwitchAppearance';
import './SiteHeader.css';

/** Every page shares navigation, with language and appearance always accessible. */
export function SiteHeader(props: NavProps) {
  const { pathname } = useLocation();
  const items = useNav();
  const lang = useLang();
  const mobileMenu = useRef<HTMLDetailsElement>(null);
  const label = lang === 'zh' ? '网站导航' : 'Site navigation';

  useEffect(() => {
    const closeOutside = (event: PointerEvent) => {
      if (
        event.target instanceof Node &&
        !mobileMenu.current?.contains(event.target)
      ) {
        mobileMenu.current?.removeAttribute('open');
      }
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape' || !mobileMenu.current?.open) return;
      mobileMenu.current.removeAttribute('open');
      mobileMenu.current.querySelector('summary')?.focus();
    };
    const closeOnClick = (event: MouseEvent) => {
      if (
        event.target instanceof Element &&
        mobileMenu.current &&
        (!mobileMenu.current.contains(event.target) ||
          event.target.closest('a'))
      ) {
        mobileMenu.current.removeAttribute('open');
      }
    };
    document.addEventListener('pointerdown', closeOutside);
    document.addEventListener('keydown', closeOnEscape);
    document.addEventListener('click', closeOnClick);
    return () => {
      document.removeEventListener('pointerdown', closeOutside);
      document.removeEventListener('keydown', closeOnEscape);
      document.removeEventListener('click', closeOnClick);
    };
  }, []);

  return (
    <header className="rp-nav snow-site-header">
      <div className="rp-nav__left">
        {props.beforeNavTitle}
        {props.navTitle ?? <NavTitle />}
        <div className="snow-site-header__links">
          {props.beforeLeftNavItems}
          <NavList items={items.filter((item) => item.position === 'left')} />
          {props.afterLeftNavItems}
        </div>
        {props.afterNavTitle}
      </div>
      <div className="rp-nav__right">
        {props.beforeNavMenu}
        <Search />
        <nav className="snow-site-header__links" aria-label={label}>
          {props.beforeRightNavItems}
          <NavList items={items.filter((item) => item.position !== 'left')} />
          {props.afterRightNavItems}
        </nav>
        <SiteLanguageSwitch />
        {props.afterNavMenu}
        <div className="snow-site-header__appearance">
          <NoSSR>
            <SwitchAppearance />
          </NoSSR>
        </div>
        <div className="snow-site-header__social">
          <SocialLinks />
        </div>
        <details
          className="snow-site-header__mobile"
          ref={mobileMenu}
          key={pathname}
        >
          <summary aria-label={label}>
            <SvgWrapper icon={IconSmallMenu} />
          </summary>
          <nav className="snow-site-header__mobile-links" aria-label={label}>
            {props.beforeLeftNavItems}
            {props.afterLeftNavItems}
            {props.beforeRightNavItems}
            <NavList items={items} />
            {props.afterRightNavItems}
          </nav>
        </details>
      </div>
    </header>
  );
}
