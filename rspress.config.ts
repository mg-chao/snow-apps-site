import { readFileSync } from 'node:fs';
import * as path from 'node:path';
import { defineConfig } from '@rspress/core';
import { seoBuildPlugin } from './scripts/seo-build';
import { siteOrigin } from './theme/seo';

export default defineConfig({
  root: path.join(__dirname, 'docs'),
  title: 'Snow Shot',
  siteOrigin,
  plugins: [seoBuildPlugin()],
  description:
    'Snow Shot is a free, open-source screenshot tool for Windows and macOS with annotation, scrolling capture, local text recognition, pinning and screen recording.',
  lang: 'en',
  icon: '/app-icon.ico',
  mediumZoom: {
    // Linked images are controls; clicking them should follow the link.
    selector: '.rspress-doc img:not(a img)',
  },
  route: {
    // Our redirect checks every visit and handles Chromium's Chinese regional
    // locale even when its content-language list contains only English.
    localeRedirect: 'never',
  },
  builderConfig: {
    html: {
      tags: [
        {
          tag: 'script',
          attrs: {
            id: 'snow-shot-locale-debug',
            'data-revision': 'locale-debug-4',
          },
          children: readFileSync(
            path.join(__dirname, 'scripts/locale-debug.js'),
            'utf8',
          ),
          append: false,
        },
        {
          tag: 'script',
          attrs: { id: 'snow-shot-locale', 'data-revision': 'locale-debug-4' },
          children: readFileSync(
            path.join(__dirname, 'scripts/locale-redirect.js'),
            'utf8',
          ),
          append: false,
        },
      ],
    },
  },
  logo: {
    light: '/app-icon.svg',
    dark: '/app-icon.svg',
  },
  locales: [
    {
      lang: 'en',
      label: 'English',
      title: 'Snow Shot',
      description:
        'Snow Shot is a free, open-source screenshot tool for Windows and macOS with annotation, scrolling capture, local text recognition, pinning and screen recording.',
    },
    {
      lang: 'zh',
      label: '简体中文',
      title: 'Snow Shot',
      description:
        'Snow Shot（SnowShot）是免费开源截图工具，支持 Windows 和 macOS，提供截图标注、滚动长截图、本地文本识别、贴图与录屏。下载和使用指南均可从官方 GitHub 仓库获取。',
    },
  ],
  themeConfig: {
    darkMode: true,
    socialLinks: [
      {
        icon: 'github',
        mode: 'link',
        content: 'https://github.com/mg-chao/snow-apps',
      },
    ],
  },
});
