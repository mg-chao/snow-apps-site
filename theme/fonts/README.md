# Self-hosted fonts

The theme loads Manrope and DM Mono from local WOFF2 files so visitors do not need
to connect to Google Fonts. These files are committed to the repository; installing
dependencies and building the site do not download fonts.

The assets were copied from these Fontsource npm packages, with their original
SIL Open Font License files:

- [@fontsource-variable/manrope 5.3.0](https://www.npmjs.com/package/@fontsource-variable/manrope/v/5.3.0)
  (`manrope-LICENSE.txt`): normal variable font, used at weights 400–800.
- [@fontsource/dm-mono 5.3.0](https://www.npmjs.com/package/@fontsource/dm-mono/v/5.3.0)
  (`dm-mono-LICENSE.txt`): normal fonts at weights 400 and 500.

`index.css` preserves the upstream Unicode ranges, so browsers request only the
subsets needed by the current text. Chinese characters use the existing system
font fallback. All faces use `font-display: swap` to show text while fonts load.
Rspress bundles the relative font URLs into hashed assets under `static/`, which
is already included in the website deployment.

To update, copy the corresponding WOFF2 files and licenses from a pinned package
version. Update the face declarations and version references together. Keep the
family name `Manrope` (the upstream variable package calls it `Manrope Variable`)
to match the existing theme styles, and retain only the WOFF2 sources.
