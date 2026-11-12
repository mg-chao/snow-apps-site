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

## Image optimization

Website bitmaps use lossless WebP with maximum encoder effort (`method=6`,
`quality=100`, `exact=True`). Pixel dimensions, RGBA pixels and transparency are
verified after encoding. Pure vector SVGs and the ICO favicon keep their formats;
bitmaps embedded in SVGs are optimized too. Existing WebP files are replaced only
when the new encoding is smaller.

To optimize new PNG/JPEG assets and update their references in docs and theme files:

```bash
python3 -m pip install Pillow
python3 scripts/optimize-images.py
```

Original guide evidence records retain their source filenames; the consolidated
asset registry resolves converted files to their current WebP paths.

## Language selection

Every URL keeps its language: unprefixed pages are English and `/zh/` pages are
Chinese, for both visitors and crawlers. Browser preferences and saved choices
never automatically redirect a visit. When a supported preference differs from
the page language, a dismissible prompt offers the corresponding translated page.
Switching preserves the page path, query parameters and fragment.

An explicit choice in the language menu or prompt is remembered when storage is
available. Choosing to keep reading saves the current language and dismisses the
prompt. Visits alone do not save a preference. Chinese regional locales are also
recognized when Chromium reports only English content languages. The prompt
handles unavailable preference storage and keeps choices in memory while the
current page remains open.

Run the language regression tests with `bun run test`.

## Privacy policy

The English and Simplified Chinese policies live in `docs/en/privacy.md` and
`docs/zh/privacy.md`. They build to `/privacy.html` and `/zh/privacy.html`, and the
footer links to the policy in the current language. The app's About page uses
`https://snowshot.top/privacy.html`; the website's usual language selection applies.

Keep both languages aligned when data handling changes. Publisher review notes
and Store submission instructions stay in the app repository. They are not public
website content. The deployment workflow requires both privacy pages, includes
them in its file checks and backups, and checks their public URLs after deployment.

## Terms of service

The English and Simplified Chinese terms live in `docs/en/terms.md` and
`docs/zh/terms.md`. They build to `/terms.html` and `/zh/terms.html`, and the
footer links to the terms in the current language. The deployment workflow
requires both pages, includes them in its file checks and backups, and checks
their public URLs after deployment.

## Download platform selection

The download page supports Windows x64, Windows ARM64, macOS Apple silicon
(ARM64), and macOS Intel (x64). Both Windows architectures offer full online,
offline, and portable packages, plus Mini online and portable packages. Intel
Macs offer the full edition only; Mini on macOS requires Apple silicon.
Intel disk images use the release asset suffix `macos-x86_64.dmg`.

Windows x64 also offers an official Microsoft Store badge for the full edition,
localized to the page language and matched to the site's light/dark theme. The
SVG artwork in `docs/public/images/microsoft-store-*.svg` comes from
`https://get.microsoft.com/images/` (`en-us` and `zh-cn`, light and dark variants),
as documented in [Microsoft's HTML-only badge example](https://github.com/microsoft/app-store-badge#html-only).
Only nonvisual accessibility titles are added to the assets.
Linked images are excluded from Rspress image zoom so the badge acts as a download link.
Clicking the badge downloads `Snow Shot Installer.exe` directly from Microsoft's installer
endpoint for product `9NRTJ1GBX69V`; running it installs Snow Shot through the
Store, which manages subsequent updates. This link is independent of the
GitHub/Gitee release version and is configured in
`theme/components/DownloadPage/releaseLinks.ts`.

The homepage carries the detected OS and architecture to the download page.
Browser CPU client hints take priority over legacy user-agent CPU tokens.
`MacIntel` and `Intel Mac OS X` are not proof of an Intel CPU: Apple silicon
browsers can report the same values. When CPU information is unavailable, the
page starts with Windows x64 or macOS ARM64 and explains how to check the chip.
The system selector always offers all four targets.

Explicit links such as `/download?os=windows&arch=arm64` and
`/zh/download?os=macos&arch=x64` override detection. The selector saves both
parameters in the URL while preserving other query parameters and fragments;
late browser hints do not overwrite a manual choice. Existing OS-only links
continue to work. The macOS terminal script detects the actual Mac architecture
itself, and the Intel page does not offer a Mini command.

Run the focused detection and download checks with
`node --test tests/platform.test.mjs tests/download-page.test.mjs`.

## Changelog

The English and Simplified Chinese changelogs are available at `/changelog.html`
and `/zh/changelog.html`. Both use the checked-in GitHub Releases snapshot in
`theme/components/ChangelogPage/releases.json`, so builds and page visits do not
depend on the GitHub API.

Refresh the snapshot before building for a new app release:

```bash
bun run changelog:sync
```

The sync command fetches every public release page, excludes drafts and unrelated
product tags, and sorts by `published_at`. Historical `alpha`, `beta`, `rc`, and
`dev` tags count as previews even when GitHub's `prerelease` flag is false.
Authored Chinese/English notes are used where available; untranslated historical
notes retain their original language. Download instructions and duplicate
generated commit lists are omitted when an authored summary is present. Original
GitHub release links remain available for full context and historical assets.

If GitHub rate-limits the request, set `GITHUB_TOKEN` in the environment. An offline
import is also supported: export all pages of the raw GitHub Releases API as one
JSON array, then run:

```bash
bun run changelog:sync --input /absolute/path/releases.json
```

Review and commit the resulting snapshot together with the website changes. A
failed sync preserves the previous snapshot. Run the extraction, pagination,
offline-import, and failure-preservation checks with
`bun test tests/changelog-sync.test.mjs`.

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

Only the generated pages, icons, `static/`, `images/`, `guides/`, `zh/`,
`robots.txt`, `sitemap.xml`, `seo-manifest.json`, and `indexnow.txt` are replaced.
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
| Windows ARM64 installer | `snow-shot-mini-<version>-windows-arm64-online.exe` |
| Windows ARM64 portable | `snow-shot-mini-<version>-windows-arm64-portable.zip` |
| macOS Apple Silicon | `snow-shot-mini-<version>-macos-arm64.dmg` |

The English download page links directly to GitHub; the Chinese page links to Gitee.
Windows and Apple silicon Macs have a Mini card with background `#f759ab`.
Windows includes a secondary portable download link. Mini has no offline
installer or Intel Mac build.

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

## Search discoverability

The official source and complete user guides live in
[mg-chao/snow-shot](https://github.com/mg-chao/snow-shot). Keep the website's
English and Chinese guide hubs useful and link each topic to that repository.
Use the real product category in page titles and headings; avoid keyword lists,
unsupported comparisons, fabricated ratings, or promises about search position.

`theme/components/SeoMetadata.tsx` supplies self-canonical URLs, the default
language alternate, social metadata, homepage SoftwareApplication/WebSite data,
and BreadcrumbList data for inner pages. Blog articles also have BlogPosting
metadata with their real publication date, modification time, Snow Apps author
link and first instructional image. These match the visible article information;
no review scores are generated. `theme/site-structure.ts` defines the
shared bilingual links used by homepage shortcuts, the grouped footer, and
visible breadcrumbs and feature tutorial links. Navigation and sidebar labels
are checked against the same definitions to prevent inconsistent link names.
Guide breadcrumbs link to the actual manual hub rather
than directory URLs without a page. Feature links use specific tutorial names.
Rspress supplies the English/Chinese alternate links; the component updates
them on client-side navigation. The existing `.html` routes remain canonical.
`scripts/seo-build.ts` generates the sitemap from actual routes. `lastmod` and
blog `dateModified` use the latest Git date for the page source, its imported
content components and referenced illustrations. Shared navigation and SEO
implementation files do not supply a date. For a significant change to a page's
generated content or structured data from shared code, add
`updated: 'YYYY-MM-DD'` to the affected page. Local edits use the edited file's
mtime. Use a full Git checkout (`git fetch --unshallow` if necessary).

`seo-manifest.json` fingerprints rendered content and referenced images. IndexNow
comparison ignores executable bundle/style hashes and blog update dates. It
still detects article text, illustrations and other schema changes. The deployment
workflow validates all generated pages with `scripts/check-seo-output.py` before
uploading, including canonical/alternate links, descriptions, visible breadcrumbs,
site naming, internal link reachability from both homepages and discovery files.

Google selects sitelinks automatically; no structured-data field forces them.
Keep important pages directly linked with clear names, and keep page titles and
headings descriptive. After deployment, submit `/sitemap.xml` in Google Search
Console and request indexing for changed key pages. Check the indexed/rendered
HTML there; a submitted sitemap or a successful crawl does not guarantee sitelinks.
See [Google's sitelink guidance](https://developers.google.com/search/docs/appearance/sitelinks).

`deploy/nginx-seo-redirects.conf` consolidates extensionless and directory aliases
with HTTP 301 and preserves query parameters used by download selection.
Nested guide/blog aliases redirect only when their canonical `.html` file exists.
Missing documents stay 404 and routes outside these directories are untouched.
Install it as `/etc/nginx/snowshot-seo-redirects.conf` and include it only inside
the HTTPS `snowshot.top` server block. Back up both files before changes, run
`nginx -t` before reload, and restore the backups if validation or reload fails.
The normal content deployment preserves this server configuration.

`deploy/nginx-www-redirect.conf` redirects HTTP and HTTPS requests from
`www.snowshot.top` to `https://snowshot.top`, preserving the path and query string.
The `www` DNS record must point to the website server. Install this standalone
server block as `/etc/nginx/sites-available/www.snowshot.top.conf` and enable it
with a matching symlink in `/etc/nginx/sites-enabled/`. It reuses the main site's
certificate under `/etc/nginx/ssh_keys/snowshot.top/`; that certificate must cover
both `snowshot.top` and `www.snowshot.top` whenever it is renewed or replaced.
Back up any existing configuration, run `nginx -t` before reload, and restore the
backup if validation or reload fails. Verify a URL such as
`https://www.snowshot.top/download.html?os=windows` returns HTTP 301 with
`Location: https://snowshot.top/download.html?os=windows`. Normal website releases
preserve this configuration as well.

The production release workflow snapshots the live SEO manifest before uploading,
then submits added, changed and deleted canonical URLs to IndexNow only after
the release receipt and public page checks pass. On the first upgrade it obtains
the baseline from the live sitemap, HTML and referenced images. Older manifests
are supplemented from the live blog pages. The key and newly deployed manifest
must match. Removed URLs must return 301/308/404/410. No-change releases skip the
notification. Network failures, 429 and transient 5xx responses get at most three
attempts with bounded backoff and Retry-After handling. A failed notification
warns without rolling back the successful deployment. Snapshots and receipts
remain under ignored `artifacts/indexnow/<transaction>/` for diagnosis and retry.

For a manual deployment (Node.js 24+), capture the baseline **before** replacing
the website, then submit **after** verifying it:

```sh
bun run indexnow snapshot --output artifacts/indexnow/previous.json
# Deploy and verify the production build, then:
bun run indexnow submit --previous artifacts/indexnow/previous.json --current doc_build/seo-manifest.json --receipt artifacts/indexnow/receipt.json
```

For a failed release notification, rerun `submit` using that transaction's saved
`previous.json`, `current.json` and `receipt.json`; the live-manifest check refuses
a stale build. `docs/public/indexnow.txt` is a public verification key, not an
account secret. HTTP 200/202 acknowledges receipt, not indexing or ranking.
Keep Google Search Console and Bing Webmaster Tools sitemap submissions current.

Markdown images get intrinsic width/height during compilation. The first content
image stays eager; later images are lazy and decoded asynchronously. Home, About
and Download components are imported by their MDX routes, preserving full static
HTML while keeping their code out of the common theme bundle. Decorative snow
pauses outside the viewport/in background tabs and respects reduced motion.
The primary Latin font is preloaded with anonymous CORS to reduce font-swap layout shifts.

Focused checks:

```sh
node --test tests/seo.test.mjs tests/seo-pipeline.test.mjs tests/blog.test.mjs
bun run build
python scripts/check-seo-output.py
python scripts/check-blog-site.py
# Uses an isolated official Nginx container when Docker is available:
python -m unittest discover -s tests -p test_seo_redirects.py
```

After deployment, check representative aliases, canonical pages, sitemap and
robots URLs. Review Bing impressions/clicks and branded/category queries over
time; use the app repository's `docs/guide/MAINTAINING.md` for the baseline and
documentation maintenance checklist.


## 博客维护

文章位于 `docs/zh/blog/` 与 `docs/en/blog/`，两语使用相同 slug。每个主题只计一篇；列表、分类、日期和相关文章由 Rspress 的页面元数据自动生成，无须另维护文章清单。

新增第 11 篇时：

1. 在两个语言目录各新增一个 `.mdx`，写入 `title`、`description`、`blog: true`、真实撰写日期 `date: 'YYYY-MM-DD'`、`category: releases` 或 `answers`、`productVersion`、`platforms` 和 `related: [其他文章的slug]`。版本解读另加含时区的真实 `releaseDate`；答疑正文只保留影响操作的兼容条件。不要把历史产品发布日期当作文章日期。
2. 使用 `sidebar: false`，保留普通文档布局和正文 H1，Rspress 自动提供文章目录。列表摘要直接取 description；页头和相关文章由主题自动插入。
3. 正文提供入口、操作、预期结果、失败后的下一步和反馈信息。截图窗口已有的功能优先在那里展示。至少三张有教学作用的图，至少一张为真实应用截图或实际输出；示意图简短标注“操作示意”。英文使用对应英文图示，中文界面截图提供必要的控件名称对照。
4. 新素材放 `docs/public/images/blog/`；位图按 `scripts/optimize-images.py` 的无损 WebP 参数处理，并核对解码像素。保留来源、版本、裁剪范围与文章映射到 `artifacts/blog-sources.md`；不在正文加入源码、制作或验收细节。小型流程图可参考 `scripts/generate-blog-diagrams.py`。
5. 执行 `bun run format -- <本次修改的代码文件>`、`bun run lint`、`bun run build`、`node --test tests/blog.test.mjs tests/seo.test.mjs`、`python3 -m unittest discover -s tests -p 'test_deploy_website.py'`、`python3 scripts/check-seo-output.py` 和 `python3 scripts/check-blog-site.py`。再检查两语、手机/桌面、浅色/深色、分类、搜索和语言切换。

博客沿用 `.html` canonical：英文 `/blog/slug.html`、中文 `/zh/blog/slug.html`，列表为各自 `/blog/index.html`。博客目录纳入网站打包、完整性校验和目录回滚；本地验收不运行发布或部署命令。调查、实施与交付证据分别维护在 `artifacts/blog-plan.md`、`artifacts/blog-sources.md`、`artifacts/blog-delivery.md`。
