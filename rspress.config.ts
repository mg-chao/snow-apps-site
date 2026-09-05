import * as path from 'node:path';
import { defineConfig } from '@rspress/core';

export default defineConfig({
  root: path.join(__dirname, 'docs'),
  title: 'Snow Shot',
  description:
    'Snow Shot is a cross-platform screenshot and screen recording tool with annotation and text recognition.',
  lang: 'en',
  icon: '/app-icon.ico',
  route: {
    localeRedirect: 'auto',
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
        'Snow Shot is a cross-platform screenshot and screen recording tool with annotation and text recognition.',
    },
    {
      lang: 'zh',
      label: '简体中文',
      title: 'Snow Shot',
      description:
        'Snow Shot 是一款跨平台的截图与录屏工具，支持标注和文字识别。',
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
