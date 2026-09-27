const feijipanShare = 'https://share.feijipan.com/s/n0v5tV1O';
const githubReleases = 'https://github.com/mg-chao/snow-apps/releases/latest';

const text = {
  en: {
    windows: 'Windows',
    macos: 'macOS',
    feijipan: {
      kicker: 'MIRROR',
      title: 'Feijipan',
      body: 'Windows and macOS builds are both in this share.',
      button: 'Open Feijipan',
      aria: 'Open Feijipan in a new tab. Windows and macOS builds are available.',
    },
    github: {
      kicker: 'RELEASES',
      title: 'GitHub',
      body: 'Windows and macOS builds are on the latest release.',
      button: 'Open GitHub',
      aria: 'Open the latest GitHub release in a new tab. Windows and macOS builds are available.',
    },
  },
  zh: {
    windows: 'Windows',
    macos: 'macOS',
    feijipan: {
      kicker: '国内分流',
      title: '小飞机网盘',
      body: '同一分享同时提供 Windows 与 macOS 安装包。',
      button: '前往小飞机网盘',
      aria: '前往小飞机网盘，在新标签页打开。支持 Windows 与 macOS。',
    },
    github: {
      kicker: '官方发布',
      title: 'GitHub',
      body: '最新发布页同时提供 Windows 与 macOS 安装包。',
      button: '前往 GitHub',
      aria: '前往 GitHub 最新发布页，在新标签页打开。支持 Windows 与 macOS。',
    },
  },
} as const;

function ExternalIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" role="presentation">
      <path
        d="M4.5 11.5 11.5 4.5M7 4.5h4.5V9"
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.6"
      />
    </svg>
  );
}

function PlaneMark() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M21.1 3.5 2.9 10.2c-.8.3-.7 1.4.1 1.6l7 1.5 1.5 7c.2.8 1.3.9 1.6.1L21.4 4.8c.3-.8-.5-1.6-1.3-1.3Z"
        fill="currentColor"
      />
      <path
        d="m9.9 13.2 10.4-8.5"
        stroke="#f4f2fb"
        strokeLinecap="round"
        strokeWidth="1.6"
      />
    </svg>
  );
}

function GitHubMark() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
      />
    </svg>
  );
}

export function MirrorLink({ locale }: { locale: 'en' | 'zh' }) {
  const content = text[locale];
  const mirrors = [
    {
      id: 'feijipan',
      href: feijipanShare,
      copy: content.feijipan,
      mark: <PlaneMark />,
    },
    {
      id: 'github',
      href: githubReleases,
      copy: content.github,
      mark: <GitHubMark />,
    },
  ] as const;

  return (
    <div className="snow-mirrors">
      {mirrors.map((mirror) => (
        <aside
          className={`snow-mirror snow-mirror--${mirror.id} rp-not-doc`}
          aria-labelledby={`snow-mirror-${mirror.id}`}
          key={mirror.id}
        >
          <span
            className={`snow-mirror__mark snow-mirror__mark--${mirror.id}`}
            aria-hidden="true"
          >
            {mirror.mark}
          </span>
          <div className="snow-mirror__copy">
            <p className="snow-download-kicker">{mirror.copy.kicker}</p>
            <h3 id={`snow-mirror-${mirror.id}`}>{mirror.copy.title}</h3>
            <p>{mirror.copy.body}</p>
          </div>
          <div className="snow-mirror__action">
            <p className="snow-mirror__systems">
              <span>{content.windows}</span>
              <span>{content.macos}</span>
            </p>
            <a
              className="snow-download-button snow-download-button--dark"
              href={mirror.href}
              rel="noopener noreferrer"
              target="_blank"
              aria-label={mirror.copy.aria}
            >
              {mirror.copy.button}
              <ExternalIcon />
            </a>
          </div>
        </aside>
      ))}
    </div>
  );
}
