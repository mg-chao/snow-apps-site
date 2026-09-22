import { IconArrowDown } from '@rspress/core/theme-original';
import { useState } from 'react';
import { MacInstallOption } from './MacInstallOption';
import {
  type DownloadPlatform,
  useResolvedDownloadPlatform,
} from '../../platform';

type Locale = 'en' | 'zh';
type CardTone = 'online' | 'offline' | 'portable';
type ButtonTone = 'dark' | 'light';

type DownloadCard = {
  tone: CardTone;
  number: string;
  tag: string;
  title: string;
  body: string;
  points: readonly [string, string, string];
  href: string;
  fileName: string;
  button: string;
  buttonTone: ButtonTone;
};

type PlatformCopy = {
  kicker: string;
  title: readonly [string, string];
  intro: string;
  meta: readonly [string, string];
  sectionKicker: string;
  sectionTitle: readonly [string, string];
  cards: readonly DownloadCard[];
  noteKicker: string;
  noteTitle: readonly [string, string];
  noteBody: string;
};

const windowsOnline = '/setup/snow-shot_windows-x64-online.exe';
const windowsOffline = '/setup/snow-shot_windows-x64-offline.exe';
const windowsPortable = '/setup/snow-shot_windows-x64-portable.zip';
const macosDmg = '/setup/snow-shot_macos-arm64.dmg';

const copy = {
  en: {
    selectLabel: 'System',
    windowsOption: 'Windows x64',
    macosOption: 'macOS ARM64',
    windows: {
      kicker: 'SNOW SHOT / WINDOWS',
      title: ['Make your screen', 'worth sharing.'],
      intro:
        'A fast, focused toolkit for screenshots, recordings, annotations, and text recognition.',
      meta: ['Free to download', 'Ready in minutes'],
      sectionKicker: 'CHOOSE YOUR SETUP',
      sectionTitle: ['Three downloads.', 'Choose your version.'],
      cards: [
        {
          tone: 'online',
          number: '01',
          tag: 'INSTALL AS NEEDED',
          title: 'Online installer',
          body: 'Start with the base package. Some features are installed when you use them for the first time.',
          points: [
            'Small initial download',
            'Features install on first use',
            'Get features as needed',
          ],
          href: windowsOnline,
          fileName: 'snow-shot_windows-x64-online.exe',
          button: 'Download online installer',
          buttonTone: 'dark',
        },
        {
          tone: 'offline',
          number: '02',
          tag: 'ALL FEATURES INCLUDED',
          title: 'Offline installer',
          body: 'The package includes every software feature for installation and use in an offline environment.',
          points: [
            'Every feature included',
            'Ready for offline environments',
            'Install once, use anywhere',
          ],
          href: windowsOffline,
          fileName: 'snow-shot_windows-x64-offline.exe',
          button: 'Download offline installer',
          buttonTone: 'light',
        },
        {
          tone: 'portable',
          number: '03',
          tag: 'PORTABLE',
          title: 'Portable version',
          body: 'Run Snow Shot directly without installation or system changes.',
          points: [
            'No installation required',
            'Keep it on a USB drive',
            'Use it on any Windows x64 PC',
          ],
          href: windowsPortable,
          fileName: 'snow-shot_windows-x64-portable.zip',
          button: 'Download portable version',
          buttonTone: 'dark',
        },
      ],
      noteKicker: 'NOT SURE WHICH ONE?',
      noteTitle: ['Pick online for speed.', 'Pick offline for certainty.'],
      noteBody:
        'All three downloads deliver the same Snow Shot experience. Your choice only changes how Snow Shot is installed or launched on your computer.',
    },
    macos: {
      kicker: 'SNOW SHOT / MACOS',
      title: ['Make your screen', 'worth sharing.'],
      intro:
        'A fast, focused toolkit for screenshots, recordings, annotations, and text recognition.',
      meta: ['Free to download', 'Ready in minutes'],
      sectionKicker: 'CHOOSE YOUR SETUP',
      sectionTitle: ['Install from Terminal.', 'Or download the disk image.'],
      cards: [
        {
          tone: 'online',
          number: 'DMG',
          tag: 'APPLE SILICON',
          title: 'Disk image',
          body: 'Install Snow Shot on Apple silicon Macs from a standard disk image.',
          points: [
            'Built for macOS ARM64',
            'Drag Snow Shot into Applications',
            'Open it and start capturing',
          ],
          href: macosDmg,
          fileName: 'snow-shot_macos-arm64.dmg',
          button: 'Download for macOS',
          buttonTone: 'dark',
        },
      ],
      noteKicker: 'INSTALL ON A MAC',
      noteTitle: ['Open the image.', 'Drag Snow Shot in.'],
      noteBody:
        'This disk image is for Apple silicon Macs. Open it, drag Snow Shot into Applications, then launch it from there.',
    },
  },
  zh: {
    selectLabel: '系统',
    windowsOption: 'Windows x64',
    macosOption: 'macOS ARM64',
    windows: {
      kicker: 'SNOW SHOT / WINDOWS',
      title: ['让每一处画面', '都值得分享。'],
      intro: '截图、录屏、标注和文字识别，一套专注而快速的工具。',
      meta: ['免费下载', '几分钟即可开始'],
      sectionKicker: '选择安装方式',
      sectionTitle: ['三种下载方式。', '选择适合你的版本。'],
      cards: [
        {
          tone: 'online',
          number: '01',
          tag: '按需安装',
          title: '在线安装包',
          body: '先下载基础包，部分功能会在首次使用时完成安装。',
          points: [
            '初始下载体积更小',
            '使用功能时自动完成安装',
            '按需获取功能',
          ],
          href: windowsOnline,
          fileName: 'snow-shot_windows-x64-online.exe',
          button: '下载在线安装包',
          buttonTone: 'dark',
        },
        {
          tone: 'offline',
          number: '02',
          tag: '完整功能',
          title: '离线安装包',
          body: '安装包包含软件的全部功能，可在离线环境中安装和使用。',
          points: ['包含全部功能', '适合离线环境', '安装一次，随时使用'],
          href: windowsOffline,
          fileName: 'snow-shot_windows-x64-offline.exe',
          button: '下载离线安装包',
          buttonTone: 'light',
        },
        {
          tone: 'portable',
          number: '03',
          tag: '便携版本',
          title: '便携版',
          body: '无需安装或修改系统设置，直接运行 Snow Shot。',
          points: [
            '无需安装即可使用',
            '可保存到 U 盘随身携带',
            '适用于任意 Windows x64 电脑',
          ],
          href: windowsPortable,
          fileName: 'snow-shot_windows-x64-portable.zip',
          button: '下载便携版',
          buttonTone: 'dark',
        },
      ],
      noteKicker: '还在犹豫？',
      noteTitle: ['想要更快，就选在线。', '想要安心，就选离线。'],
      noteBody:
        '三种下载方式提供完全相同的 Snow Shot 体验，区别只在于 Snow Shot 如何安装或启动。',
    },
    macos: {
      kicker: 'SNOW SHOT / MACOS',
      title: ['让每一处画面', '都值得分享。'],
      intro: '截图、录屏、标注和文字识别，一套专注而快速的工具。',
      meta: ['免费下载', '几分钟即可开始'],
      sectionKicker: '选择安装方式',
      sectionTitle: ['通过终端安装。', '也可下载磁盘映像。'],
      cards: [
        {
          tone: 'online',
          number: 'DMG',
          tag: 'Apple 芯片',
          title: '磁盘映像',
          body: '适用于 Apple 芯片的 macOS，通过磁盘映像安装。',
          points: [
            '适用于 macOS ARM64',
            '拖入应用程序文件夹',
            '打开即可开始使用',
          ],
          href: macosDmg,
          fileName: 'snow-shot_macos-arm64.dmg',
          button: '下载 macOS 版',
          buttonTone: 'dark',
        },
      ],
      noteKicker: '在 Mac 上安装',
      noteTitle: ['打开映像，拖入应用。', '从应用程序启动。'],
      noteBody:
        '这个磁盘映像适用于 Apple 芯片的 Mac。打开后把 Snow Shot 拖进应用程序文件夹，再从那里启动。',
    },
  },
} as const satisfies Record<
  Locale,
  {
    selectLabel: string;
    windowsOption: string;
    macosOption: string;
    windows: PlatformCopy;
    macos: PlatformCopy;
  }
>;

function SystemSelect({
  label,
  windowsOption,
  macosOption,
  value,
  onChange,
}: {
  label: string;
  windowsOption: string;
  macosOption: string;
  value: DownloadPlatform;
  onChange: (next: DownloadPlatform) => void;
}) {
  return (
    <div className="snow-os-select">
      <label htmlFor="snow-download-platform">{label}</label>
      <div className="snow-os-select__field">
        <select
          id="snow-download-platform"
          value={value}
          onChange={(event) => {
            onChange(event.target.value === 'macos' ? 'macos' : 'windows');
          }}
        >
          <option value="windows">{windowsOption}</option>
          <option value="macos">{macosOption}</option>
        </select>
      </div>
    </div>
  );
}

function rememberPlatform(next: DownloadPlatform) {
  const url = new URL(window.location.href);
  url.searchParams.set('os', next);
  window.history.replaceState(
    null,
    '',
    `${url.pathname}${url.search}${url.hash}`,
  );
}

export function DownloadPage({ locale }: { locale: Locale }) {
  const resolved = useResolvedDownloadPlatform();
  const [override, setOverride] = useState<DownloadPlatform | null>(null);
  const platform = override ?? resolved;
  const page = copy[locale];
  const content = page[platform];

  return (
    <main className="snow-download-page">
      <section className="snow-download-hero">
        <div className="snow-download-hero__copy">
          <p className="snow-download-kicker">{content.kicker}</p>
          <h1>
            {content.title[0]}
            <br />
            <em>{content.title[1]}</em>
          </h1>
          <p className="snow-download-hero__intro">{content.intro}</p>
          <SystemSelect
            label={page.selectLabel}
            macosOption={page.macosOption}
            value={platform}
            windowsOption={page.windowsOption}
            onChange={(next) => {
              setOverride(next);
              rememberPlatform(next);
            }}
          />
          <div className="snow-download-hero__meta">
            {content.meta.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>
        <div className="snow-download-hero__badge" aria-hidden="true">
          <img alt="" src="/app-icon.svg" />
          <span>SS</span>
        </div>
      </section>
      <section
        className="snow-download-options"
        aria-labelledby="download-options-title"
      >
        <div className="snow-download-section-head">
          <p className="snow-download-kicker">{content.sectionKicker}</p>
          <h2 id="download-options-title">
            {content.sectionTitle[0]}
            <br />
            {content.sectionTitle[1]}
          </h2>
        </div>
        {platform === 'macos' && (
          <MacInstallOption key={locale} locale={locale} />
        )}
        <div
          className={
            content.cards.length === 1
              ? 'snow-download-grid snow-download-grid--single'
              : 'snow-download-grid'
          }
        >
          {content.cards.map((card) => (
            <article
              className={`snow-download-card snow-download-card--${card.tone}`}
              key={card.fileName}
            >
              <div className="snow-download-card__top">
                <span className="snow-download-card__number">
                  {card.number}
                </span>
                <span className="snow-download-tag">{card.tag}</span>
              </div>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
              <ul>
                {card.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
              <a
                className={`snow-download-button snow-download-button--${card.buttonTone}`}
                download={card.fileName}
                href={card.href}
              >
                <IconArrowDown />
                {card.button}
              </a>
              <p className="snow-download-file">{card.fileName}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="snow-download-note">
        <div className="snow-download-note__mark">?</div>
        <div>
          <p className="snow-download-kicker">{content.noteKicker}</p>
          <h2>
            {content.noteTitle[0]}
            <br />
            {content.noteTitle[1]}
          </h2>
        </div>
        <p className="snow-download-note__body">{content.noteBody}</p>
      </section>
    </main>
  );
}
