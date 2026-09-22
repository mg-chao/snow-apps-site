import { useState } from 'react';

const scriptUrl = 'https://snowshot.top/setup/install-snow-shot-macos.sh';

const text = {
  en: {
    tag: 'INSTALL FROM TERMINAL',
    title: 'One command. Ready to capture.',
    body: 'Open Terminal, paste this command, and press Return. The script downloads, verifies, locally signs, and installs Snow Shot in Applications.',
    copy: 'Copy command',
    copied: 'Command copied',
    failed: 'Select and copy the command below.',
    inspect: 'View installation script',
    note: 'Requires macOS 15 or later on Apple silicon. Run as your usual user; enter your Mac password only if prompted. On first launch, allow the requested privacy permissions.',
    lang: 'en',
  },
  zh: {
    tag: '通过终端安装',
    title: '一条命令，完成安装。',
    body: '打开「终端」，粘贴命令并按回车。脚本会下载、校验、在本机签名，并将 Snow Shot 安装到应用程序文件夹。',
    copy: '复制安装命令',
    copied: '已复制安装命令',
    failed: '请选中并复制下方命令。',
    inspect: '查看安装脚本',
    note: '适用于运行 macOS 15 或更新版本的 Apple 芯片 Mac。请以日常用户运行，仅在提示时输入 Mac 密码。首次启动时，请按提示授予隐私权限。',
    lang: 'zh-CN',
  },
} as const;

export function MacInstallOption({ locale }: { locale: 'en' | 'zh' }) {
  const content = text[locale];
  const [status, setStatus] = useState<'idle' | 'copied' | 'failed'>('idle');
  const command = `curl --fail --location --proto '=https' --proto-redir '=https' --output install-snow-shot-macos.sh ${scriptUrl} &&\nbash install-snow-shot-macos.sh --lang ${content.lang}`;

  async function copyCommand() {
    try {
      await navigator.clipboard.writeText(command);
      setStatus('copied');
    } catch {
      setStatus('failed');
    }
  }

  return (
    <article
      className="snow-macos-install"
      aria-labelledby="macos-install-title"
    >
      <div className="snow-macos-install__heading">
        <div>
          <p className="snow-download-kicker">{content.tag}</p>
          <h3 id="macos-install-title">{content.title}</h3>
        </div>
        <button
          className="snow-download-button snow-download-button--dark"
          type="button"
          onClick={copyCommand}
        >
          {content.copy}
        </button>
      </div>
      <p>{content.body}</p>
      <p role="status" className="snow-macos-install__status">
        {status === 'copied'
          ? content.copied
          : status === 'failed'
            ? content.failed
            : ''}
      </p>
      <textarea
        aria-label={content.copy}
        readOnly
        rows={4}
        value={command}
        onFocus={(event) => event.currentTarget.select()}
      />
      <div className="snow-macos-install__footer">
        <p>{content.note}</p>
        <a href={scriptUrl}>{content.inspect}</a>
      </div>
    </article>
  );
}
