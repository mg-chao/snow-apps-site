# Repository Guidelines

## Project Structure

- `docs/en/` and `docs/zh/` contain the English and Simplified Chinese Rspress pages; `docs/public/` contains published static assets.
- `theme/` contains React components, styles, and shared site logic. `rspress.config.ts` configures the site.
- `scripts/` contains build, SEO, asset, and release tooling; `tests/` contains Node.js and Python regression tests. `deploy/` contains server configuration.
- `doc_build/` is generated site output; `artifacts/` contains local reports and validation evidence. Both are ignored by Git.

## Tools and Development Commands

- Use Bun for package management and scripts. Run `bun install` to install dependencies and commit `bun.lock` when dependencies change.
- `bun run dev` starts the development server.
- `bun run build` generates the production site in `doc_build/`; `bun run preview` previews that build.

### Biome

- Run `bun run lint` to lint your code
- Run `bun run format` to format your code
- Follow `biome.json`: use space indentation and single quotes in JavaScript and TypeScript. Scope formatting to changed files when the working tree contains unrelated edits, for example `bun run format -- theme/components/DownloadPage/index.tsx`.

## Coding and Content Guidelines

- Match the surrounding TypeScript, React, and CSS conventions; reuse shared theme components and helpers.
- Keep corresponding English and Chinese pages, navigation, and user-visible component text aligned.
- Store published images and other site assets under `docs/public/`; keep local screenshots, research notes, and validation reports under `artifacts/`.
- Keep secrets and machine-specific configuration in ignored local files or environment variables. Commit sanitized `.env.example` or `.env.<name>.example` templates when needed.

## Validation

- Run only the tests related to the change. Run the full suite only when the user explicitly requests it.
- Node.js tests: `node --test tests/<feature>.test.mjs`. For example, download and platform changes use `node --test tests/download-page.test.mjs tests/platform.test.mjs`.
- Python tests: `python3 -m unittest discover -s tests -p 'test_<feature>.py'`.
- For changes affecting routes, page rendering, or SEO, run `bun run build` and `python3 scripts/check-seo-output.py` against the resulting build.
- Cover behavioral changes with focused regression tests; documentation-only or ignore-rule changes need relevant content and Git checks.

## Commit and Pull Request Guidelines

Follow the Conventional Commits style used in `../snow-apps`:

```text
<type>(<scope>): <summary>
```

- Use a lowercase type and an English imperative summary, starting with a lowercase verb, without a trailing period. Keep the subject concise, preferably within 72 characters.
- Omit `(<scope>)` for changes that span the project; otherwise use a short, lowercase feature or area such as `guides`, `download`, `changelog`, `seo`, `i18n`, `theme`, `deploy`, `release`, or `repo`.
- Types: `feat` for features, `fix` for bugs, `refactor` for restructuring, `perf` for performance, `test` for tests, `style` for formatting, `build` for dependencies/build/release tooling, `docs` for documentation, `ci` for CI configuration, and `chore` for repository maintenance.
- Describe the concrete change. Keep each commit focused on one purpose and exclude unrelated working-tree edits. Add a body when motivation or behavior needs explanation; reference related issues when available.
- Mark breaking changes with `!` after the type/scope and describe them in a `BREAKING CHANGE:` footer.

Examples:

```text
feat(guides): add recording tutorials
fix(download): preserve the selected architecture
docs(guides): clarify scrolling capture steps
build(release): update website to 1.5.2
chore(repo): improve ignore rules and contributor guidance
```

- PRs should explain the problem and resulting behavior, link related issues, and report formatting, lint, and relevant test results. Include screenshots for visual changes.

## Repository Hygiene

- Review `git status` and the staged diff before committing. Stage explicit paths when unrelated edits are present.
- Keep generated output, caches, local reports, and credentials out of commits. Keep source assets, shared `.agents/skills/`, `skills-lock.json`, and `bun.lock` under version control.
