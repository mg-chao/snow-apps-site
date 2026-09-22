import {
  type ComponentType,
  type SVGProps,
  useLayoutEffect,
  useRef,
} from 'react';
import { type DownloadPlatform as PreviewOs, usePreviewOs } from '../../platform';
import {
  ApplicationTitleBarIcon,
  DownIcon,
  HistoryIcon,
  InfoCircleIcon,
  KeyboardIcon,
  MenuFoldIcon,
  OcrTranslateIcon,
  PinToScreenIcon,
  RecognizeTextIcon,
  ReloadIcon,
  ScreenshotCopyIcon,
  ScreenshotDelayIcon,
  ScreenshotFeatureIcon,
  ScreenshotFocusedWindowIcon,
  ScreenshotFullScreenIcon,
  SearchIcon,
  SettingIcon,
  SnowShotLogo,
  ThunderboltIcon,
  WheelMouseIcon,
} from './icons';
import './HeroAppPreview.css';

type IconComponent = ComponentType<SVGProps<SVGSVGElement>>;

type Copy = {
  label: string;
  search: string;
  tabs: [string, string, string, string];
  nav: {
    hotkeys: string;
    mouse: string;
    history: string;
    settings: string;
    interface: string;
    function: string;
    shortcuts: string;
    storage: string;
    api: string;
    extended: string;
    system: string;
    about: string;
  };
  section: string;
  unset: string;
  rows: Array<{
    title: string;
    shortcut: string | null;
    Icon: IconComponent;
  }>;
};

const en: Copy = {
  label: 'Snow Shot screenshot settings interface',
  search: 'Search settings and functions',
  tabs: ['Screenshot', 'Pin to screen', 'Screen recording', 'Other'],
  nav: {
    hotkeys: 'Global hotkeys',
    mouse: 'Global mouse',
    history: 'Screenshot history',
    settings: 'Settings',
    interface: 'Interface settings',
    function: 'Function settings',
    shortcuts: 'Application shortcuts',
    storage: 'Storage and privacy',
    api: 'API Configuration',
    extended: 'Extended Features Settings',
    system: 'System settings',
    about: 'About',
  },
  section: 'Screenshot',
  unset: 'Unset',
  rows: [
    { title: 'Screenshot', shortcut: 'F1', Icon: ScreenshotFeatureIcon },
    {
      title: 'Delay 3s to execute',
      shortcut: null,
      Icon: ScreenshotDelayIcon,
    },
    { title: 'Pin to screen', shortcut: null, Icon: PinToScreenIcon },
    { title: 'Text recognition', shortcut: null, Icon: RecognizeTextIcon },
    { title: 'Text translation', shortcut: null, Icon: OcrTranslateIcon },
    {
      title: 'Copy to clipboard',
      shortcut: 'Ctrl+F1',
      Icon: ScreenshotCopyIcon,
    },
    {
      title: 'Current monitor',
      shortcut: null,
      Icon: ScreenshotFullScreenIcon,
    },
    {
      title: 'Focused window',
      shortcut: null,
      Icon: ScreenshotFocusedWindowIcon,
    },
  ],
};

const zh: Copy = {
  label: 'Snow Shot 截图设置界面',
  search: '搜索设置和功能',
  tabs: ['截图', '固定到屏幕', '屏幕录制', '其它'],
  nav: {
    hotkeys: '全局快捷键',
    mouse: '全局鼠标',
    history: '截图历史',
    settings: '设置',
    interface: '界面设置',
    function: '功能设置',
    shortcuts: '应用快捷键',
    storage: '存储与隐私',
    api: 'API 配置',
    extended: '扩展功能设置',
    system: '系统设置',
    about: '关于',
  },
  section: '截图',
  unset: '未设置',
  rows: [
    { title: '截图', shortcut: 'F1', Icon: ScreenshotFeatureIcon },
    { title: '延时 3 秒执行', shortcut: null, Icon: ScreenshotDelayIcon },
    { title: '固定到屏幕', shortcut: null, Icon: PinToScreenIcon },
    { title: '文本识别', shortcut: null, Icon: RecognizeTextIcon },
    { title: '文本翻译', shortcut: null, Icon: OcrTranslateIcon },
    { title: '复制到剪贴板', shortcut: 'Ctrl+F1', Icon: ScreenshotCopyIcon },
    { title: '当前显示器', shortcut: null, Icon: ScreenshotFullScreenIcon },
    { title: '焦点窗口', shortcut: null, Icon: ScreenshotFocusedWindowIcon },
  ],
};

const PREVIEW_WIDTH = 1372;

export function HeroAppPreview({
  isDark,
  isZh,
}: {
  isDark: boolean;
  isZh: boolean;
}) {
  const t = isZh ? zh : en;
  const rootRef = useRef<HTMLDivElement>(null);
  const os = usePreviewOs();

  useLayoutEffect(() => {
    const root = rootRef.current;
    const win = root?.querySelector<HTMLElement>('.snow-app-window');
    if (!root || !win) {
      return undefined;
    }

    const applyScale = () => {
      win.style.transform = `scale(${root.clientWidth / PREVIEW_WIDTH})`;
    };

    applyScale();
    const observer = new ResizeObserver(applyScale);
    observer.observe(root);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      aria-label={t.label}
      className={
        isDark ? 'snow-app-preview snow-app-preview--dark' : 'snow-app-preview'
      }
      ref={rootRef}
      role="img"
    >
      <div aria-hidden="true" className="snow-app-window">
        <TitleBar os={os} />
        <div className="snow-app-body">
          <aside className="snow-app-sidebar">
            <div className="snow-app-menu">
              <NavItem Icon={ThunderboltIcon} active label={t.nav.hotkeys} />
              <NavItem Icon={WheelMouseIcon} label={t.nav.mouse} />
              <NavItem Icon={HistoryIcon} label={t.nav.history} />
              <NavItem Icon={SettingIcon} expanded label={t.nav.settings} />
              <div className="snow-app-submenu">
                <div className="snow-app-subitem">{t.nav.interface}</div>
                <div className="snow-app-subitem">{t.nav.function}</div>
                <div className="snow-app-subitem">{t.nav.shortcuts}</div>
                <div className="snow-app-subitem">{t.nav.storage}</div>
                <div className="snow-app-subitem">{t.nav.api}</div>
                <div className="snow-app-subitem">{t.nav.extended}</div>
                <div className="snow-app-subitem">{t.nav.system}</div>
              </div>
              <NavItem Icon={InfoCircleIcon} label={t.nav.about} />
            </div>
            <div className="snow-app-collapse">
              <MenuFoldIcon />
            </div>
          </aside>
          <div className="snow-app-main">
            <div className="snow-app-header">
              <div className="snow-app-search">
                <SearchIcon className="snow-app-search__prefix" />
                <span className="snow-app-search__placeholder">{t.search}</span>
                <DownIcon className="snow-app-search__suffix" />
              </div>
              <div className="snow-app-tabs">
                {t.tabs.map((tab, index) => (
                  <span
                    className={
                      index === 0
                        ? 'snow-app-tab snow-app-tab--active'
                        : 'snow-app-tab'
                    }
                    key={tab}
                  >
                    {tab}
                  </span>
                ))}
              </div>
            </div>
            <div className="snow-app-content">
              <div className="snow-app-card">
                <div className="snow-app-card__header">
                  <div className="snow-app-card__title">{t.section}</div>
                  <span className="snow-app-reset">
                    <ReloadIcon />
                  </span>
                </div>
                <div className="snow-app-card__body">
                  {t.rows.map((row) => (
                    <div className="snow-app-row" key={row.title}>
                      <div className="snow-app-row__label">
                        <span>{row.title}</span>
                        <row.Icon className="snow-app-row__icon" />
                      </div>
                      <span
                        className={
                          row.shortcut
                            ? 'snow-app-hotkey snow-app-hotkey--set'
                            : 'snow-app-hotkey'
                        }
                      >
                        <KeyboardIcon />
                        {row.shortcut ?? t.unset}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TitleBar({ os }: { os: PreviewOs }) {
  return (
    <div className={`snow-app-titlebar snow-app-titlebar--${os}`}>
      {os === 'macos' ? (
        <div className="snow-app-traffic">
          <span className="snow-app-traffic__btn snow-app-traffic__btn--close" />
          <span className="snow-app-traffic__btn snow-app-traffic__btn--min" />
          <span className="snow-app-traffic__btn snow-app-traffic__btn--zoom" />
        </div>
      ) : (
        <ApplicationTitleBarIcon className="snow-app-sys-icon" />
      )}
      <SnowShotLogo className="snow-app-logo" />
      {os === 'windows' ? (
        <div className="snow-app-caption">
          <span className="snow-app-caption__btn">
            <CaptionMinimizeIcon />
          </span>
          <span className="snow-app-caption__btn">
            <CaptionMaximizeIcon />
          </span>
          <span className="snow-app-caption__btn snow-app-caption__btn--close">
            <CaptionCloseIcon />
          </span>
        </div>
      ) : null}
    </div>
  );
}

function CaptionMinimizeIcon() {
  return (
    <svg aria-hidden="true" fill="currentColor" viewBox="0 0 10 10">
      <rect height="1.5" width="10" x="0" y="4.25" />
    </svg>
  );
}

function CaptionMaximizeIcon() {
  return (
    <svg aria-hidden="true" fill="none" viewBox="0 0 10 10">
      <rect
        height="8.5"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
        width="8.5"
        x="0.75"
        y="0.75"
      />
    </svg>
  );
}

function CaptionCloseIcon() {
  return (
    <svg aria-hidden="true" fill="none" viewBox="0 0 10 10">
      <path
        d="M1 1l8 8M9 1L1 9"
        stroke="currentColor"
        strokeLinecap="square"
        strokeWidth="1.5"
      />
    </svg>
  );
}

function NavItem({
  Icon,
  label,
  active,
  expanded,
}: {
  Icon: IconComponent;
  label: string;
  active?: boolean;
  expanded?: boolean;
}) {
  return (
    <div
      className={
        active
          ? 'snow-app-nav-item snow-app-nav-item--active'
          : 'snow-app-nav-item'
      }
    >
      <Icon className="snow-app-nav-item__icon" />
      <span className="snow-app-nav-item__label">{label}</span>
      {expanded ? (
        <DownIcon className="snow-app-nav-item__chevron snow-app-nav-item__chevron--open" />
      ) : null}
    </div>
  );
}
