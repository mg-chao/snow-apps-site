import { useLang, useLocation, usePage } from '@rspress/core/runtime';
import { pageBreadcrumbs } from '../seo';
import './SiteNavigation.css';

export function PageBreadcrumbs({
  placement,
}: {
  placement: 'doc' | 'custom' | 'content';
}) {
  const { pathname } = useLocation();
  const { page } = usePage();
  const locale = useLang() === 'zh' ? 'zh' : 'en';
  if (
    page.pageType === 'home' ||
    page.pageType === '404' ||
    page.pageType === 'blank'
  )
    return null;

  const pagePlacement =
    page.pageType === 'custom'
      ? page.frontmatter.breadcrumbPlacement === 'content'
        ? 'content'
        : 'custom'
      : 'doc';
  if (placement !== pagePlacement) return null;

  const items = pageBreadcrumbs(pathname, locale, page.title);
  if (items.length < 2) return null;
  return (
    <nav
      className={`snow-breadcrumbs snow-breadcrumbs--${placement}`}
      aria-label={locale === 'zh' ? '面包屑导航' : 'Breadcrumb'}
    >
      <ol>
        {items.map((item, index) => (
          <li key={item.href}>
            {index === items.length - 1 ? (
              <span aria-current="page">{item.label}</span>
            ) : (
              <a href={item.href}>{item.label}</a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
