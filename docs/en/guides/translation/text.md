---
title: Text translation
description: Enable the translation page, type or paste text, select languages and services, inspect automatic translations, swap languages, copy results, and retry service errors.
---

# Text translation

For copyable text, type or paste directly into **Translation** in the main window. Changes to input and language settings automatically start translation. This page requires Full and the translation extension enabled.

![Text translation: choose source and target languages and a service, enter text, wait, and copy the translation](/images/guides/en/tr-text.svg)

*Instructional illustration. Edit the source; use the result area to read, select, and copy translations.*

## Open the translation page

1. Open **Settings → Text recognition & translation → Translation extensions** in the main window.
2. Enable **Translation page**, then enter **Translation** from the sidebar. This also enables the Translate selected text action. The initial configuration has it disabled.
3. To send recognized screenshot text here, also enable **Jump to translation page**. A button with that name then appears in the recognition property bar.

If the page is absent, check that the switch is enabled and you are using Full. Configuring a service alone does not enable the page. Mini does not include this extension.

## Enter text and change languages

1. Select **Source language**, **Target language**, and **Translation service** at the top. Choose **Detect language automatically** if the source is uncertain.
2. Type or paste complete sentences into **Source text**. Pause typing and wait for the result area's processing state and translation. There is no separate Start translation button to find.
3. Correcting the source, changing the target, or changing the service triggers processing again. Wait for the current result to update before comparing it with the source.
4. For reverse translation, specify a source language and use **Swap languages**. Swapping is unavailable with automatic source detection or identical source and target languages.

Finish composing input-method text before checking the translation; continuous typing delays the current request. The translation area displays results. To revise wording, change the source and translate again, or copy into your own editor.

## Copy and retry

Click **Copy translated text** after a result appears, then paste into the destination. For part of the source or translation, select text and use ordinary copying. With a selection, normal copying retains that range; without one, the page's copy shortcut retrieves the full translation.

The standalone translation window's action menu offers **Copy** and **Copy and close**, showing shortcuts for the current platform. Copy and close puts the translation on the clipboard and closes that window. Keep it open if you want to compare services.

For an error, read the result-area message, check configuration and connectivity, then click **Retry**. Re-entering text or changing languages or services also starts another request. Do not repeatedly clear a long source passage before resolving the error.

Leaving or closing the main translation page may clear the current session. Copy source text and translations into a document first if you need to keep them.

Continue with [Selected-text translation](./selected-text.md), [Screenshot translation](./screenshot.md), or [Translation services and custom models](./services.md).
