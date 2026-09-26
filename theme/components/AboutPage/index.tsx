import './style.css';
import { useHead } from '@rspress/core/runtime';

type Locale = 'en' | 'zh';
type IconName =
  | 'capture'
  | 'annotate'
  | 'text'
  | 'record'
  | 'pin'
  | 'history'
  | 'code'
  | 'heart'
  | 'chat'
  | 'arrow'
  | 'download';

const projectUrl = 'https://github.com/mg-chao/snow-apps';

const copy = {
  en: {
    eyebrow: 'A LITTLE ABOUT SNOW SHOT',
    title: ['Small tool.', 'Clearer ideas.'],
    intro:
      'A screenshot can say so much. Snow Shot helps you capture the right moment, add a little context, and make yourself understood.',
    download: 'Get Snow Shot',
    source: 'Explore the source',
    free: 'Free & open source',
    platforms: 'For Windows & macOS',
    artwork: 'A little clarity, captured.',
    annotation: 'Make your point.',
    ocr: 'From pixels to words',
    tools: [
      'Capture',
      'Annotate',
      'Recognize text',
      'Record',
      'Pin',
      'Find again',
    ],
    storyLabel: 'THE IDEA BEHIND IT',
    storyTitle: ['Less explaining.', 'More understanding.'],
    storyBody:
      'A detail worth saving. A fix that’s easier to show. A few lines of text you don’t want to type again. These small moments are part of every working day.',
    storyEnd:
      'Snow Shot brings capture, annotation, text recognition, and recording together, so you can spend less time moving between tools and more time on what you want to say.',
    madeBy: 'Made by',
    partOf: 'Part of Snow Apps',
    openLabel: 'BUILT IN THE OPEN',
    openTitle: ['Good tools get better', 'when we build together.'],
    openBody:
      'Read the code, share an idea, or help with a fix. Snow Shot is free and open source, with room for you to make it better.',
    github: 'Find us on GitHub',
    license: 'GPL-3.0-or-later',
    licenseLabel: 'View the Snow Shot license',
    thanks: 'Made possible by open-source projects.',
    credits: 'Meet the dependencies',
    communityLabel: 'LET’S MAKE IT BETTER',
    communityTitle: 'A small tool. A shared effort.',
    communityBody:
      'Every thoughtful suggestion, bug report, and contribution helps shape what comes next.',
    resources: [
      {
        title: 'Contribute on GitHub',
        body: 'Explore the code. Make something better.',
        action: 'Visit the repository',
      },
      {
        title: 'Feedback & ideas',
        body: 'Found a bug? Have something in mind?',
        action: 'Open an issue',
      },
      {
        title: 'See what’s new',
        body: 'Follow the latest changes to Snow Shot.',
        action: 'Read the release notes',
      },
    ],
    group: 'QQ Group',
    groupBody: 'Chat, share tips, and get help.',
    join: 'Join group',
    closing: 'Here’s to clearer screenshots. And better work.',
  },
  zh: {
    eyebrow: '关于 SNOW SHOT',
    title: ['小小工具，', '让表达更清晰。'],
    intro:
      '一张截图，可以说很多。Snow Shot 帮你捕捉恰好的瞬间，添上必要的说明，让每一次表达都更容易被理解。',
    download: '下载 Snow Shot',
    source: '探索源代码',
    free: '免费 · 开源',
    platforms: '适用于 Windows 和 macOS',
    artwork: '把清晰，留在这一刻。',
    annotation: '重点，一眼就懂。',
    ocr: '从像素，到文字',
    tools: ['截图', '标注', '文字识别', '录屏', '贴图', '历史记录'],
    storyLabel: '从日常的小事出发',
    storyTitle: ['少一点解释，', '多一分理解。'],
    storyBody:
      '一个值得留存的细节，一段演示更直观的操作，几行不想重新输入的文字。这些小小的时刻，每天都在发生。',
    storyEnd:
      'Snow Shot 把截图、标注、文字识别和录屏放在一起，让你少一些工具之间的切换，把时间留给真正想表达的内容。',
    madeBy: '开发者',
    partOf: 'Snow Apps 的一员',
    openLabel: '开放源码，共同打磨',
    openTitle: ['好用的工具，', '因你我而更好。'],
    openBody:
      '读一读代码，分享一个想法，或修复一个问题。Snow Shot 免费且开源，期待你一起让它变得更好。',
    github: '在 GitHub 上找到我们',
    license: 'GPL-3.0-or-later',
    licenseLabel: '查看 Snow Shot 开源许可证',
    thanks: '感谢让这一切成为可能的开源项目。',
    credits: '查看开源依赖',
    communityLabel: '一起，让它更好用',
    communityTitle: '小小工具，汇聚你我的心意。',
    communityBody:
      '每一个用心的建议、问题反馈与代码贡献，都在帮助我们走向下一步。',
    resources: [
      {
        title: '参与开源',
        body: '探索源代码，一起完善每个细节。',
        action: '访问 GitHub 仓库',
      },
      {
        title: '反馈与建议',
        body: '遇到了问题，或有个新想法？',
        action: '提交 Issue',
      },
      {
        title: '看看新变化',
        body: '了解 Snow Shot 的更新与改进。',
        action: '查看更新日志',
      },
    ],
    group: 'QQ 交流群',
    groupBody: '交流心得，分享技巧，获取帮助。',
    join: '加入群聊',
    closing: '让截图更清晰，让工作更出色。',
  },
};

const iconPaths: Record<IconName, string> = {
  capture:
    'M8 3H5a2 2 0 0 0-2 2v3m13-5h3a2 2 0 0 1 2 2v3M3 16v3a2 2 0 0 0 2 2h3m8 0h3a2 2 0 0 0 2-2v-3M7 7h10v10H7z',
  annotate: 'm15 4 5 5M4 20l5-1L21 7a2 2 0 0 0-5-5L4 14zM4 14l5 5',
  text: 'M4 8V4h4m8 0h4v4M4 16v4h4m8 0h4v-4M8 9V8h8v1m-4-1v8m-3 0h6',
  record:
    'M14 8h2l5-3v14l-5-3h-2M5 6h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Z',
  pin: 'm8 3 8 0m-7 0v6l-4 5v2h14v-2l-4-5V3m-3 13v6',
  history: 'M3 11a9 9 0 1 1 2 7M3 4v7h7m2-4v6l4 2',
  code: 'm8 6-6 6 6 6m8-12 6 6-6 6m-3-15-2 18',
  heart: 'M20 5c-3-3-7-1-8 1-1-2-5-4-8-1-5 5 4 11 8 15 4-4 13-10 8-15Z',
  chat: 'M21 11a8 8 0 0 1-8 8H8l-5 3V7a4 4 0 0 1 4-4h6a8 8 0 0 1 8 8ZM7 9h10M7 13h6',
  arrow: 'M5 12h14m-6-6 6 6-6 6',
  download: 'M12 3v12m-5-5 5 5 5-5M4 16v4h16v-4',
};

function AboutIcon({ name }: { name: IconName }) {
  return (
    <svg aria-hidden="true" className="snow-about__icon" viewBox="0 0 24 24">
      <path d={iconPaths[name]} />
    </svg>
  );
}

function CaptureIllustration({ locale }: { locale: Locale }) {
  const t = copy[locale];
  return (
    <div className="snow-about-art" aria-hidden="true">
      <div className="snow-about-art__orbit" />
      <div className="snow-about-art__window">
        <div className="snow-about-art__titlebar">
          <span className="snow-about-art__dots">
            <i />
            <i />
            <i />
          </span>
          <span>Snow Shot</span>
          <AboutIcon name="capture" />
        </div>
        <div className="snow-about-art__landscape">
          <svg
            aria-hidden="true"
            viewBox="0 0 440 270"
            preserveAspectRatio="xMidYMid slice"
          >
            <circle cx="338" cy="67" r="34" className="snow-about-art__sun" />
            <path
              d="M-35 275 144 66l113 144 77-117 150 182Z"
              className="snow-about-art__mountain-back"
            />
            <path
              d="m104 113 40-47 47 60-28-12-20-22-13 29-13-14Z"
              className="snow-about-art__snow"
            />
            <path
              d="m302 142 32-49 36 59-22-11-14-22-14 28Z"
              className="snow-about-art__snow"
            />
            <path
              d="M-25 270 78 154l62 72 99-101 137 145Z"
              className="snow-about-art__mountain-front"
            />
            <path
              d="m206 158 33-33 40 42-25-8-15-13-17 19Z"
              className="snow-about-art__snow"
            />
            <path
              d="M0 243c74-49 118 2 185-4s154-74 255-17v48H0Z"
              className="snow-about-art__snow"
            />
            <g className="snow-about-art__flakes">
              <circle cx="40" cy="52" r="2" />
              <circle cx="205" cy="42" r="2.5" />
              <circle cx="285" cy="83" r="2" />
              <circle cx="390" cy="155" r="2" />
            </g>
          </svg>
          <div className="snow-about-art__selection">
            <span className="snow-about-art__size">280 × 160</span>
            <i />
            <i />
            <i />
            <i />
            <img src="/app-icon.svg" alt="" width="68" height="68" />
            <span className="snow-about-art__name">Snow Shot</span>
          </div>
        </div>
      </div>
      <div className="snow-about-art__annotation">
        <AboutIcon name="annotate" />
        <span>{t.annotation}</span>
      </div>
      <div className="snow-about-art__recognition">
        <span className="snow-about-art__ocr-icon">
          <AboutIcon name="text" />
        </span>
        <div>
          <span>{t.tools[2]}</span>
          <strong>{t.ocr}</strong>
        </div>
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="snow-about__icon"
        >
          <path d="m5 12 4 4L19 6" />
        </svg>
      </div>
      <div className="snow-about-art__toolbar">
        {(['capture', 'annotate', 'text', 'pin'] as const).map((name) => (
          <span key={name}>
            <AboutIcon name={name} />
          </span>
        ))}
        <span className="snow-about-art__done">
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            className="snow-about__icon"
          >
            <path d="m5 12 4 4L19 6" />
          </svg>
        </span>
      </div>
      <p className="snow-about-art__caption">{t.artwork}</p>
    </div>
  );
}

const toolIcons: IconName[] = [
  'capture',
  'annotate',
  'text',
  'record',
  'pin',
  'history',
];
const resources: { icon: IconName; path: string }[] = [
  { icon: 'code', path: '' },
  { icon: 'chat', path: '/issues' },
  { icon: 'history', path: '/releases' },
];
const groups = [
  { name: '2', number: '895818102', href: 'https://qm.qq.com/q/hRIRFED9Ze' },
  { name: '3', number: '1037819112', href: 'https://qm.qq.com/q/Ts3cwNdykW' },
];

export function AboutPage({ locale }: { locale: Locale }) {
  // Rspress custom layouts use the site title unless the page supplies its own.
  useHead({ title: locale === 'zh' ? '关于 Snow Shot' : 'About Snow Shot' });
  const t = copy[locale];
  const downloadHref = locale === 'zh' ? '/zh/download' : '/download';

  return (
    <main className="snow-about" id="top" lang={locale}>
      <div className="snow-about__hero-surface">
        <section
          className="snow-about__hero snow-about__shell"
          aria-labelledby="about-title"
        >
          <div className="snow-about__hero-copy">
            <p className="snow-about__eyebrow">{t.eyebrow}</p>
            <h1 id="about-title">
              {t.title[0]}
              <br />
              <span>{t.title[1]}</span>
            </h1>
            <p className="snow-about__intro">{t.intro}</p>
            <div className="snow-about__actions">
              <a
                className="snow-button snow-button--primary"
                href={downloadHref}
              >
                <AboutIcon name="download" />
                {t.download}
              </a>
              <a
                className="snow-about__text-link"
                href={projectUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                {t.source}
                <AboutIcon name="arrow" />
              </a>
            </div>
            <p className="snow-about__meta">
              <span>{t.free}</span>
              <span>{t.platforms}</span>
            </p>
          </div>
          <CaptureIllustration locale={locale} />
        </section>
      </div>

      <div className="snow-about__shell">
        <ul
          className="snow-about__toolkit"
          aria-label={locale === 'zh' ? 'Snow Shot 功能' : 'Snow Shot toolkit'}
        >
          {t.tools.map((label, index) => (
            <li key={toolIcons[index]}>
              <AboutIcon name={toolIcons[index]} />
              <span>{label}</span>
            </li>
          ))}
        </ul>

        <section
          className="snow-about__story"
          aria-labelledby="about-story-title"
        >
          <div>
            <p className="snow-about__eyebrow">{t.storyLabel}</p>
            <h2 id="about-story-title">
              {t.storyTitle[0]}
              <br />
              {t.storyTitle[1]}
            </h2>
          </div>
          <div className="snow-about__story-copy">
            <p>{t.storyBody}</p>
            <p>{t.storyEnd}</p>
            <div className="snow-about__maker">
              <img src="/app-icon.svg" alt="" width="30" height="30" />
              <span>
                {t.madeBy}{' '}
                <a
                  href="https://github.com/mg-chao"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  mg-chao
                </a>
                <small>{t.partOf}</small>
              </span>
            </div>
          </div>
        </section>

        <section
          className="snow-about__open"
          aria-labelledby="about-open-title"
        >
          <div className="snow-about__open-copy">
            <p className="snow-about__eyebrow">{t.openLabel}</p>
            <h2 id="about-open-title">
              {t.openTitle[0]}
              <br />
              {t.openTitle[1]}
            </h2>
            <p>{t.openBody}</p>
            <a
              className="snow-about__text-link"
              href={projectUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              {t.github}
              <AboutIcon name="arrow" />
            </a>
          </div>
          <div className="snow-about__source-mark">
            <div className="snow-about__code-art" aria-hidden="true">
              <span>&lt;</span>
              <img src="/app-icon.svg" alt="" width="78" height="78" />
              <span>/&gt;</span>
            </div>
            <a
              className="snow-about__license"
              aria-label={t.licenseLabel}
              href={`${projectUrl}/blob/main/snow_shot/COPYRIGHT`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="snow-about__license-dot" />
              {t.license}
              <AboutIcon name="arrow" />
            </a>
          </div>
          <div className="snow-about__credits">
            <span>{t.thanks}</span>
            <a
              href={`${projectUrl}/blob/main/snow_shot/THIRD_PARTY_NOTICES.md`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {t.credits}
              <AboutIcon name="arrow" />
            </a>
          </div>
        </section>

        <section
          className="snow-about__community"
          aria-labelledby="about-community-title"
        >
          <p className="snow-about__eyebrow">{t.communityLabel}</p>
          <h2 id="about-community-title">{t.communityTitle}</h2>
          <p className="snow-about__community-intro">{t.communityBody}</p>
          <div className="snow-about__resources">
            {resources.map((resource, index) => (
              <a
                key={resource.icon}
                className="snow-about__resource"
                href={`${projectUrl}${resource.path}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <AboutIcon name={resource.icon} />
                <h3>{t.resources[index].title}</h3>
                <p>{t.resources[index].body}</p>
                <span>
                  {t.resources[index].action}
                  <AboutIcon name="arrow" />
                </span>
              </a>
            ))}
          </div>
          <div className="snow-about__groups">
            {groups.map((group) => (
              <a
                className="snow-about__group"
                href={group.href}
                key={group.number}
                target="_blank"
                rel="noopener noreferrer"
              >
                <span className="snow-about__group-icon">
                  <AboutIcon name="chat" />
                </span>
                <span className="snow-about__group-copy">
                  <strong>
                    {t.group} {group.name}
                    <span>{group.number}</span>
                  </strong>
                  <small>{t.groupBody}</small>
                </span>
                <span className="snow-about__group-action">
                  {t.join}
                  <AboutIcon name="arrow" />
                </span>
              </a>
            ))}
          </div>
        </section>
        <p className="snow-about__closing">
          <AboutIcon name="heart" />
          {t.closing}
        </p>
      </div>
    </main>
  );
}
