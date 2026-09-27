const feijipanShare = 'https://share.feijipan.com/s/n0v5tV1O';

const text = {
  en: {
    kicker: 'MIRROR',
    title: 'Feijipan',
    body: 'Windows and macOS builds are both in this share.',
    windows: 'Windows',
    macos: 'macOS',
    button: 'Open Feijipan',
    aria: 'Open Feijipan in a new tab. Windows and macOS builds are available.',
  },
  zh: {
    kicker: '国内分流',
    title: '小飞机网盘',
    body: '同一分享同时提供 Windows 与 macOS 安装包。',
    windows: 'Windows',
    macos: 'macOS',
    button: '前往小飞机网盘',
    aria: '前往小飞机网盘，在新标签页打开。支持 Windows 与 macOS。',
  },
} as const;

export function MirrorLink({ locale }: { locale: 'en' | 'zh' }) {
  const content = text[locale];

  return (
    <aside
      className="snow-mirror rp-not-doc"
      aria-labelledby="snow-mirror-title"
    >
      <span className="snow-mirror__mark" aria-hidden="true">
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
      </span>
      <div className="snow-mirror__copy">
        <p className="snow-download-kicker">{content.kicker}</p>
        <h3 id="snow-mirror-title">{content.title}</h3>
        <p>{content.body}</p>
      </div>
      <div className="snow-mirror__action">
        <p className="snow-mirror__systems">
          <span>{content.windows}</span>
          <span>{content.macos}</span>
        </p>
        <a
          className="snow-download-button snow-download-button--dark"
          href={feijipanShare}
          rel="noopener noreferrer"
          target="_blank"
          aria-label={content.aria}
        >
          {content.button}
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
        </a>
      </div>
    </aside>
  );
}
