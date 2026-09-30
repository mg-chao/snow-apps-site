import { giteeReleases, githubReleases } from './releaseLinks';

const text = {
  en: {
    windows: 'Windows',
    macos: 'macOS',
    gitee: {
      kicker: 'MIRROR',
      title: 'Gitee',
      body: 'Windows and macOS builds are mirrored on the latest release.',
      button: 'Open Gitee',
      aria: 'Open the latest Gitee release in a new tab. Windows and macOS builds are available.',
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
    gitee: {
      kicker: '国内分流',
      title: 'Gitee',
      body: '最新发布页同步提供 Windows 与 macOS 安装包。',
      button: '前往 Gitee',
      aria: '前往 Gitee 最新发布页，在新标签页打开。支持 Windows 与 macOS。',
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

function GiteeMark() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M5 3h14v4H7v10h10v-4h-5V9h9v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"
        fill="currentColor"
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
      id: 'gitee',
      href: giteeReleases,
      copy: content.gitee,
      mark: <GiteeMark />,
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
