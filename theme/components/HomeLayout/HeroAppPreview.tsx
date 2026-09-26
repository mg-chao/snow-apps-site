import {
  type ComponentType,
  type PointerEvent as ReactPointerEvent,
  type SVGProps,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import {
  type DownloadPlatform as PreviewOs,
  usePreviewOs,
} from '../../platform';
import {
  ApplicationTitleBarIcon,
  DisabledIcon,
  DownIcon,
  HistoryIcon,
  InfoCircleIcon,
  KeyboardIcon,
  MenuFoldIcon,
  OcrTranslateIcon,
  PinClipboardIcon,
  PinToScreenIcon,
  PinToScreenManagementIcon,
  RecognizeTextIcon,
  RecordingFolderIcon,
  RecordScreenIcon,
  ReloadIcon,
  ScreenshotCopyIcon,
  ScreenshotDelayIcon,
  ScreenshotFeatureIcon,
  ScreenshotFocusedWindowIcon,
  ScreenshotFullScreenIcon,
  SearchIcon,
  SelectIcon,
  SettingIcon,
  SnowShotLogo,
  ThunderboltIcon,
  WheelMouseIcon,
} from './icons';
import {
  PreviewSelectionOverlay,
  selectionRectFromClientBoxes,
} from './selectionOverlay';
import './HeroAppPreview.css';

type IconComponent = ComponentType<SVGProps<SVGSVGElement>>;

type Copy = {
  label: string;
  search: string;
  nav: {
    hotkeys: string;
    mouse: string;
    history: string;
    pinned: string;
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
  unset: string;
};

type HotkeyFunction = {
  en: string;
  zh: string;
  windows: string | null;
  macos: string | null;
  Icon: IconComponent;
};

type HotkeySection = {
  id: string;
  en: string;
  zh: string;
  reset: boolean;
  functions: HotkeyFunction[];
};

// Global hotkeys page, in settings-catalog order.
// macOS Meta is the physical Control key, so Meta+1 displays as ⌃1.
const hotkeySections: HotkeySection[] = [
  {
    id: 'screenshot',
    en: 'Screenshot',
    zh: '截图',
    reset: true,
    functions: [
      {
        en: 'Screenshot',
        zh: '截图',
        windows: 'F1',
        macos: '⌃1',
        Icon: ScreenshotFeatureIcon,
      },
      {
        en: 'Delay 3s to execute',
        zh: '延时 3 秒执行',
        windows: null,
        macos: null,
        Icon: ScreenshotDelayIcon,
      },
      {
        en: 'Pin to screen',
        zh: '固定到屏幕',
        windows: null,
        macos: null,
        Icon: PinToScreenIcon,
      },
      {
        en: 'Text recognition',
        zh: '文本识别',
        windows: null,
        macos: null,
        Icon: RecognizeTextIcon,
      },
      {
        en: 'Text translation',
        zh: '文本翻译',
        windows: null,
        macos: null,
        Icon: OcrTranslateIcon,
      },
      {
        en: 'Copy to clipboard',
        zh: '复制到剪贴板',
        windows: 'Ctrl+F1',
        macos: '⌃2',
        Icon: ScreenshotCopyIcon,
      },
      {
        en: 'Current monitor',
        zh: '当前显示器',
        windows: null,
        macos: null,
        Icon: ScreenshotFullScreenIcon,
      },
      {
        en: 'Focused window',
        zh: '焦点窗口',
        windows: null,
        macos: null,
        Icon: ScreenshotFocusedWindowIcon,
      },
    ],
  },
  {
    id: 'pin-to-screen',
    en: 'Pin to screen',
    zh: '固定到屏幕',
    reset: true,
    functions: [
      {
        en: 'Pin clipboard content to screen',
        zh: '将剪贴板内容固定到屏幕',
        windows: 'F3',
        macos: '⌃3',
        Icon: PinClipboardIcon,
      },
      {
        en: 'Pin Selected Files to Screen',
        zh: '将选中文件固定到屏幕',
        windows: null,
        macos: null,
        Icon: SelectIcon,
      },
      {
        en: 'Restore Last Closed Window',
        zh: '恢复上次关闭的窗口',
        windows: 'Ctrl+F3',
        macos: '⌃⇧3',
        Icon: HistoryIcon,
      },
    ],
  },
  {
    id: 'screen-recording',
    en: 'Screen recording',
    zh: '屏幕录制',
    reset: false,
    functions: [
      {
        en: 'Screen recording',
        zh: '屏幕录制',
        windows: null,
        macos: null,
        Icon: RecordScreenIcon,
      },
      {
        en: 'Record/Copy Video',
        zh: '录制/复制视频',
        windows: null,
        macos: null,
        Icon: ScreenshotCopyIcon,
      },
      {
        en: 'Screen recording folder',
        zh: '屏幕录制文件夹',
        windows: null,
        macos: null,
        Icon: RecordingFolderIcon,
      },
    ],
  },
  {
    id: 'other',
    en: 'Other',
    zh: '其它',
    reset: true,
    functions: [
      {
        en: 'Screenshot history',
        zh: '截图历史',
        windows: null,
        macos: null,
        Icon: HistoryIcon,
      },
      {
        en: 'Pin to Screen Management',
        zh: '固定到屏幕管理',
        windows: null,
        macos: null,
        Icon: PinToScreenManagementIcon,
      },
      {
        en: 'Translate Selected Text',
        zh: '翻译选中文本',
        windows: null,
        macos: null,
        Icon: OcrTranslateIcon,
      },
      {
        en: 'Disable/Enable global hotkeys',
        zh: '禁用/启用全局快捷键',
        windows: null,
        macos: null,
        Icon: DisabledIcon,
      },
      {
        en: 'Disable hotkeys in fullscreen windows',
        zh: '在全屏窗口中禁用快捷键',
        windows: null,
        macos: null,
        Icon: ScreenshotFullScreenIcon,
      },
    ],
  },
];

const en: Copy = {
  label: 'Snow Shot screenshot settings interface',
  search: 'Search settings and functions',
  nav: {
    hotkeys: 'Global hotkeys',
    mouse: 'Global mouse',
    history: 'Screenshot history',
    pinned: 'Pin to Screen Management',
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
  unset: 'Unset',
};

const zh: Copy = {
  label: 'Snow Shot 截图设置界面',
  search: '搜索设置和功能',
  nav: {
    hotkeys: '全局快捷键',
    mouse: '全局鼠标',
    history: '截图历史',
    pinned: '固定到屏幕管理',
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
  unset: '未设置',
};

const PREVIEW_WIDTH = 1372;

function captureTarget(node: EventTarget | null): HTMLElement | null {
  if (!(node instanceof Element)) {
    return null;
  }
  const target = node.closest('[data-capture-target]');
  return target instanceof HTMLElement ? target : null;
}

export function HeroAppPreview({
  isDark,
  isZh,
}: {
  isDark: boolean;
  isZh: boolean;
}) {
  const t = isZh ? zh : en;
  const os = usePreviewOs();
  const sections = hotkeySections.map((section) => ({
    id: section.id,
    title: isZh ? section.zh : section.en,
    reset: section.reset,
    rows: section.functions.map((row) => ({
      title: isZh ? row.zh : row.en,
      shortcut: os === 'macos' ? row.macos : row.windows,
      Icon: row.Icon,
    })),
  }));
  const [activeSection, setActiveSection] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayRef = useRef<PreviewSelectionOverlay | null>(null);

  const showSection = (index: number) => {
    const body = bodyRef.current;
    const section = body?.querySelector<HTMLElement>(
      `[data-hotkey-section="${hotkeySections[index]?.id}"]`,
    );
    if (!body || !section) {
      return;
    }
    body.scrollTo({
      top: section.offsetTop - body.offsetTop,
    });
    setActiveSection(index);
  };

  const syncActiveSection = () => {
    const body = bodyRef.current;
    if (!body) {
      return;
    }
    const atEnd = body.scrollTop >= body.scrollHeight - body.clientHeight - 1;
    let next = atEnd ? hotkeySections.length - 1 : 0;
    if (!atEnd) {
      for (const section of body.querySelectorAll<HTMLElement>(
        '[data-hotkey-section]',
      )) {
        if (section.offsetTop - body.offsetTop <= body.scrollTop + 8) {
          const index = hotkeySections.findIndex(
            (item) => item.id === section.dataset.hotkeySection,
          );
          if (index >= 0) {
            next = index;
          }
        }
      }
    }
    setActiveSection((current) => (current === next ? current : next));
  };

  useLayoutEffect(() => {
    const root = rootRef.current;
    const win = root?.querySelector<HTMLElement>('.snow-app-window');
    const canvas = canvasRef.current;
    if (!root || !win || !canvas) {
      return undefined;
    }

    const applyScale = () => {
      win.style.transform = `scale(${root.clientWidth / PREVIEW_WIDTH})`;
    };

    applyScale();
    const overlay = new PreviewSelectionOverlay(canvas, win);
    overlayRef.current = overlay;
    overlay.setUnit(os === 'macos' ? 'dp' : 'px');

    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const applyMotion = () => overlay.setReducedMotion(motion.matches);
    applyMotion();
    motion.addEventListener('change', applyMotion);

    const observer = new ResizeObserver(() => {
      applyScale();
      overlay.render();
    });
    observer.observe(root);
    return () => {
      motion.removeEventListener('change', applyMotion);
      observer.disconnect();
      overlay.dispose();
      overlayRef.current = null;
    };
  }, [os]);

  const showCapture = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.pointerType !== 'mouse') {
      return;
    }
    const target = captureTarget(event.target);
    if (!target) {
      return;
    }
    const selection = selectionRectFromClientBoxes(
      event.currentTarget.getBoundingClientRect(),
      event.currentTarget.offsetWidth,
      target.getBoundingClientRect(),
    );
    if (!selection) {
      return;
    }
    overlayRef.current?.moveTo(selection);
    event.currentTarget.classList.add('snow-app-window--capturing');
  };

  const hideCapture = (event: ReactPointerEvent<HTMLDivElement>) => {
    overlayRef.current?.dismiss();
    event.currentTarget.classList.remove('snow-app-window--capturing');
  };

  return (
    <div
      aria-label={t.label}
      className={
        isDark ? 'snow-app-preview snow-app-preview--dark' : 'snow-app-preview'
      }
      ref={rootRef}
      role="img"
    >
      <div
        aria-hidden="true"
        className="snow-app-window"
        onPointerCancel={hideCapture}
        onPointerEnter={showCapture}
        onPointerLeave={hideCapture}
        onPointerMove={showCapture}
      >
        <TitleBar os={os} />
        <div className="snow-app-body">
          <aside className="snow-app-sidebar" data-capture-target="">
            <div className="snow-app-menu">
              <NavItem Icon={ThunderboltIcon} active label={t.nav.hotkeys} />
              <NavItem Icon={WheelMouseIcon} label={t.nav.mouse} />
              <NavItem Icon={HistoryIcon} label={t.nav.history} />
              <NavItem Icon={PinToScreenManagementIcon} label={t.nav.pinned} />
              <NavItem Icon={SettingIcon} expanded label={t.nav.settings} />
              <div className="snow-app-submenu">
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.interface}
                </div>
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.function}
                </div>
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.shortcuts}
                </div>
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.storage}
                </div>
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.api}
                </div>
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.extended}
                </div>
                <div className="snow-app-subitem" data-capture-target="">
                  {t.nav.system}
                </div>
              </div>
              <NavItem Icon={InfoCircleIcon} label={t.nav.about} />
            </div>
            <div className="snow-app-collapse" data-capture-target="">
              <MenuFoldIcon />
            </div>
          </aside>
          <div className="snow-app-main">
            <div className="snow-app-header" data-capture-target="">
              <div className="snow-app-search" data-capture-target="">
                <SearchIcon className="snow-app-search__prefix" />
                <span className="snow-app-search__placeholder">{t.search}</span>
                <DownIcon className="snow-app-search__suffix" />
              </div>
              <div className="snow-app-tabs">
                {sections.map((section, index) => (
                  <button
                    className={
                      index === activeSection
                        ? 'snow-app-tab snow-app-tab--active'
                        : 'snow-app-tab'
                    }
                    data-capture-target=""
                    key={section.id}
                    onClick={() => showSection(index)}
                    type="button"
                  >
                    {section.title}
                  </button>
                ))}
              </div>
            </div>
            <div className="snow-app-content" data-capture-target="">
              <div className="snow-app-card" data-capture-target="">
                <div
                  className="snow-app-card__body"
                  onScroll={syncActiveSection}
                  ref={bodyRef}
                >
                  {sections.map((section) => (
                    <section
                      className="snow-app-section"
                      data-capture-target=""
                      data-hotkey-section={section.id}
                      key={section.id}
                    >
                      <div
                        className="snow-app-card__header"
                        data-capture-target=""
                      >
                        <div className="snow-app-card__title">
                          {section.title}
                        </div>
                        {section.reset ? (
                          <span
                            className="snow-app-reset"
                            data-capture-target=""
                          >
                            <ReloadIcon />
                          </span>
                        ) : null}
                      </div>
                      <div className="snow-app-section__rows">
                        {section.rows.map((row) => (
                          <div
                            className="snow-app-row"
                            data-capture-target=""
                            key={row.title}
                          >
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
                              data-capture-target=""
                            >
                              <KeyboardIcon />
                              {row.shortcut ?? t.unset}
                            </span>
                          </div>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
        <canvas className="snow-capture" ref={canvasRef} />
      </div>
    </div>
  );
}

function TitleBar({ os }: { os: PreviewOs }) {
  return (
    <div
      className={`snow-app-titlebar snow-app-titlebar--${os}`}
      data-capture-target=""
    >
      {os === 'macos' ? (
        <div className="snow-app-traffic">
          <span
            className="snow-app-traffic__btn snow-app-traffic__btn--close"
            data-capture-target=""
          />
          <span
            className="snow-app-traffic__btn snow-app-traffic__btn--min"
            data-capture-target=""
          />
          <span
            className="snow-app-traffic__btn snow-app-traffic__btn--zoom"
            data-capture-target=""
          />
        </div>
      ) : (
        <ApplicationTitleBarIcon
          className="snow-app-sys-icon"
          data-capture-target=""
        />
      )}
      <SnowShotLogo className="snow-app-logo" data-capture-target="" />
      {os === 'windows' ? (
        <div className="snow-app-caption">
          <span className="snow-app-caption__btn" data-capture-target="">
            <CaptionMinimizeIcon />
          </span>
          <span className="snow-app-caption__btn" data-capture-target="">
            <CaptionMaximizeIcon />
          </span>
          <span
            className="snow-app-caption__btn snow-app-caption__btn--close"
            data-capture-target=""
          >
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

function SubmenuChevron() {
  return (
    <svg
      aria-hidden="true"
      className="snow-app-nav-item__chevron"
      fill="none"
      viewBox="0 0 12 14"
    >
      <path
        d="M3 8L6 5L9 8"
        stroke="currentColor"
        strokeLinejoin="bevel"
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
      data-capture-target=""
    >
      <Icon className="snow-app-nav-item__icon" />
      <span className="snow-app-nav-item__label">{label}</span>
      {expanded ? <SubmenuChevron /> : null}
    </div>
  );
}
