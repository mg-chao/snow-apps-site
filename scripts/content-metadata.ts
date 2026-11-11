import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { dirname, relative, resolve, sep } from 'node:path';

const sourceExtensions = [
  '',
  '.ts',
  '.tsx',
  '.js',
  '.json',
  '/index.tsx',
  '/index.ts',
];

/** Use repository history, never checkout/build time, for unchanged sources. */
export function contentMetadata(root = process.cwd()) {
  const dates = new Map<string, string>();
  const dirty = new Set<string>();
  const git = (...args: string[]) =>
    execFileSync('git', args, {
      cwd: root,
      encoding: 'utf8',
      maxBuffer: 32 * 1024 * 1024,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  if (git('rev-parse', '--is-shallow-repository').trim() === 'true') {
    throw new Error(
      'SEO dates require full Git history. Fetch with --unshallow before building.',
    );
  }
  let date = '';
  for (const line of git(
    'log',
    '--format=@@%cI',
    '--name-only',
    '--',
    'docs',
    'theme',
  ).split(/\r?\n/)) {
    if (line.startsWith('@@')) date = line.slice(2);
    else if (line && date && !dates.has(line)) dates.set(line, date);
  }
  for (const file of [
    ...git('diff', '--name-only', '-z', 'HEAD').split('\0'),
    ...git('ls-files', '--others', '--exclude-standard', '-z').split('\0'),
  ])
    if (file) dirty.add(file);

  const key = (file: string) => relative(root, file).split(sep).join('/');
  const fileDate = (file: string) => {
    const name = key(file);
    const value = dirty.has(name)
      ? statSync(file).mtime.toISOString()
      : dates.get(name);
    return value ? new Date(value).toISOString() : undefined;
  };
  const resolveSource = (base: string) =>
    sourceExtensions
      .map((suffix) => `${base}${suffix}`)
      .find((file) => existsSync(file) && statSync(file).isFile());
  const dependencies = (
    file: string,
    seen = new Set<string>(),
  ): Set<string> => {
    if (seen.has(file) || !existsSync(file)) return seen;
    seen.add(file);
    if (!/\.(?:mdx?|[jt]sx?)$/.test(file)) return seen;
    const source = readFileSync(file, 'utf8');
    // Local source imports (including lazy imports) and public illustrations.
    const references = [
      ...source.matchAll(/(?:from\s*|import\s*\(?\s*)['"](\.[^'"]+)['"]/g),
      ...source.matchAll(/['"(](\/images\/[^'"\s)]+)['")]/g),
    ];
    for (const match of references) {
      const value = match[1];
      if (/\.css$/.test(value)) continue;
      const target = resolveSource(
        value.startsWith('/')
          ? resolve(root, 'docs/public', value.slice(1))
          : resolve(dirname(file), value),
      );
      if (target && !key(target).startsWith('../')) dependencies(target, seen);
    }
    for (const match of source.matchAll(
      /import\s*\{([^}]+)\}\s*from\s*['"]@rspress\/core\/theme['"]/g,
    )) {
      for (const symbol of match[1]
        .split(',')
        .map((name) => name.trim().split(/\s+as\s+/)[0])) {
        const target = resolveSource(resolve(root, 'theme/components', symbol));
        if (target) dependencies(target, seen);
      }
    }
    return seen;
  };
  return (file: string, isHome = false) => {
    const files = dependencies(file);
    // Shared visible navigation and structured metadata affect every page.
    for (const name of [
      'theme/index.tsx',
      'theme/site-structure.ts',
      'theme/seo.ts',
      'theme/components/SeoMetadata.tsx',
      'theme/components/SiteHeader.tsx',
    ]) {
      const target = resolve(root, name);
      if (existsSync(target)) files.add(target);
    }
    if (isHome)
      dependencies(
        resolve(root, 'theme/components/HomeLayout/index.tsx'),
        files,
      );
    if (key(file).includes('/blog/'))
      dependencies(resolve(root, 'theme/components/Blog/index.tsx'), files);
    const known = [...files]
      .map(fileDate)
      .filter((value): value is string => Boolean(value));
    const lastModified = known.sort((a, b) => Date.parse(b) - Date.parse(a))[0];
    const source = readFileSync(file, 'utf8');
    const image = source.match(/!\[[^\]]*\]\((\/images\/[^\s)]+)\)/)?.[1];
    return { lastModified, image };
  };
}
