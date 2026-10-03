import { IconArrowDown } from '@rspress/core/theme-original';
import { useState } from 'react';
import {
  type DownloadPlatform,
  useResolvedDownloadPlatform,
} from '../../platform';
import { MacInstallOption } from './MacInstallOption';
import { MirrorLink } from './MirrorLink';
import {
  type ReleaseAsset,
  releaseAssets,
  releaseDownloadUrl,
} from './releaseLinks';

type Locale = 'en' | 'zh';
type CardTone = 'online' | 'offline' | 'portable' | 'mini';
type ButtonTone = 'dark' | 'light';

type DownloadCard = {
  tone: CardTone;
  number: string;
  tag: string;
  title: string;
  body: string;
  points: readonly [string, string, string];
  asset: ReleaseAsset;
  buttonTone: ButtonTone;
  alternate?: { asset: ReleaseAsset; label: string };
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

const copy = {
  en: {
    selectLabel: 'System',
    downloadButton: 'Download from GitHub',
    windowsOption: 'Windows x64',
    macosOption: 'macOS ARM64',
    windows: {
      kicker: 'SNOW SHOT / WINDOWS',
      title: ['Make your screen', 'worth sharing.'],
      intro:
        'A fast, focused toolkit for screenshots, recordings, annotations, and text recognition.',
      meta: ['Free to download', 'Ready in minutes'],
      sectionKicker: 'CHOOSE YOUR SETUP',
      sectionTitle: ['Choose your edition.', 'Download your way.'],
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
          asset: 'windowsOnline',
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
          asset: 'windowsOffline',
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
          asset: 'windowsPortable',
          buttonTone: 'dark',
        },
        {
          tone: 'mini',
          number: 'MINI',
          tag: 'LIGHTER EDITION',
          title: 'Snow Shot Mini',
          body: 'A lighter edition for screenshots, annotations, pinning, and recording. Enable manual text recognition in settings when you need it.',
          points: [
            'No QR or table recognition',
            'Text recognition downloads on first use',
            'Online installer or portable archive',
          ],
          asset: 'windowsMiniOnline',
          buttonTone: 'dark',
          alternate: {
            asset: 'windowsMiniPortable',
            label: 'Download Mini portable version',
          },
        },
      ],
      noteKicker: 'NOT SURE WHICH ONE?',
      noteTitle: ['Full toolkit or Mini.', 'Choose what you need.'],
      noteBody:
        'The online installer, offline installer, and portable version provide the full Snow Shot toolkit. Mini keeps the capture essentials and leaves out tools such as QR and table recognition. Mini has no offline installer.',
    },
    macos: {
      kicker: 'SNOW SHOT / MACOS',
      title: ['Make your screen', 'worth sharing.'],
      intro:
        'A fast, focused toolkit for screenshots, recordings, annotations, and text recognition.',
      meta: ['Free to download', 'Ready in minutes'],
      sectionKicker: 'CHOOSE YOUR SETUP',
      sectionTitle: ['Choose your edition.', 'Install on your Mac.'],
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
          asset: 'macosDmg',
          buttonTone: 'dark',
        },
        {
          tone: 'mini',
          number: 'MINI',
          tag: 'LIGHTER EDITION',
          title: 'Snow Shot Mini',
          body: 'A lighter edition for screenshots, annotations, pinning, and recording on Apple silicon Macs.',
          points: [
            'Apple silicon · macOS 15 or later',
            'Text recognition included; enable in settings',
            'No QR or table recognition',
          ],
          asset: 'macosMiniDmg',
          buttonTone: 'dark',
        },
      ],
      noteKicker: 'INSTALL ON A MAC',
      noteTitle: ['Open the image.', 'Drag Snow Shot in.'],
      noteBody:
        'Both editions require macOS 15 or later on Apple silicon. Open your chosen disk image, drag Snow Shot or Snow Shot Mini into Applications, then launch it from there.',
    },
  },
  zh: {
    selectLabel: '系统',
    downloadButton: '从 Gitee 下载',
    windowsOption: 'Windows x64',
    macosOption: 'macOS ARM64',
    windows: {
      kicker: 'SNOW SHOT / WINDOWS',
      title: ['让每一处画面', '都值得分享。'],
      intro: '截图、录屏、标注和文字识别，一套专注而快速的工具。',
      meta: ['免费下载', '几分钟即可开始'],
      sectionKicker: '选择安装方式',
      sectionTitle: ['选择适合你的版本。', '按你的方式下载。'],
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
          asset: 'windowsOnline',
          buttonTone: 'dark',
        },
        {
          tone: 'offline',
          number: '02',
          tag: '完整功能',
          title: '离线安装包',
          body: '安装包包含软件的全部功能，可在离线环境中安装和使用。',
          points: ['包含全部功能', '适合离线环境', '安装一次，随时使用'],
          asset: 'windowsOffline',
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
          asset: 'windowsPortable',
          buttonTone: 'dark',
        },
        {
          tone: 'mini',
          number: 'MINI',
          tag: '轻量版本',
          title: 'Snow Shot Mini',
          body: '专注截图、标注、贴图和录屏的轻量版本。需要手动文字识别时，可在设置中开启。',
          points: [
            '不包含二维码和表格识别',
            '首次使用文字识别时下载组件',
            '提供在线安装包和便携版',
          ],
          asset: 'windowsMiniOnline',
          buttonTone: 'dark',
          alternate: {
            asset: 'windowsMiniPortable',
            label: '下载 Mini 便携版',
          },
        },
      ],
      noteKicker: '还在犹豫？',
      noteTitle: ['完整工具，或轻量 Mini。', '按需选择。'],
      noteBody:
        '在线安装包、离线安装包和便携版均提供完整的 Snow Shot 功能。Mini 保留核心截图功能，不包含二维码、表格识别等工具。Mini 不提供离线安装包。',
    },
    macos: {
      kicker: 'SNOW SHOT / MACOS',
      title: ['让每一处画面', '都值得分享。'],
      intro: '截图、录屏、标注和文字识别，一套专注而快速的工具。',
      meta: ['免费下载', '几分钟即可开始'],
      sectionKicker: '选择安装方式',
      sectionTitle: ['选择适合你的版本。', '安装到你的 Mac。'],
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
          asset: 'macosDmg',
          buttonTone: 'dark',
        },
        {
          tone: 'mini',
          number: 'MINI',
          tag: '轻量版本',
          title: 'Snow Shot Mini',
          body: '适用于 Apple 芯片 Mac，专注截图、标注、贴图和录屏的轻量版本。',
          points: [
            'Apple 芯片 · macOS 15 或更新版本',
            '内置文字识别，可在设置中开启',
            '不包含二维码和表格识别',
          ],
          asset: 'macosMiniDmg',
          buttonTone: 'dark',
        },
      ],
      noteKicker: '在 Mac 上安装',
      noteTitle: ['打开映像，拖入应用。', '从应用程序启动。'],
      noteBody:
        '两个版本均适用于运行 macOS 15 或更新版本的 Apple 芯片 Mac。打开所选磁盘映像，把 Snow Shot 或 Snow Shot Mini 拖进应用程序文件夹，再从那里启动。',
    },
  },
} as const satisfies Record<
  Locale,
  {
    selectLabel: string;
    downloadButton: string;
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
  const content: PlatformCopy = page[platform];

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
        <div id="download-channels">
          <p className="snow-download-hero__intro">
            {locale === 'zh'
              ? '选择安装方式，直接从 Gitee 下载对应安装包。也可通过下方 GitHub 发布页下载。'
              : 'Choose an installation method to download the matching package directly from GitHub. You can also browse the Gitee release below.'}
          </p>
        </div>
        {platform === 'macos' && <MacInstallOption locale={locale} />}
        <div
          className={
            content.cards.length === 1
              ? 'snow-download-grid snow-download-grid--single'
              : content.cards.length === 4
                ? 'snow-download-grid snow-download-grid--paired'
                : 'snow-download-grid'
          }
        >
          {content.cards.map((card) => (
            <article
              className={`snow-download-card snow-download-card--${card.tone}`}
              key={card.asset}
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
              <div className="snow-download-card__actions">
                <a
                  className={`snow-download-button snow-download-button--${card.buttonTone}`}
                  href={releaseDownloadUrl(locale, card.asset)}
                  aria-label={`${page.downloadButton}: ${card.title}`}
                >
                  <IconArrowDown />
                  {page.downloadButton}
                </a>
                {card.alternate && (
                  <a
                    className="snow-download-card__alternate"
                    href={releaseDownloadUrl(locale, card.alternate.asset)}
                  >
                    {card.alternate.label}
                  </a>
                )}
              </div>
              <p className="snow-download-file">{releaseAssets[card.asset]}</p>
            </article>
          ))}
        </div>
        <MirrorLink locale={locale} />
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
