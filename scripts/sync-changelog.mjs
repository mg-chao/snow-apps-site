import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const releaseSource = 'https://github.com/mg-chao/snow-shot/releases';
const releaseApi = 'https://api.github.com/repos/mg-chao/snow-shot/releases';
const defaultOutput = fileURLToPath(
  new URL('../theme/components/ChangelogPage/releases.json', import.meta.url),
);

const hasChinese = (value) => /[\u3400-\u9fff]/u.test(value);
const downloadHeading =
  /^(?:(?:choose your |choose a |recommended )?downloads?\b|install(?:ation)?\b|(?:quick )?macos (?:quick )?install\b|下载(?:指南|选择|指引)?|安装包选择|macOS\s*快速安装)/i;
const generatedHeading =
  /^(?:what['’]s changed|new contributors|changes since\b)/i;
const languageHeading =
  /^(?:中文|简体中文|chinese|english|en|zh|更新内容|what['’]s new)(?:\s*\/\s*(?:中文|简体中文|chinese|english|en|zh|更新内容|what['’]s new))?$/i;

function headingLanguage(heading) {
  if (
    /^(?:中文|简体中文|chinese|zh|更新内容|新功能与改进|问题修复)$/i.test(
      heading,
    )
  ) {
    return 'zh';
  }
  if (
    /^(?:english|en|what['’]s new|features and improvements|fixes)$/i.test(
      heading,
    )
  ) {
    return 'en';
  }
  return undefined;
}

function originalLanguage(value) {
  // URLs, HTML labels, and code identifiers are not evidence of English prose.
  const prose = value
    .replace(/https?:\/\/[^\s)]+/g, '')
    .replace(/`[^`]*`/g, '')
    .replace(/<[^>]*>/g, '');
  if (!hasChinese(prose)) return 'en';
  return /\b[A-Za-z]{3,}\s+[A-Za-z]{3,}\s+[A-Za-z]{3,}\b/.test(prose)
    ? 'mixed'
    : 'zh';
}

function sectionsOf(body) {
  const sections = [];
  let section = { heading: '', lines: [] };
  let fence;
  for (const line of body.replace(/\r\n?/g, '\n').split('\n')) {
    const nextFence = line.match(/^\s*(`{3,}|~{3,})/);
    if (nextFence) {
      if (!fence) fence = nextFence[1][0];
      else if (fence === nextFence[1][0]) fence = undefined;
    }
    const heading = !fence && line.match(/^(#{1,2})\s+(.+?)\s*#*\s*$/);
    if (heading) {
      sections.push(section);
      section = { heading: heading[2], lines: [line] };
    } else {
      section.lines.push(line);
    }
  }
  sections.push(section);
  return sections;
}

function cleanSection(section) {
  let lines = [...section.lines];
  if (/^Snow Shot(?:\s|$)/i.test(section.heading)) lines = lines.slice(1);
  if (languageHeading.test(section.heading)) lines = lines.slice(1);
  // Older releases use a bold paragraph instead of a download heading.
  // Remove that paragraph alone, preserving later notes and changelog links.
  let downloadParagraph = false;
  return lines
    .filter((line) => {
      if (/^\*\*(?:Downloads?\s*:?|下载选择|下载指南)\*\*[:：]?/i.test(line)) {
        downloadParagraph = true;
      }
      if (downloadParagraph && !line.trim()) downloadParagraph = false;
      return !downloadParagraph;
    })
    .join('\n')
    .trim();
}

function splitBilingualLines(value) {
  let splitCount = 0;
  const values = { zh: [], en: [] };
  for (const line of value.split('\n')) {
    // Split only the established prose separator, never slash characters in
    // links, paths, code, or English-only notes.
    const separator = proseSeparator(line);
    const left = line.slice(0, separator);
    const right = line.slice(separator + 3);
    if (
      separator >= 0 &&
      left.trim() &&
      !hasChinese(left) &&
      hasChinese(right)
    ) {
      const marker = left.match(/^(\s*(?:[-*+]|\d+[.)])\s+)/)?.[1] ?? '';
      values.en.push(left.trimEnd());
      values.zh.push(`${marker}${right.trim()}`);
      splitCount += 1;
    } else {
      values.en.push(line);
      values.zh.push(line);
    }
  }
  return splitCount
    ? { zh: values.zh.join('\n').trim(), en: values.en.join('\n').trim() }
    : undefined;
}

function proseSeparator(line) {
  let code;
  let brackets = 0;
  let parentheses = 0;
  for (let index = 0; index < line.length; index += 1) {
    if (line[index] === '`') {
      const delimiter = line.slice(index).match(/^`+/)[0];
      if (!code) code = delimiter;
      else if (code === delimiter) code = undefined;
      index += delimiter.length - 1;
      continue;
    }
    if (code) continue;
    if (line[index] === '[') brackets += 1;
    if (line[index] === ']') brackets = Math.max(0, brackets - 1);
    if (line[index] === '(') parentheses += 1;
    if (line[index] === ')') parentheses = Math.max(0, parentheses - 1);
    if (!brackets && !parentheses && line.startsWith(' / ', index))
      return index;
  }
  return -1;
}

export function extractReleaseNotes(body = '') {
  const sections = sectionsOf(body).filter(
    (section) => !downloadHeading.test(section.heading),
  );
  // GitHub-generated commit lists duplicate the authored summary. Releases
  // without an authored summary retain those lists as their actual notes.
  const hasSummary = sections.some(
    (section) =>
      !generatedHeading.test(section.heading) && cleanSection(section),
  );
  const retained = sections.filter(
    (section) => !hasSummary || !generatedHeading.test(section.heading),
  );
  const explicitLanguages = retained.some((section) =>
    headingLanguage(section.heading),
  );
  const notes = { zh: [], en: [] };
  for (const section of retained) {
    const value = cleanSection(section);
    if (!value) continue;
    const language = headingLanguage(section.heading);
    if (language) {
      notes[language].push(value);
      continue;
    }
    const bilingual = splitBilingualLines(value);
    if (bilingual) {
      notes.zh.push(bilingual.zh);
      notes.en.push(bilingual.en);
    } else if (explicitLanguages) {
      const language = originalLanguage(value);
      if (language === 'mixed') {
        notes.zh.push(value);
        notes.en.push(value);
      } else {
        notes[language].push(value);
      }
    } else {
      notes.zh.push(value);
      notes.en.push(value);
    }
  }
  const result = {
    zh: notes.zh.join('\n\n').trim(),
    en: notes.en.join('\n\n').trim(),
  };
  result.zh ||= result.en;
  result.en ||= result.zh;
  return {
    notes: result,
    notesLanguage: {
      zh: originalLanguage(result.zh),
      en: originalLanguage(result.en),
    },
  };
}

export function isPrerelease(release) {
  return (
    release.prerelease === true ||
    /(?:^|[-_])(?:alpha|beta|rc|dev|preview|canary)(?=$|[._\d-])/i.test(
      release.tag_name,
    )
  );
}

export function createSnapshot(releases, syncedAt = new Date().toISOString()) {
  if (!Array.isArray(releases)) {
    throw new Error('Expected a JSON array of raw GitHub releases.');
  }
  const seen = new Set();
  const normalized = [];
  for (const release of releases) {
    if (release.draft) continue;
    const tag = release.tag_name;
    // The repository also mirrors product releases with an explicit suffix.
    // Legacy Snow Shot tags have no product suffix; do not import other apps.
    if (
      typeof tag !== 'string' ||
      !/^v?\d+\.\d+\.\d+(?:$|[-_](?:snow-shot$|alpha|beta|rc|dev|preview|canary))/i.test(
        tag,
      )
    ) {
      continue;
    }
    if (seen.has(tag)) continue;
    if (
      typeof release.published_at !== 'string' ||
      !Number.isFinite(Date.parse(release.published_at)) ||
      typeof release.body !== 'string' ||
      typeof release.html_url !== 'string' ||
      !release.html_url.startsWith(`${releaseSource}/tag/`)
    ) {
      throw new Error(
        `Invalid release metadata for ${tag}. Existing snapshot preserved.`,
      );
    }
    seen.add(tag);
    normalized.push({
      tag,
      version: tag
        .replace(/^v/, '')
        .replace(/_snow-shot$/, '')
        .replaceAll('_', '-'),
      name: release.name || tag,
      publishedAt: release.published_at,
      url: release.html_url,
      prerelease: isPrerelease(release),
      ...extractReleaseNotes(release.body),
    });
  }
  if (!normalized.length)
    throw new Error('No published Snow Shot releases found.');
  normalized.sort(
    (left, right) =>
      Date.parse(right.publishedAt) - Date.parse(left.publishedAt),
  );
  return { source: releaseSource, syncedAt, releases: normalized };
}

export async function fetchReleases({ fetcher = fetch, token } = {}) {
  const releases = [];
  for (let page = 1; page <= 100; page += 1) {
    const response = await fetcher(`${releaseApi}?per_page=100&page=${page}`, {
      headers: {
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'snow-shot-site-changelog',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      signal: AbortSignal.timeout(30_000),
    });
    if (!response.ok) {
      throw new Error(
        `GitHub releases request failed (${response.status}, page ${page}). ` +
          'Try GITHUB_TOKEN or --input with a raw GitHub releases JSON export. Existing snapshot preserved.',
      );
    }
    const batch = await response.json();
    if (!Array.isArray(batch))
      throw new Error(`Invalid GitHub response on page ${page}.`);
    releases.push(...batch);
    if (batch.length < 100) return releases;
  }
  throw new Error(
    'GitHub pagination exceeded 100 pages; refusing to save an incomplete snapshot.',
  );
}

async function main(args) {
  let input;
  let output = defaultOutput;
  for (let index = 0; index < args.length; index += 1) {
    const flag = args[index];
    if (flag === '--help' || flag === '-h') {
      console.log(
        'Usage: bun run changelog:sync [--input releases.json] [--output snapshot.json]\nUses paginated GitHub releases; optionally set GITHUB_TOKEN. Builds use the checked-in snapshot without network access.',
      );
      return;
    }
    if ((flag === '--input' || flag === '--output') && args[index + 1]) {
      const value = args[++index];
      if (flag === '--input') input = value;
      else output = path.resolve(value);
    } else {
      throw new Error(`Unknown or incomplete option: ${flag}. Use --help.`);
    }
  }
  const releases = input
    ? JSON.parse(await readFile(path.resolve(input), 'utf8'))
    : await fetchReleases({ token: process.env.GITHUB_TOKEN });
  const snapshot = createSnapshot(releases);
  await mkdir(path.dirname(output), { recursive: true });
  // Write and validate everything before replacing the last working snapshot.
  const temporary = `${output}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(snapshot, null, 2)}\n`);
  await rename(temporary, output);
  console.log(
    `Synced ${snapshot.releases.length} Snow Shot releases to ${output}`,
  );
}

if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  main(process.argv.slice(2)).catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
