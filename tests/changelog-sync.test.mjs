import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';
import {
  createSnapshot,
  extractReleaseNotes,
  fetchReleases,
  isPrerelease,
  releaseSource,
} from '../scripts/sync-changelog.mjs';

function release(tag, overrides = {}) {
  return {
    tag_name: tag,
    name: `Snow Shot ${tag}`,
    html_url: `${releaseSource}/tag/${tag}`,
    published_at: '2026-11-08T16:14:35Z',
    body: '- A useful improvement.',
    draft: false,
    prerelease: false,
    ...overrides,
  };
}

describe('release-note extraction', () => {
  it('keeps each explicit language and omits download and install sections', () => {
    const result = extractReleaseNotes(
      '# Snow Shot / Snow Shot Mini 1.5.2\r\n\r\n## 中文\r\n- **改进**：保留 `OCR`。\r\n\r\n## English\r\n- **Improved:** keep `OCR`.\r\n\r\n## 下载指南 / Download guide\r\nPackage table\r\n\r\n## macOS 快速安装\r\nInstaller command',
    );
    assert.deepEqual(result, {
      notes: {
        zh: '- **改进**：保留 `OCR`。',
        en: '- **Improved:** keep `OCR`.',
      },
      notesLanguage: { zh: 'zh', en: 'en' },
    });
  });

  it('does not lose later English notes when a download section comes between languages', () => {
    const result = extractReleaseNotes(
      '# Snow Shot 1.1.8\n\n## 新功能与改进\n- 新增贴图。\n\n## 安装包选择\nDownload packages\n\n## Features and improvements\n- New pinned images.\n\n## Fixes\n- Preserve drafts.\n\n## Downloads and verification\nChecksums',
    );
    assert.match(result.notes.zh, /新增贴图/);
    assert.match(result.notes.en, /New pinned images/);
    assert.match(result.notes.en, /Preserve drafts/);
    assert.doesNotMatch(result.notes.en, /packages|Checksums/);
    assert.doesNotMatch(result.notes.zh, /New pinned/);
  });

  it('splits bilingual bullets without corrupting inline code, links, or images', () => {
    const result = extractReleaseNotes(
      '- Use `OCR / PDF` with [the guide](https://example.com/a/b). / 支持 `OCR / PDF` 与[指南](https://example.com/a/b)。\n- ![Preview](https://example.com/a.png) / ![预览](https://example.com/a.png)',
    );
    assert.equal(
      result.notes.en,
      '- Use `OCR / PDF` with [the guide](https://example.com/a/b).\n- ![Preview](https://example.com/a.png)',
    );
    assert.equal(
      result.notes.zh,
      '- 支持 `OCR / PDF` 与[指南](https://example.com/a/b)。\n- ![预览](https://example.com/a.png)',
    );
    assert.deepEqual(result.notesLanguage, { zh: 'zh', en: 'en' });
  });

  it('marks the source language when a release has no translation', () => {
    const english = extractReleaseNotes('- Fixed screenshot history.');
    assert.equal(english.notes.zh, english.notes.en);
    assert.deepEqual(english.notesLanguage, { zh: 'en', en: 'en' });
    const chinese = extractReleaseNotes('1. 修复截图历史。');
    assert.equal(chinese.notes.en, chinese.notes.zh);
    assert.deepEqual(chinese.notesLanguage, { zh: 'zh', en: 'zh' });
  });

  it('removes bilingual wrapper headings without removing the translated bullets', () => {
    const result = extractReleaseNotes(
      "## What's new / 更新内容\n\n- Better capture. / 截图更顺手。",
    );
    assert.equal(result.notes.zh, '- 截图更顺手。');
    assert.equal(result.notes.en, '- Better capture.');
  });

  it('keeps generated notes when they are the only description, avoiding duplicate commit lists otherwise', () => {
    const generated =
      "## What's Changed\n- Fixed capture in https://github.com/mg-chao/snow-shot/pull/1";
    assert.match(extractReleaseNotes(generated).notes.en, /pull\/1/);
    const curated = extractReleaseNotes(`1. 修复截图。\n\n${generated}`);
    assert.equal(curated.notes.zh, '1. 修复截图。');
  });

  it('preserves unknown sections and headings inside code fences', () => {
    const result = extractReleaseNotes(
      '## Compatibility\nExisting notes.\n\n```md\n## Downloads\nExample heading, not a download section.\n```\n\n## More improvements\nAdditional notes.',
    );
    assert.match(result.notes.en, /Existing notes/);
    assert.match(result.notes.en, /Example heading/);
    assert.match(result.notes.en, /Additional notes/);
  });

  it('removes only a legacy bold download paragraph and preserves subsequent text', () => {
    const result = extractReleaseNotes(
      "## What's new\n- Better capture.\n\n**Downloads:** Installer details.\nContinued package details.\n\n[Full changelog](https://example.com/compare)\n\nMore release notes.",
    );
    assert.doesNotMatch(result.notes.en, /Installer details|Continued package/);
    assert.match(result.notes.en, /Full changelog/);
    assert.match(result.notes.en, /More release notes/);
  });
});

describe('release synchronization', () => {
  it('recognizes historical pre-release tags even when the GitHub flag is false', () => {
    for (const tag of [
      'v1.1.7-beta',
      'v0.1.3_beta_20250618',
      'v0.1.0_dev2025051302',
      'v1.6.0-rc1',
      'v1.6.0-alpha.1',
    ]) {
      assert.equal(isPrerelease(release(tag)), true, tag);
    }
    assert.equal(isPrerelease(release('v1.5.2_snow-shot')), false);
    assert.equal(isPrerelease(release('v1.5.2', { prerelease: true })), true);
  });

  it('excludes drafts and unrelated products, deduplicates tags, and sorts by publication time', () => {
    const old = release('v1.4.9_snow-shot', {
      published_at: '2026-11-06T16:19:34Z',
    });
    const snapshot = createSnapshot(
      [
        old,
        release('v1.5.2_snow-shot'),
        old,
        release('v2.0.0_snow-editor'),
        release('v1.6.0', { draft: true }),
      ],
      '2026-11-09T00:00:00Z',
    );
    assert.deepEqual(
      snapshot.releases.map((item) => item.version),
      ['1.5.2', '1.4.9'],
    );
    assert.equal(snapshot.source, releaseSource);
    assert.equal(snapshot.syncedAt, '2026-11-09T00:00:00Z');
    assert.throws(() => createSnapshot({}), /JSON array/);
    assert.throws(
      () => createSnapshot([release('v1.5.2', { published_at: 'invalid' })]),
      /Invalid release metadata/,
    );
  });

  it('fetches every page, including an empty page after a full final page', async () => {
    const urls = [];
    const result = await fetchReleases({
      fetcher: async (url) => {
        urls.push(url);
        return {
          ok: true,
          json: async () =>
            urls.length <= 2
              ? Array.from({ length: 100 }, () => release('v1.5.2'))
              : [],
        };
      },
    });
    assert.equal(result.length, 200);
    assert.equal(urls.length, 3);
    assert.match(urls[2], /per_page=100&page=3$/);
  });

  it('reports API failures without swallowing them or exposing credentials', async () => {
    await assert.rejects(
      fetchReleases({
        token: 'private-token-do-not-print',
        fetcher: async () => ({ ok: false, status: 403 }),
      }),
      (error) => {
        assert.match(error.message, /403.*page 1/);
        assert.match(error.message, /--input/);
        assert.doesNotMatch(error.message, /private-token/);
        return true;
      },
    );
  });

  it('imports raw API JSON offline and preserves the last snapshot on invalid input', async () => {
    const directory = await mkdtemp(path.join(os.tmpdir(), 'snow-changelog-'));
    try {
      const input = path.join(directory, 'raw.json');
      const output = path.join(directory, 'snapshot.json');
      const script = fileURLToPath(
        new URL('../scripts/sync-changelog.mjs', import.meta.url),
      );
      await writeFile(input, JSON.stringify([release('v1.5.2_snow-shot')]));
      const success = spawnSync(
        process.execPath,
        [script, '--input', input, '--output', output],
        { encoding: 'utf8' },
      );
      assert.equal(success.status, 0, success.stderr);
      const saved = await readFile(output, 'utf8');
      assert.equal(JSON.parse(saved).releases[0].version, '1.5.2');
      await writeFile(input, '{}');
      const failure = spawnSync(
        process.execPath,
        [script, '--input', input, '--output', output],
        { encoding: 'utf8' },
      );
      assert.equal(failure.status, 1);
      assert.equal(await readFile(output, 'utf8'), saved);
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  });
});
