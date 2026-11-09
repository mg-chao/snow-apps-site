import { useDark, useLang } from '@rspress/core/runtime';
import { downloadPageUrl, useDownloadTarget } from '../../platform';
import { repositoryUrl } from '../../seo';
import { SnowCanvas } from '../SnowCanvas';
import { FeatureShowcase } from '../FeatureShowcase';
import { HeroAppPreview } from './HeroAppPreview';

function DownloadIcon() {
  return (
    <svg aria-hidden="true" className="snow-button-icon" viewBox="0 0 18 18">
      <path d="M9 2v9M5.5 8.5 9 12l3.5-3.5M3 14.5h12" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg aria-hidden="true" className="snow-arrow-icon" viewBox="0 0 18 18">
      <path d="M3 9h11M10 4l5 5-5 5" />
    </svg>
  );
}

function OpenSourceIcon() {
  return (
    <svg
      aria-hidden="true"
      className="snow-open-source__icon"
      viewBox="0 0 32 32"
    >
      <path d="m12 8-8 8 8 8M20 8l8 8-8 8M18 5l-4 22" />
    </svg>
  );
}

function DownloadButton({ isZh }: { isZh: boolean }) {
  const target = useDownloadTarget();
  const label =
    target.platform === 'macos'
      ? isZh
        ? '下载 macOS 版'
        : 'Download for macOS'
      : isZh
        ? '下载 Windows 版'
        : 'Download for Windows';

  return (
    <div className="snow-download-wrap">
      <a
        className="snow-button snow-button--primary"
        href={downloadPageUrl(isZh ? 'zh' : 'en', target)}
      >
        <DownloadIcon />
        {label}
      </a>
    </div>
  );
}

export function HomeLayout() {
  const lang = useLang();
  const isDark = useDark();
  const isZh = lang.startsWith('zh');
  const copy = isZh
    ? {
        titlePrefix: '免费',
        titleAccent: '开源',
        titleSuffix: '的',
        titleSecondLine: '截图与录屏工具',
        description:
          'Snow Shot 支持 Windows 和 macOS，集成截图标注、滚动长截图、本地文本识别与桌面贴图。优雅截图，清晰分享。',
        secondary: 'GitHub 源码与下载',
        sectionTitle: '让每一次截图都服务于高效工作。',
        sectionDescription:
          '轻松截取，快速整理，随时查找和分享。每一步都为清晰表达与出色工作而设计。',
        openSourceEyebrow: '开放项目 / 一起打磨',
        openSourceTitle: '为日常工作打造，也在社区中持续成长。',
        openSourceDescription:
          'Snow Shot 免费开源。欢迎在 GitHub 反馈问题、提出建议或贡献代码，一起让截图与录屏更顺手。',
        openSourceLink: '访问 Snow Shot 官方 GitHub 仓库',
        openSourceLabel: 'SNOW SHOT / 开源项目',
        openSourceWorkflow: ['截图', '说明', '分享'],
        openSourceNote: '跨平台 · 开放协作 · 持续改进',
        availabilityEyebrow: '随时开始',
        commandTitle: '一个快捷键，优雅截图，高效完成工作。',
        commandHint: '唤起截图并复制结果',
        ctaTitle: '从下一张截图开始，优雅高效地工作。',
        ctaDescription:
          'Snow Shot 为高效工作精心打造，让每一次截图都更简单、更出色。',
        footer: '优雅截图，出色工作。',
      }
    : {
        titlePrefix: 'Free, ',
        titleAccent: 'open-source',
        titleSuffix: '',
        titleSecondLine: 'screenshots & recording',
        description:
          'Snow Shot for Windows and macOS. Annotate captures, take scrolling screenshots, extract text with local text recognition, and pin references above your work.',
        secondary: 'Source & releases on GitHub',
        sectionTitle: 'Make every screenshot work harder.',
        sectionDescription:
          'Capture simply, refine in seconds, and keep every result ready to find or share. Every step is designed for clear communication and excellent work.',
        openSourceEyebrow: 'OPEN SOURCE / BUILT IN THE OPEN',
        openSourceTitle: 'Made for daily work. Shaped in the open.',
        openSourceDescription:
          'Snow Shot is free and open source. Report issues, share ideas, or contribute code on GitHub to help make everyday capture and recording smoother.',
        openSourceLink: 'Visit the official Snow Shot GitHub repository',
        openSourceLabel: 'SNOW SHOT / OPEN SOURCE',
        openSourceWorkflow: ['capture', 'clarify', 'share'],
        openSourceNote:
          'Cross-platform · Open collaboration · Always improving',
        availabilityEyebrow: 'READY WHEN YOU ARE',
        commandTitle:
          'One shortcut to an elegant screenshot and excellent work.',
        commandHint: 'Invoke the screenshot and copy the result.',
        ctaTitle: 'Start your next piece of work with a better screenshot.',
        ctaDescription:
          'Snow Shot is carefully crafted for efficient work, making every screenshot simpler and better.',
        footer: 'Screenshot simply. Work excellently.',
      };
  return (
    <main className="snow-home">
      <section className="snow-hero" id="top">
        <SnowCanvas />
        <div className="snow-hero__inner">
          <div className="snow-hero__copy">
            <h1>
              <span>
                {copy.titlePrefix}
                <span className="snow-title-accent">{copy.titleAccent}</span>
                {copy.titleSuffix}
              </span>
              <br />
              <span>{copy.titleSecondLine}</span>
            </h1>
            <p className="snow-hero__description">{copy.description}</p>
            <div className="snow-hero__actions">
              <DownloadButton isZh={isZh} />
              <a
                className="snow-button snow-button--quiet"
                href={repositoryUrl}
              >
                {copy.secondary}
                <ArrowIcon />
              </a>
            </div>
          </div>
        </div>
        <div className="snow-hero__preview">
          <div className="snow-hero__image-shell">
            <HeroAppPreview isDark={isDark} isZh={isZh} />
          </div>
        </div>
      </section>
      <FeatureShowcase isZh={isZh} />
      <section
        className="snow-command section-shell"
        aria-labelledby="command-title"
      >
        <div className="snow-command__index">/ 07</div>
        <div>
          <p className="snow-eyebrow">
            {isZh ? '更多掌控' : 'A LITTLE MORE CONTROL'}
          </p>
          <h2 id="command-title">{copy.commandTitle}</h2>
        </div>
        <div className="snow-command__keys">
          <kbd>Ctrl</kbd>
          <span>+</span>
          <kbd>F1</kbd>
          <p>{copy.commandHint}</p>
        </div>
      </section>
      <section
        className="snow-open-source section-shell"
        aria-labelledby="open-source-title"
      >
        <div className="snow-open-source__copy">
          <p className="snow-eyebrow">{copy.openSourceEyebrow}</p>
          <h2 id="open-source-title">{copy.openSourceTitle}</h2>
          <p>{copy.openSourceDescription}</p>
          <a
            className="snow-text-link"
            href="https://github.com/mg-chao/snow-shot"
          >
            {copy.openSourceLink}
            <ArrowIcon />
          </a>
        </div>
        <div className="snow-open-source__panel">
          <div className="snow-open-source__panel-top">
            <OpenSourceIcon />
            <span>{copy.openSourceLabel}</span>
          </div>
          <div className="snow-open-source__code" aria-hidden="true">
            {copy.openSourceWorkflow.map((step, index) => (
              <span key={step}>
                {index > 0 && (
                  <span className="snow-open-source__code-accent"> → </span>
                )}
                {step}
              </span>
            ))}
          </div>
          <p>{copy.openSourceNote}</p>
        </div>
      </section>
      <section className="snow-final-cta">
        <div className="snow-final-cta__inner">
          <div>
            <p className="snow-eyebrow">{copy.availabilityEyebrow}</p>
            <h2>{copy.ctaTitle}</h2>
            <p>{copy.ctaDescription}</p>
          </div>
          <DownloadButton isZh={isZh} />
        </div>
      </section>
    </main>
  );
}
