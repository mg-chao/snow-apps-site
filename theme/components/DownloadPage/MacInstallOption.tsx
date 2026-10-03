import { useState } from 'react';
import {
  type MacosEdition,
  macosInstallCommand,
  releaseDownloadUrl,
} from './releaseLinks';

const text = {
  en: {
    tag: 'INSTALL FROM TERMINAL',
    title: 'One command. Ready to capture.',
    body: 'Choose your edition, then open Terminal, paste the command, and press Return. The script downloads the latest release, verifies it, signs it locally, and installs it in Applications.',
    edition: 'Edition',
    copy: 'Copy command',
    copied: 'Command copied',
    failed: 'Select and copy the command below.',
    inspect: 'Download installation script',
    note: 'Requires macOS 15 or later on Apple silicon. Run as your usual user; enter your Mac password only if prompted. On first launch, allow the requested privacy permissions.',
  },
  zh: {
    tag: '通过终端安装',
    title: '一条命令，完成安装。',
    body: '选择版本，然后打开「终端」，粘贴命令并按回车。脚本会下载最新发布版本、校验、在本机签名，并安装到应用程序文件夹。',
    edition: '版本',
    copy: '复制安装命令',
    copied: '已复制安装命令',
    failed: '请选中并复制下方命令。',
    inspect: '下载安装脚本',
    note: '适用于运行 macOS 15 或更新版本的 Apple 芯片 Mac。请以日常用户运行，仅在提示时输入 Mac 密码。首次启动时，请按提示授予隐私权限。',
  },
} as const;

export function MacInstallOption({ locale }: { locale: 'en' | 'zh' }) {
  const content = text[locale];
  const [edition, setEdition] = useState<MacosEdition>('full');
  const [status, setStatus] = useState<'idle' | 'copied' | 'failed'>('idle');
  const scriptUrl = releaseDownloadUrl(locale, 'macosInstallScript');
  const command = macosInstallCommand(locale, edition);

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
      <div className="snow-os-select snow-macos-install__edition">
        <label htmlFor="snow-macos-install-edition">{content.edition}</label>
        <div className="snow-os-select__field">
          <select
            id="snow-macos-install-edition"
            value={edition}
            onChange={(event) => {
              setEdition(event.target.value === 'mini' ? 'mini' : 'full');
              setStatus('idle');
            }}
          >
            <option value="full">Snow Shot</option>
            <option value="mini">Snow Shot Mini</option>
          </select>
        </div>
      </div>
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
