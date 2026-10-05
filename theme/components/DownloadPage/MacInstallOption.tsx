import { useState } from 'react';
import type { DownloadArchitecture } from '../../platform';
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
    intelBody:
      'Open Terminal, paste the command, and press Return. The script downloads the latest Snow Shot release, verifies it, signs it locally, and installs it in Applications.',
    edition: 'Edition',
    copy: 'Copy command',
    copied: 'Command copied',
    failed: 'Select and copy the command below.',
    inspect: 'Download installation script',
    note: 'Requires macOS 15 or later. The script automatically detects Apple silicon or Intel; Mini requires Apple silicon. Run as your usual user; enter your Mac password only if prompted. On first launch, allow the requested privacy permissions.',
  },
  zh: {
    tag: '通过终端安装',
    title: '一条命令，完成安装。',
    body: '选择版本，然后打开「终端」，粘贴命令并按回车。脚本会下载最新发布版本、校验、在本机签名，并安装到应用程序文件夹。',
    intelBody:
      '打开「终端」，粘贴命令并按回车。脚本会下载最新发布的 Snow Shot 版本、校验、在本机签名，并安装到应用程序文件夹。',
    edition: '版本',
    copy: '复制安装命令',
    copied: '已复制安装命令',
    failed: '请选中并复制下方命令。',
    inspect: '下载安装脚本',
    note: '需要 macOS 15 或更新版本。脚本自动识别 Apple 芯片或 Intel；Mini 仅支持 Apple 芯片。请以日常用户运行，仅在提示时输入 Mac 密码。首次启动时，请按提示授予隐私权限。',
  },
} as const;

export function MacInstallOption({
  locale,
  architecture,
}: {
  locale: 'en' | 'zh';
  architecture: DownloadArchitecture;
}) {
  const content = text[locale];
  const [edition, setEdition] = useState<MacosEdition>('full');
  const [status, setStatus] = useState<'idle' | 'copied' | 'failed'>('idle');
  const scriptUrl = releaseDownloadUrl(locale, 'macosInstallScript');
  const selectedEdition = architecture === 'x64' ? 'full' : edition;
  const command = macosInstallCommand(locale, selectedEdition);

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
      <p>{architecture === 'x64' ? content.intelBody : content.body}</p>
      {architecture === 'arm64' && (
        <div className="snow-os-select snow-macos-install__edition">
          <label htmlFor="snow-macos-install-edition">{content.edition}</label>
          <div className="snow-os-select__field">
            <select
              id="snow-macos-install-edition"
              value={selectedEdition}
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
      )}
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
