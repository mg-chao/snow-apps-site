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

The checkout must be clean. Before changing any source or publishing the site, the
workflow downloads `install-snow-shot-macos.sh` from the requested GitHub and Gitee
release and checks that both assets contain identical UTF-8 scripts with Bash
headers and LF line endings. Missing, unavailable, or mismatched installers stop
publication before the version is changed. The workflow then updates `releaseVersion` in
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

### Snow Shot Mini

Publish and verify the paired Snow Shot / Snow Shot Mini release on GitHub and Gitee
before deploying the website. Both editions use the same `releaseVersion` and
`v<version>_snow-shot` tag; there is no separate Mini website version to update.
The release must contain these Mini downloads:

| Platform | Release asset |
| --- | --- |
| Windows x64 installer | `snow-shot-mini-<version>-windows-x64-online.exe` |
| Windows x64 portable | `snow-shot-mini-<version>-windows-x64-portable.zip` |
| macOS Apple Silicon | `snow-shot-mini-<version>-macos-arm64.dmg` |

The English download page links directly to GitHub; the Chinese page links to Gitee.
Each platform has a Mini card with background `#f759ab`. Windows includes a
secondary portable download link. Mini has no offline installer or Intel Mac build.

The macOS download page also offers a terminal installation command for either
edition. Each release must include `install-snow-shot-macos.sh`; the command and
script link use the same release tag and language channel as the disk images.
The edition selector passes `--edition full` or `--edition mini`, and the page
language sets `--lang en` or `--lang zh-CN`. The script discovers and installs the
latest application release, verifies the package, and signs the app locally.

Run the same `scripts/publish-release.ps1 -Version <version>` workflow for both
editions. From the app repository, `scripts/publish-snow-shot-website.ps1` derives
the version from `SNOW_SHOT_VERSION`; `-DeployWebsite` on the app release publisher
runs this workflow after release publication. Commit the Mini website changes
before running either entry point.

Packaging and server-side staging require the full and Mini Windows download
anchors in both generated download pages to match the target version and language
channel. Public download pages are checked again after deployment. The macOS cards
are selected in the browser and covered by the download component tests.
An interrupted website deployment can be retried with the same version without
republishing the application packages. Existing Mini packages under `setup/` and
`latest-version-mini.json` are preserved alongside the full edition's files.

Run the focused deployment checks with
`python -m unittest discover -s tests -p test_deploy_website.py` and
`pwsh -File scripts/test-publish-release.ps1`.
Run the release installer checks with
`python -m unittest discover -s tests -p test_release_installer.py`.
To verify published assets without changing the website, run
`python scripts/deploy-website.py check-release-installer --version <version>`.
Run the download component and Terminal command checks with
`node --test tests/download-page.test.mjs tests/mac-install-option.test.mjs`
(Node.js 24 or later). The Terminal execution checks use system Bash on macOS or
Linux. Then run `bun run lint` and `bun run build`.
