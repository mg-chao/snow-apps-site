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
    pricing: link('/pricing.html', '权益与收费', 'Credits and pricing'),
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
      '区域截图与智能框选',
      'Region capture and Smart Selection',
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
    blog: link('/blog/index.html', '博客', 'Blog'),
    changelog: link('/changelog.html', '更新日志', 'Changelog'),
    about: link('/about.html', '关于', 'About'),
  };
}

export function footerSections(locale: SiteLocale) {
  const links = siteLinks(locale);
  const shortLink = (link: SiteLink, zh: string, en: string): SiteLink => ({
    ...link,
    label: locale === 'zh' ? zh : en,
  });
  return [
    {
      title: locale === 'zh' ? '开始使用' : 'Get started',
      links: [
        links.download,
        shortLink(links.install, '安装与更新', 'Installation'),
        shortLink(links.quickStart, '快速上手', 'Quick start'),
        shortLink(links.shortcuts, '快捷键', 'Shortcuts'),
        links.pricing,
      ],
    },
    {
      title: locale === 'zh' ? '功能指南' : 'Feature guides',
      links: [
        shortLink(links.scrolling, '滚动截图', 'Scrolling capture'),
        shortLink(links.recognition, '文字识别', 'Text recognition'),
        shortLink(links.pinning, '桌面贴图', 'Pin to screen'),
        shortLink(links.recording, '屏幕录制', 'Screen recording'),
      ],
    },
    {
      title: locale === 'zh' ? '了解项目' : 'The project',
      links: [
        links.home,
        links.guides,
        links.blog,
        links.changelog,
        links.about,
      ],
    },
  ];
}
