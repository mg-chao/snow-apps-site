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
