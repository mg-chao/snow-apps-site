import { ThemeContext, useLang } from '@rspress/core/runtime';
import { IconMoon, IconSun, SvgWrapper } from '@rspress/core/theme-original';
import { useContext } from 'react';

export function SwitchAppearance({ onClick }: { onClick?: () => void }) {
  const { theme, setTheme } = useContext(ThemeContext);
  const isDark = theme === 'dark';
  const isZh = useLang().startsWith('zh');
  const title = isZh
    ? isDark
      ? '切换到浅色模式'
      : '切换到深色模式'
    : isDark
      ? 'Switch to light mode'
      : 'Switch to dark mode';

  return (
    <button
      aria-checked={isDark}
      aria-label={isZh ? '深色模式' : 'Dark mode'}
      className="snow-theme-switch"
      onClick={() => {
        setTheme?.(isDark ? 'light' : 'dark');
        onClick?.();
      }}
      role="switch"
      title={title}
      type="button"
    >
      <span aria-hidden="true">
        <SvgWrapper className="snow-theme-switch__sun" icon={IconSun} />
        <SvgWrapper className="snow-theme-switch__moon" icon={IconMoon} />
      </span>
    </button>
  );
}
