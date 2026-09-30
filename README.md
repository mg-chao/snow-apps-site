# Rspress website

## Setup

Install the dependencies:

```bash
npm install
```

## Get started

Start the dev server:

```bash
npm run dev
```

Build the website for production:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

## Language selection

Unprefixed URLs use Chinese when the browser's regional locale is Chinese,
including Chrome and Edge configurations that report only `en-US` and `en` in
their language list while `Intl.DateTimeFormat().resolvedOptions().locale`
reports `zh-CN`. Otherwise, the first supported browser language wins, with
English as the fallback. Regional Chinese preferences such as `zh-CN` and `zh-TW`
use the Chinese pages. This is checked on every page load, including visits with
Rspress's old `rspress-visited` flag.

Choosing a language in the site's menu saves that preference for future visits.
Explicit `/zh/` URLs always stay Chinese. The redirect script runs in the HTML
head and preserves the path, query string, and fragment.

Run the language regression tests with `bun run test`.

## Release deployment

From PowerShell 7, publish the website for a Snow Shot release:

```powershell
& scripts/publish-release.ps1 -Version 1.1.8
```

The checkout must be clean. The workflow updates `releaseVersion` in
`theme/components/DownloadPage/releaseLinks.ts`, commits a version change when needed,
pushes the current branch to `origin`, and verifies the remote commit before running
`bun run build`. An already matching version reuses its existing commit.

The default destination is `root@120.79.232.67:/var/www/html`, using the local OpenSSH
configuration and trusted host keys. `IdentityFile`, `KnownHostsFile`, `ServerPort`,
`RemoteWebRoot`, and `PublicBaseUrl` can be overridden. `-WhatIf` previews the operation.

Only the generated pages, icons, `static/`, `images/`, and `zh/` are replaced.
Downloads in `setup/`, `npm/`, `plugins/`, legacy update feeds, and all other paths
are preserved. Previous website files remain in `/var/www/snow-shot-website-backups/`.
The deployment verifies SHA-256 for the archive and every file, rolls back file
replacement errors, and checks the public receipt and English/Chinese pages.
The receipt at `/website-release.json` records the release version and website commit.

Run the focused deployment checks with
`python -m unittest discover -s tests -p test_deploy_website.py` and
`pwsh -File scripts/test-publish-release.ps1`.
