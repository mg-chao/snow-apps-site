---
title: Text recognition and cleanup
description: Extract editable text from screenshots, compare it with the original, correct recognition errors, adjust line breaks and punctuation, copy text, and troubleshoot OCR preparation or recognition failures.
---

# Text recognition and cleanup

Use **Text recognition** to turn error messages, scanned documents, or text in images into copyable text. Ordinary OCR runs locally; its components may need preparation on first use. Mini does not show Text recognition in the default screenshot toolbar. You can launch its main-window action, add it to the toolbar, or assign a separate shortcut. See [OCR models and offline preparation](./models.md).

![Text recognition: select clear text, compare the original, correct the result, and copy it](/images/guides/en/rec-text.svg)

*Instructional illustration. The three stages show the input area, recognized text, and a cleaned-up result.*

## Extract a passage

1. Display all the text you need. Start a screenshot with the configured shortcut—**F1** on Windows or **Control+1** on macOS by default—and drag a selection around the text. Include complete lines without cutting through characters.
2. Find **Text recognition** in the selection toolbar. If its group or position has changed, hover over icons to read their tooltips. Click it to enter recognition mode.
3. If “Preparing text recognition components” appears, stay online and wait for preparation to finish. Prepared components can recognize immediately. Check the result before copying it to another application.
4. To copy only a few lines, select them in the result. For the whole passage, clear the partial selection and use **Copy to clipboard** in the toolbar.

You can also launch OCR without assigning a separate shortcut. In the main window, enter “Text recognition” in **Search function** and choose the matching result. This locates the **Text recognition** action under **Global shortcuts**. Click the action row's title or empty area to start a screenshot; confirming the selection starts recognition directly. The dashed button showing a shortcut or “Not set” configures keys. Selecting a search result only locates the action; it does not launch recognition.

Do not repeatedly click while components are downloading. Use **Cancel screenshot** to end the session. Start again with a smaller, clearer selection if you need a different input.

## Compare and edit

Check digits, letter case, path separators, and similar-looking characters against the original. Verify commands, amounts, and account details before copying them.

1. Click **Show original image** in the recognition property bar to display a reference alongside the result; click again to toggle it. **Show original image preview** in settings controls the initial state.
2. Click **Edit**, locate a mistake in the editable result, and replace it. This changes the current recognition result, not the text in the source application.
3. Use **Undo** to reverse an edit or **Redo** to restore it. Keep focus in the current result so another application does not receive the shortcut.
4. Click **Reset** to discard text cleanup and return to the recognition result. Reset is different from capturing again; exit the screenshot and select a new area to change the source.

## Line breaks and punctuation

Use **Format** and **Punctuation** in the property bar to clean up recognized text. Choose an option and inspect the result. Clear it or choose “None” to stop that conversion. These tools do not proofread text or decide whether punctuation in a command should change.

| Option | Effect and use |
| --- | --- |
| None | Adds no corresponding layout or punctuation conversion; useful for retaining the recognition result |
| Keep line breaks | Keeps line boundaries for logs, addresses, and line-by-line lists |
| Remove line breaks | Joins continuous text that was visually wrapped; check paragraph boundaries after pasting |
| Smart typesetting | Uses relationships between recognized lines to organize paragraphs; still check headings and lists |
| Half-width | Converts supported punctuation to half-width forms; check again before using it in code |
| Full-width | Converts supported punctuation to full-width forms for suitable Chinese typesetting |

Set default formatting and punctuation under **Settings → Text recognition & translation → Recognition results**. Mini calls the settings page **Text recognition**. Defaults apply when editing or copying recognized text; test a short passage to confirm the output suits your task.

## Copy text and save an image

**Copy to clipboard** transfers the current text result to a text editor. Check the copy range when a partial text selection exists. Paste into the destination once to check for missing characters or unwanted line breaks.

Interpret **Save as file** together with the current result and output settings. **Save recognition results as an image** controls whether displayed recognition text is rendered into screenshot image exports. For editable text, copy into a text editor and save your own text file. For cell structure, use [Table recognition](./table.mdx).

## Text background and highlighting

Under **Settings → Text recognition & translation → Text background**—the **Text recognition** page in Mini—you can change how recognized text appears over the original:

- **Fill style** offers **Blur** and **Background fill**. Compare the same passage on a textured background and choose the more readable treatment. This is separate from annotation mosaic or blur filters.
- **Show text highlight** adds a mask around recognition results to emphasize the text. Compare it with the original; turn it off when that emphasis is unnecessary.

![Recognition text background: blur and background fill provide different display treatments](/images/guides/en/rec-background.svg)

*Instructional illustration. Compare two treatments for recognized-text backgrounds.*

Changing the display style does not correct recognition errors. Continue to compare the text before copying it or exporting a rendered image.

## Automatically act after recognition

To copy automatically or enter correction immediately, open **Settings → Screenshots → Interaction → Automatically execute after text recognition**. Select a behavior and try a short sample sentence. Existing custom settings can change the manual-copy workflow above.

| Option | After successful recognition |
| --- | --- |
| Do nothing | Keeps the result for manual checking, editing, or copying |
| Copy text | Copies recognized text and keeps the screenshot session open |
| Copy text and end screenshot | Copies text and ends the session so you can paste elsewhere |
| Copy text (global) | Copies automatically only when launched through the separate global Text recognition action; the ordinary screenshot-toolbar entry does not trigger this option |
| Copy text and end screenshot (global) | Copies and ends the session only through the separate global recognition entry |
| Enable edit mode | Enters text editing when the recognition result appears |

“Global” describes the **entry point**; it does not turn ordinary keys such as C into system-wide shortcuts. The separate **Copy after text recognition** action is itself designed to copy and end the screenshot. Choose it separately from ordinary toolbar recognition.

![Automatic actions after OCR: ordinary and global recognition entries can use different copy and exit behavior](/images/guides/en/rec-auto-action.svg)

*Instructional illustration. Choose Do nothing or Enable edit mode when you want to check text first.*

If the screenshot disappears after recognition, check whether a copy-and-end option is selected. If the behavior occurs only through the separate recognition action, check for a “global” option. Verify the clipboard before continuing so you do not use a previous result accidentally.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Components keep preparing | Check the network and proxy; finish initial preparation before going offline |
| Missing text or unexpected order | Use a smaller selection containing complete lines; enlarge text in the source application and capture again, then consider detection settings |
| A screenshot-over-4K warning | Reduce the recognition area or recognize sections instead of one extremely long image |
| Slow local recognition | Compare model size, detection scaling, and resident-process settings in OCR models and performance; change one setting at a time |
| A table becomes plain text | Use Table recognition; ordinary OCR does not replace structured cell editing |

Continue with [OCR models](./models.md), [Screenshot translation](../translation/screenshot.md), or [Text and annotations in pins](../pinning/text.md).
