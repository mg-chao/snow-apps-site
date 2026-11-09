export type SiteLocale = 'en' | 'zh';
export type SiteLink = { label: string; href: string };

export function siteLinks(locale: SiteLocale) {
  const isZh = locale === 'zh';
  const prefix = isZh ? '/zh' : '';
  const link = (path: string, zh: string, en: string): SiteLink => ({
    label: isZh ? zh : en,
    href: `${prefix}${path}`,
  });
  return {
    home: link('/index.html', '首页', 'Home'),
    download: link('/download.html', '下载', 'Download'),
    guides: link('/guides/index.html', '使用手册', 'User manual'),
    install: link(
      '/guides/getting-started/install.html',
      '安装与更新',
      'Install, choose an edition, and update',
    ),
    quickStart: link(
      '/guides/getting-started/quick-start.html',
      '完成第一张截图',
      'Take your first screenshot',
    ),
    shortcuts: link(
      '/guides/settings/shortcuts.html',
      '快捷键与全局鼠标',
      'Shortcuts and global mouse actions',
    ),
    scrolling: link(
      '/guides/capture/scrolling.html',
      '滚动长截图与拼接检查',
      'Scrolling capture and stitching checks',
    ),
    capture: link(
      '/guides/capture/basics.html',
      '区域、窗口与控件截图',
      'Region, window and control capture',
    ),
    annotation: link(
      '/guides/annotations/basics.html',
      '标注入门与通用样式',
      'Annotation basics and shared styles',
    ),
    arrows: link('/guides/annotations/arrows.html', '箭头', 'Arrows'),
    recognition: link(
      '/guides/recognition/text.html',
      '文本识别与结果整理',
      'Text recognition and cleanup',
    ),
    table: link(
      '/guides/recognition/table.html',
      '表格识别与单元格编辑',
      'Table recognition and cell editing',
    ),
    pinning: link(
      '/guides/pinning/image.html',
      '图片与剪贴板贴图',
      'Image and clipboard pins',
    ),
    recording: link(
      '/guides/recording/start.html',
      '录屏区域与开始暂停停止',
      'Recording area, start, pause, and stop',
    ),
    history: link(
      '/guides/output/history.html',
      '截图历史与批量处理',
      'Screenshot history and bulk actions',
    ),
    changelog: link('/changelog.html', '更新日志', 'Changelog'),
    about: link('/about.html', '关于', 'About'),
  };
}

export function footerSections(locale: SiteLocale) {
  const links = siteLinks(locale);
  return [
    {
      title: locale === 'zh' ? '开始使用' : 'Get started',
      links: [links.download, links.install, links.quickStart, links.shortcuts],
    },
    {
      title: locale === 'zh' ? '功能指南' : 'Feature guides',
      links: [
        links.scrolling,
        links.recognition,
        links.pinning,
        links.recording,
      ],
    },
    {
      title: locale === 'zh' ? '了解项目' : 'The project',
      links: [links.home, links.guides, links.changelog, links.about],
    },
  ];
}
