import type { LlmsTxtContext } from '@rspress/core';
import { canonicalUrl, repositoryUrl, siteOrigin } from '../theme/seo.ts';

const guideSections = [
  {
    title: { en: 'Get started', zh: '开始使用' },
    pages: [
      '/download',
      '/guides/getting-started/install',
      '/guides/getting-started/quick-start',
      '/guides/index',
    ],
  },
  {
    title: { en: 'Core workflows', zh: '常用操作' },
    pages: [
      '/guides/capture/basics',
      '/guides/capture/scrolling',
      '/guides/annotations/basics',
      '/guides/recognition/text',
      '/guides/recognition/models',
      '/guides/recognition/table',
      '/guides/translation/screenshot',
      '/guides/pinning/image',
      '/guides/recording/start',
      '/guides/output/copy-save',
    ],
  },
  {
    title: { en: 'Troubleshooting', zh: '故障排查' },
    pages: [
      '/guides/getting-started/permissions',
      '/guides/settings/shortcuts',
      '/blog/ocr-troubleshooting',
      '/blog/scrolling-capture-fixes',
    ],
  },
  {
    title: { en: 'Releases and policies', zh: '版本与政策' },
    pages: ['/changelog', '/privacy', '/terms'],
  },
];

const copy = {
  en: {
    summary:
      'Snow Shot (SnowShot) is a free, open-source screenshot tool for Windows and macOS. It supports scrolling capture, annotation, local OCR, desktop pinning, and screen recording.',
    details:
      'The installation guide covers Full and Mini edition differences and platform requirements. Local OCR can run offline after setup. Some translation and recognition workflows use online services.',
    otherLanguage: '简体中文索引',
    otherLanguagePath: '/zh/llms.txt',
    otherLanguageDescription: 'Snow Shot 简体中文文档索引。',
    full: 'Full English documentation',
    fullDescription: 'All English site pages in one Markdown bundle.',
    repository: 'Source code on GitHub',
    repositoryDescription: 'Official Snow Shot repository and issue tracker.',
  },
  zh: {
    summary:
      'Snow Shot（SnowShot）是一款支持 Windows 和 macOS 的免费开源截图工具，提供滚动长截图、截图标注、本地 OCR 文字识别、桌面贴图与录屏。',
    details:
      '安装指南说明完整版与 Mini 的功能差异及系统要求。本地 OCR 完成配置后可离线使用，部分翻译与识别功能需要联网。',
    otherLanguage: 'English index',
    otherLanguagePath: '/llms.txt',
    otherLanguageDescription: 'Snow Shot documentation index in English.',
    full: '完整中文文档',
    fullDescription: '将全部简体中文站点页面汇总为一份 Markdown 文档。',
    repository: 'GitHub 源代码',
    repositoryDescription: 'Snow Shot 官方代码仓库与问题反馈入口。',
  },
};

export function renderLlmsTxt({ title, lang, sections }: LlmsTxtContext) {
  const locale = lang === 'zh' ? 'zh' : 'en';
  const prefix = locale === 'zh' ? '/zh' : '';
  const labels = copy[locale];
  const pages = new Map(
    sections.flatMap((section) =>
      section.pages.map((page) => [new URL(page.link).pathname, page]),
    ),
  );
  const output = [`# ${title}`, `> ${labels.summary}`, labels.details];

  for (const section of guideSections) {
    const links = section.pages.map((path) => {
      const page = pages.get(`${prefix}${path}.md`);
      if (!page?.description?.trim()) {
        throw new Error(
          `Missing llms.txt page or description: ${prefix}${path}`,
        );
      }
      // The HTML download page lets readers choose their OS and architecture.
      const url =
        path === '/download' ? canonicalUrl(page.routePath) : page.link;
      return `- [${page.title}](${url}): ${page.description.replace(/\s+/g, ' ').trim()}`;
    });
    if (section === guideSections[0]) {
      links.push(
        `- [${labels.otherLanguage}](${siteOrigin}${labels.otherLanguagePath}): ${labels.otherLanguageDescription}`,
      );
    }
    output.push(`## ${section.title[locale]}`, links.join('\n'));
  }

  output.push(
    '## Optional',
    [
      `- [${labels.full}](${siteOrigin}${prefix}/llms-full.txt): ${labels.fullDescription}`,
      `- [${labels.repository}](${repositoryUrl}): ${labels.repositoryDescription}`,
    ].join('\n'),
  );
  return `${output.join('\n\n')}\n`;
}
