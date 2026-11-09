---
title: Translate selected text
description: Enable the translation page and selected-text action, retrieve selections from other applications, choose the main page or a standalone window, and resolve macOS permissions, empty selections, or retrieval failures.
---

# Translate selected text

**Translate selected text** sends an existing selection from another application to Snow Shot, useful while reading a browser or document. It reads text selections; for unselectable text in images, use [Screenshot translation](./screenshot.md). This feature requires Full.

![Selected-text translation: retain an external application's selection, invoke the action, and use the main page or standalone window](/images/guides/en/tr-selected.svg)

*Instructional illustration. Retrieving text and translating it are successive steps; successful retrieval still needs an available service.*

## Enable the action

1. Open **Settings → Text recognition & translation → Translation extensions** and enable **Translation page**. This switch controls both the page and selected-text action.
2. Under **Settings → Global shortcuts**, find **Translate selected text**, assign a combination that does not conflict with other applications, and note the keys shown in settings.
3. Return to an application with selectable text, select a short ordinary passage, and test the new shortcut. Confirm retrieval and translation work before using longer text.

## Translate a selection

Select a complete sentence in the source application, **keep its current text selection**, and press the translation shortcut directly. Clicking Snow Shot's main window first may lose the source selection.

Retrieved text appears in the source area of the translation page or standalone window, then translates automatically. Check the source is complete before reading the result. For missing text, select again in the source application or manually copy the complete passage into the translation page.

In the destination, change the target language or service, or edit the source to translate again. Click **Copy translated text** when ready, or select and copy only the part you need.

## Choose a standalone window

Enable **Standalone translation window** under **Text recognition & translation → Translation extensions** to send selections to a separate window. Disable it to use the main translation page. The standalone window still depends on the Translation page master switch.

Its action menu includes **Copy** and **Copy and close**. Check the translation, then use Copy and close to return to reading. Copy anything you need to retain before closing.

## If text cannot be retrieved

On macOS, native retrieval tries Accessibility first and uses a clipboard fallback where applicable. Grant Snow Shot the required **Accessibility** permission in System Settings, then select the source again. Permission does not guarantee every application exposes its text selection.

Other platforms attempt clipboard retrieval, so the source application must respond to ordinary text copying. Protected fields, specialized canvases, and images without real text selections may provide no content.

| Symptom | Action |
| --- | --- |
| The translation window opens with an empty source | Reselect a short sentence, retain source focus, and invoke again; or copy and paste manually |
| Retrieved text is incomplete | Check the source selection and avoid ranges crossing controls that cannot be copied |
| Text arrives but no translation appears | Retrieval succeeded; check the service, network, or model error, then click **Retry** |
| The shortcut does nothing | Check the Translation page switch and binding; choose a nonconflicting combination |
| The screen contains only text in an image | Use Screenshot translation rather than trying to create a text selection on the image |

Continue with [Text translation](./text.md), [Screenshot translation](./screenshot.md), or [Translation services and custom models](./services.md).
