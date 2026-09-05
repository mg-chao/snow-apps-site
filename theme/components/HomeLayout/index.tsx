import { useDark, useLang } from '@rspress/core/runtime';
import { SnowCanvas } from '../SnowCanvas';

type Feature = {
  eyebrow: string;
  title: string;
  details: string;
  tone: string;
  visual: 'annotate' | 'organize' | 'capture' | 'ocr' | 'record' | 'pin';
};

const features: Record<'en' | 'zh', Feature[]> = {
  en: [
    {
      eyebrow: '01 / EXPLAIN IN SECONDS',
      title: 'Make every screenshot easy to understand',
      details:
        'Add arrows, highlights, blur, and text in one clean pass. Turn a raw capture into a clear explanation immediately.',
      tone: 'lavender',
      visual: 'annotate',
    },
    {
      eyebrow: '02 / FIND IT FAST',
      title: 'Every capture, ready when you are',
      details:
        'Keep recent screenshots organized and searchable. Find the right frame without opening a file browser.',
      tone: 'sky',
      visual: 'organize',
    },
    {
      eyebrow: '03 / CAPTURE IMMEDIATELY',
      title: 'Choose a mode. Capture in one move.',
      details:
        'Full screen, window, region, scrolling page, or delay. Pick the right mode and get back to work.',
      tone: 'butter',
      visual: 'capture',
    },
    {
      eyebrow: '04 / REUSE WHAT YOU SEE',
      title: 'Turn pixels into usable text',
      details:
        'Recognize text and structured tables directly from an image, then copy clean results in one step.',
      tone: 'mint',
      visual: 'ocr',
    },
    {
      eyebrow: '05 / SHOW IT QUICKLY',
      title: 'Record the fix instead of describing it',
      details:
        'Capture a focused video with cursor context and clean audio. Give teammates the answer in seconds.',
      tone: 'peach',
      visual: 'record',
    },
    {
      eyebrow: '06 / KEEP IT IN VIEW',
      title: 'Pin the important part above everything',
      details:
        'Keep a screenshot, document, or note above other windows. Your reference stays close while you work.',
      tone: 'ink',
      visual: 'pin',
    },
  ],
  zh: [
    {
      eyebrow: '01 / 几秒说清楚',
      title: '让每张截图都一看就懂',
      details: '箭头、重点、模糊和文字一次完成，把原始截图立刻变成清晰说明。',
      tone: 'lavender',
      visual: 'annotate',
    },
    {
      eyebrow: '02 / 快速找回',
      title: '每一次截图，随时都能用',
      details: '自动整理最近截图并支持搜索，不用打开文件夹也能找到正确画面。',
      tone: 'sky',
      visual: 'organize',
    },
    {
      eyebrow: '03 / 立即捕捉',
      title: '选择模式，一步完成截图',
      details: '全屏、窗口、区域、滚动页面或延时截图，选对模式，马上继续工作。',
      tone: 'butter',
      visual: 'capture',
    },
    {
      eyebrow: '04 / 直接复用',
      title: '把画面变成可用文字',
      details: '直接从图片识别文字和结构化表格，一步复制干净结果。',
      tone: 'mint',
      visual: 'ocr',
    },
    {
      eyebrow: '05 / 快速展示',
      title: '录下解决方法，不必写长文',
      details: '录制带有光标和清晰声音的短视频，用几秒钟把答案交给同事。',
      tone: 'peach',
      visual: 'record',
    },
    {
      eyebrow: '06 / 始终在视线内',
      title: '把重要内容固定在所有窗口之上',
      details: '让截图、文档或备注始终浮在上方，工作时参考内容就在手边。',
      tone: 'ink',
      visual: 'pin',
    },
  ],
};

function LogoMark() {
  return (
    <img
      alt=""
      aria-hidden="true"
      className="snow-logo-mark"
      src="/app-icon.svg"
    />
  );
}

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

function FeatureVisual({ kind }: { kind: Feature['visual'] }) {
  const common = {
    className: 'snow-feature-card__visual',
    viewBox: '0 0 360 190',
    role: 'img' as const,
  };

  if (kind === 'annotate') {
    return (
      <svg {...common} aria-label="Screenshot with annotation tools">
        <rect
          className="snow-visual-panel"
          x="13"
          y="18"
          width="334"
          height="157"
          rx="9"
        />
        <rect
          className="snow-visual-window"
          x="29"
          y="34"
          width="302"
          height="125"
          rx="5"
        />
        <path className="snow-visual-line" d="M48 57h100M48 69h76M48 81h58" />
        <rect
          className="snow-visual-highlight"
          x="46"
          y="95"
          width="151"
          height="16"
          rx="3"
        />
        <path
          className="snow-visual-accent"
          d="M222 118l45-36M258 81l11 1-2 11"
        />
        <circle className="snow-visual-dot" cx="222" cy="118" r="4" />
        <rect
          className="snow-visual-tool"
          x="211"
          y="43"
          width="96"
          height="25"
          rx="6"
        />
        <circle className="snow-visual-tool-dot" cx="227" cy="55" r="4" />
        <path
          className="snow-visual-tool-line"
          d="M239 55h12M260 55h12M281 55h12"
        />
      </svg>
    );
  }
  if (kind === 'organize') {
    return (
      <svg {...common} aria-label="Searchable screenshot library">
        <rect
          className="snow-visual-panel"
          x="13"
          y="18"
          width="334"
          height="157"
          rx="9"
        />
        <rect
          className="snow-visual-search"
          x="31"
          y="34"
          width="298"
          height="27"
          rx="7"
        />
        <circle className="snow-visual-search-icon" cx="48" cy="47" r="6" />
        <path className="snow-visual-search-icon" d="M52 51l5 5" />
        <path className="snow-visual-search-text" d="M68 47h72" />
        <g className="snow-visual-thumb">
          <rect x="31" y="78" width="88" height="68" rx="5" />
          <path d="M42 130l20-20 13 12 12-14 21 22" />
          <circle cx="95" cy="94" r="7" />
        </g>
        <g className="snow-visual-thumb snow-visual-thumb--active">
          <rect x="136" y="78" width="88" height="68" rx="5" />
          <path d="M147 130l21-17 13 10 15-18 19 25" />
          <circle cx="198" cy="94" r="7" />
        </g>
        <g className="snow-visual-thumb">
          <rect x="241" y="78" width="88" height="68" rx="5" />
          <path d="M252 130l22-22 13 14 13-12 18 20" />
          <circle cx="304" cy="94" r="7" />
        </g>
      </svg>
    );
  }
  if (kind === 'capture') {
    return (
      <svg {...common} aria-label="Screenshot capture modes">
        <rect
          className="snow-visual-panel"
          x="13"
          y="18"
          width="334"
          height="157"
          rx="9"
        />
        <path
          className="snow-visual-crosshair"
          d="M180 31v18M180 141v18M31 96h18M311 96h18"
        />
        <rect
          className="snow-visual-capture-frame"
          x="64"
          y="44"
          width="232"
          height="104"
          rx="6"
        />
        <path className="snow-visual-line" d="M82 65h91M82 77h64M82 89h42" />
        <rect
          className="snow-visual-highlight"
          x="82"
          y="105"
          width="91"
          height="22"
          rx="4"
        />
        <path
          className="snow-visual-accent"
          d="M208 82h58M208 96h40M208 110h49"
        />
        <circle className="snow-visual-capture-dot" cx="180" cy="96" r="10" />
      </svg>
    );
  }
  if (kind === 'ocr') {
    return (
      <svg {...common} aria-label="Image converted into editable text">
        <rect
          className="snow-visual-panel"
          x="13"
          y="18"
          width="334"
          height="157"
          rx="9"
        />
        <rect
          className="snow-visual-window"
          x="29"
          y="36"
          width="137"
          height="120"
          rx="5"
        />
        <path
          className="snow-visual-line"
          d="M45 59h81M45 72h66M45 85h92M45 98h57"
        />
        <rect
          className="snow-visual-highlight"
          x="45"
          y="111"
          width="95"
          height="24"
          rx="4"
        />
        <path className="snow-visual-arrow" d="M178 96h24M194 89l8 7-8 7" />
        <rect
          className="snow-visual-text-sheet"
          x="218"
          y="36"
          width="113"
          height="120"
          rx="5"
        />
        <path
          className="snow-visual-accent"
          d="M235 57h76M235 70h62M235 83h76M235 96h54M235 117h76M235 130h62"
        />
        <path className="snow-visual-check" d="M235 105l5 5 9-11" />
      </svg>
    );
  }
  if (kind === 'record') {
    return (
      <svg {...common} aria-label="Focused screen recording">
        <rect
          className="snow-visual-panel"
          x="13"
          y="18"
          width="334"
          height="157"
          rx="9"
        />
        <rect
          className="snow-visual-window"
          x="31"
          y="37"
          width="298"
          height="101"
          rx="6"
        />
        <path className="snow-visual-line" d="M50 59h104M50 72h74M50 85h86" />
        <rect
          className="snow-visual-highlight"
          x="50"
          y="99"
          width="104"
          height="21"
          rx="4"
        />
        <circle className="snow-visual-record-dot" cx="288" cy="53" r="7" />
        <path
          className="snow-visual-cursor"
          d="M201 78l22 22-9 1 5 13-6 3-6-13-6 6z"
        />
        <rect
          className="snow-visual-timeline"
          x="47"
          y="151"
          width="266"
          height="9"
          rx="4.5"
        />
        <rect
          className="snow-visual-timeline-progress"
          x="47"
          y="151"
          width="119"
          height="9"
          rx="4.5"
        />
      </svg>
    );
  }
  return (
    <svg {...common} aria-label="Pinned reference window">
      <rect
        className="snow-visual-panel"
        x="13"
        y="18"
        width="334"
        height="157"
        rx="9"
      />
      <rect
        className="snow-visual-window snow-visual-window--back"
        x="42"
        y="43"
        width="193"
        height="103"
        rx="6"
      />
      <path className="snow-visual-line" d="M58 68h97M58 81h74M58 94h82" />
      <rect
        className="snow-visual-highlight"
        x="58"
        y="108"
        width="86"
        height="21"
        rx="4"
      />
      <rect
        className="snow-visual-window snow-visual-window--front"
        x="152"
        y="30"
        width="166"
        height="108"
        rx="6"
      />
      <path className="snow-visual-accent" d="M170 59h91M170 72h74M170 85h98" />
      <path
        className="snow-visual-pin"
        d="M281 46l14 14M289 42l10 10-10 10-8-8zM282 58l-13 13"
      />
      <circle className="snow-visual-pin-dot" cx="269" cy="71" r="3" />
    </svg>
  );
}

function DownloadButton({ isZh }: { isZh: boolean }) {
  return (
    <div className="snow-download-wrap">
      <a
        className="snow-button snow-button--primary"
        href={isZh ? '/zh/download' : '/download'}
      >
        <DownloadIcon />
        {isZh ? '立即下载' : 'Download now'}
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
        titlePrefix: '',
        titleAccent: '优雅',
        titleSuffix: '高效地完成',
        titleSecondLine: '每一次工作',
        description:
          '截图、标注、文字识别和录屏，让屏幕上的每一刻都能清晰表达、轻松分享。',
        secondary: '查看功能',
        sectionTitle: '让每一次截图都服务于高效工作。',
        sectionDescription:
          '轻松截取，快速整理，随时查找和分享。每一步都为清晰表达与出色工作而设计。',
        openSourceEyebrow: '开放项目 / 一起打磨',
        openSourceTitle: '为日常工作打造，也在社区中持续成长。',
        openSourceDescription:
          'Snow Shot 是一款跨平台的开源工具，把截图、标注、文字识别和录屏放在一个专注的工作流里，也欢迎更多想法让它变得更好。',
        openSourceLink: '前往社区',
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
        titlePrefix: 'Work ',
        titleAccent: 'elegantly',
        titleSuffix: ' and',
        titleSecondLine: 'efficiently, every time',
        description:
          'Capture, annotate, extract text, and record your screen. Turn a moment into something worth sharing.',
        secondary: 'Explore features',
        sectionTitle: 'Make every screenshot work harder.',
        sectionDescription:
          'Capture simply, refine in seconds, and keep every result ready to find or share. Every step is designed for clear communication and excellent work.',
        openSourceEyebrow: 'OPEN SOURCE / BUILT IN THE OPEN',
        openSourceTitle: 'Made for daily work. Shaped in the open.',
        openSourceDescription:
          'Snow Shot is a cross-platform open-source tool for focused screen work. Capture, annotate, extract text, and record in one calm workflow, with room for the community to make it better.',
        openSourceLink: 'Visit community',
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
  const localizedFeatures = isZh ? features.zh : features.en;
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
              <a className="snow-button snow-button--quiet" href="#features">
                {copy.secondary}
                <ArrowIcon />
              </a>
            </div>
          </div>
        </div>
        <div className="snow-hero__preview">
          <div className="snow-hero__image-shell">
            <img
              alt={
                isZh
                  ? 'Snow Shot 截图设置界面'
                  : 'Snow Shot screenshot settings interface'
              }
              fetchPriority="high"
              width="1372"
              height="891"
              src={`/images/${isZh ? 'zh' : 'en'}/main${isDark ? '-dark' : ''}.webp`}
            />
          </div>
        </div>
      </section>
      <section
        className="snow-features section-shell"
        id="features"
        aria-labelledby="features-title"
      >
        <div className="snow-section-heading">
          <p className="snow-eyebrow">
            {isZh
              ? '工具箱 / 六项高效能力'
              : 'THE TOOLKIT / SIX SMALL SUPERPOWERS'}
          </p>
          <h2 id="features-title">{copy.sectionTitle}</h2>
          <p>{copy.sectionDescription}</p>
        </div>
        <div className="snow-feature-grid">
          {localizedFeatures.map((feature) => (
            <article
              className={`snow-feature-card snow-feature-card--${feature.tone}`}
              key={feature.title}
            >
              <div className="snow-feature-card__copy">
                <p className="snow-feature-card__eyebrow">{feature.eyebrow}</p>
                <h3>{feature.title}</h3>
                <p>{feature.details}</p>
              </div>
              <FeatureVisual kind={feature.visual} />
            </article>
          ))}
        </div>
      </section>
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
            href="https://github.com/mg-chao/snow-apps"
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
