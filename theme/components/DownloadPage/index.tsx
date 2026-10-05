import { IconArrowDown } from '@rspress/core/theme-original';
import { useState } from 'react';
import {
  type DownloadArchitecture,
  type DownloadPlatform,
  type DownloadTarget,
  useResolvedDownloadTarget,
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
    windowsX64Option: 'Windows x64',
    windowsArm64Option: 'Windows ARM64',
    macosArm64Option: 'macOS ARM64 (Apple)',
    macosX64Option: 'macOS x64 (Intel)',
    architectureHint:
      'Check your chip before downloading: Windows Settings → System → About, or Apple menu → About This Mac. Choose the matching system above if detection is unavailable.',
    intelTag: 'INTEL MAC',
    macosX64SectionTitle: ['Download Snow Shot.', 'Install on your Mac.'],
    macosX64Note:
      'Snow Shot requires macOS 15 or later on an Intel Mac. Open the disk image, drag Snow Shot into Applications, then launch it from there. Snow Shot Mini is available only for Apple silicon Macs.',
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
            'Use it on a PC with the matching chip',
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
          body: 'Install Snow Shot on your Mac from a standard disk image.',
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
    windowsX64Option: 'Windows x64',
    windowsArm64Option: 'Windows ARM64',
    macosArm64Option: 'macOS ARM64（Apple 芯片）',
    macosX64Option: 'macOS x64（Intel）',
    architectureHint:
      '下载前请确认芯片：Windows「设置 → 系统 → 系统信息」，或 Apple 菜单「关于本机」。无法自动识别时，请在上方选择匹配的系统。',
    intelTag: 'Intel 芯片',
    macosX64SectionTitle: ['下载 Snow Shot。', '安装到你的 Mac。'],
    macosX64Note:
      'Snow Shot 适用于运行 macOS 15 或更新版本的 Intel Mac。打开磁盘映像，把 Snow Shot 拖进应用程序文件夹，再从那里启动。Snow Shot Mini 仅支持 Apple 芯片 Mac。',
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
            '适用于芯片匹配的 Windows 电脑',
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
          body: '通过标准磁盘映像在 Mac 上安装 Snow Shot。',
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
    windowsX64Option: string;
    windowsArm64Option: string;
    macosArm64Option: string;
    macosX64Option: string;
    architectureHint: string;
    intelTag: string;
    macosX64SectionTitle: readonly [string, string];
    macosX64Note: string;
    windows: PlatformCopy;
    macos: PlatformCopy;
  }
>;

const systems = [
  { platform: 'windows', architecture: 'x64', label: 'windowsX64Option' },
  { platform: 'windows', architecture: 'arm64', label: 'windowsArm64Option' },
  { platform: 'macos', architecture: 'arm64', label: 'macosArm64Option' },
  { platform: 'macos', architecture: 'x64', label: 'macosX64Option' },
] as const;

const arm64WindowsAssets: Partial<Record<ReleaseAsset, ReleaseAsset>> = {
  windowsOnline: 'windowsArm64Online',
  windowsOffline: 'windowsArm64Offline',
  windowsPortable: 'windowsArm64Portable',
  windowsMiniOnline: 'windowsArm64MiniOnline',
  windowsMiniPortable: 'windowsArm64MiniPortable',
};

function SystemSelect({
  page,
  value,
  showHint,
  onChange,
}: {
  page: (typeof copy)[Locale];
  value: { platform: DownloadPlatform; architecture: DownloadArchitecture };
  showHint: boolean;
  onChange: (next: DownloadTarget) => void;
}) {
  return (
    <div className="snow-os-select">
      <label htmlFor="snow-download-platform">{page.selectLabel}</label>
      <div className="snow-os-select__field">
        <select
          id="snow-download-platform"
          value={`${value.platform}-${value.architecture}`}
          aria-describedby={showHint ? 'snow-download-system-hint' : undefined}
          onChange={(event) => {
            const next = systems.find(
              (system) =>
                `${system.platform}-${system.architecture}` ===
                event.target.value,
            );
            if (next) {
              onChange(next);
            }
          }}
        >
          {systems.map((system) => (
            <option
              key={`${system.platform}-${system.architecture}`}
              value={`${system.platform}-${system.architecture}`}
            >
              {page[system.label]}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

function rememberTarget(next: DownloadTarget) {
  const url = new URL(window.location.href);
  url.searchParams.set('os', next.platform);
  if (next.architecture) {
    url.searchParams.set('arch', next.architecture);
  }
  window.history.replaceState(
    null,
    '',
    `${url.pathname}${url.search}${url.hash}`,
  );
}

export function DownloadPage({ locale }: { locale: Locale }) {
  const resolved = useResolvedDownloadTarget();
  const [override, setOverride] = useState<DownloadTarget | null>(null);
  const target = override ?? resolved;
  const { platform } = target;
  const architecture =
    target.architecture ?? (platform === 'macos' ? 'arm64' : 'x64');
  const page = copy[locale];
  const content: PlatformCopy = page[platform];
  const intelMac = platform === 'macos' && architecture === 'x64';
  const sectionTitle = intelMac
    ? page.macosX64SectionTitle
    : content.sectionTitle;
  const architectureAsset = (asset: ReleaseAsset): ReleaseAsset =>
    platform === 'windows' && architecture === 'arm64'
      ? (arm64WindowsAssets[asset] ?? asset)
      : intelMac && asset === 'macosDmg'
        ? 'macosX64Dmg'
        : asset;
  const cards = content.cards
    .filter((card) => !intelMac || card.tone !== 'mini')
    .map((card): DownloadCard => {
      const points: DownloadCard['points'] =
        intelMac && card.asset === 'macosDmg'
          ? [
              locale === 'zh'
                ? '适用于 macOS x64（Intel）'
                : 'Built for macOS x64 (Intel)',
              card.points[1],
              card.points[2],
            ]
          : card.points;
      return {
        ...card,
        tag: intelMac ? page.intelTag : card.tag,
        points,
        asset: architectureAsset(card.asset),
        alternate: card.alternate && {
          ...card.alternate,
          asset: architectureAsset(card.alternate.asset),
        },
      };
    });

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
            page={page}
            value={{ platform, architecture }}
            showHint={target.architecture === null}
            onChange={(next) => {
              setOverride(next);
              rememberTarget(next);
            }}
          />
          {target.architecture === null && (
            <p
              id="snow-download-system-hint"
              className="snow-download-system-hint"
            >
              {page.architectureHint}
            </p>
          )}
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
            {sectionTitle[0]}
            <br />
            {sectionTitle[1]}
          </h2>
        </div>
        <div id="download-channels">
          <p className="snow-download-hero__intro">
            {locale === 'zh'
              ? '选择安装方式，直接从 Gitee 下载对应安装包。也可通过下方 GitHub 发布页下载。'
              : 'Choose an installation method to download the matching package directly from GitHub. You can also browse the Gitee release below.'}
          </p>
        </div>
        {platform === 'macos' && (
          <MacInstallOption
            key={architecture}
            locale={locale}
            architecture={architecture}
          />
        )}
        <div
          className={
            cards.length === 1
              ? 'snow-download-grid snow-download-grid--single'
              : cards.length === 4
                ? 'snow-download-grid snow-download-grid--paired'
                : 'snow-download-grid'
          }
        >
          {cards.map((card) => (
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
        <p className="snow-download-note__body">
          {intelMac ? page.macosX64Note : content.noteBody}
        </p>
      </section>
    </main>
  );
}
