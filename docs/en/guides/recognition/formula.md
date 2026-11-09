---
title: LaTeX formula recognition
description: Extract LaTeX source from a screenshot, choose dedicated or vision models, correct symbols and scripts with a formula preview, copy or save text, and resolve recognition or rendering errors.
---

# LaTeX formula recognition

Use **LaTeX formula recognition** to turn a formula in a paper or slide into source for a LaTeX-capable editor. A preview helps you check scripts, fractions, and brackets. This feature requires Full and an available recognition service.

![Formula recognition: convert a formula image to source, edit a denominator, and inspect the rendered result](/images/guides/en/rec-formula.svg)

*Instructional illustration. Source and preview represent the same result. Check which syntax your destination expects.*

## Obtain formula source

1. Capture one complete formula—**F1** on Windows or **Control+1** on macOS by default. Include scripts, fraction bars, integral limits, and brackets at both ends.
2. Choose **LaTeX formula recognition** in the screenshot toolbar and wait for processing.
3. Under **Recognition model**, choose the **LaTeX-specific model** or an available vision model. Prepare a model that actually supports images in [Service configuration](../translation/services.md) before choosing a vision model.
4. Compare the returned source and formula preview with the original. If the dedicated model reports an input larger than 4K, capture a single formula or a smaller area.

## Correct and preview

Edit the **LaTeX formula source** area; the preview renders again after content changes. Find the smallest error first—for example, `x_1` recognized as `x_l`, or a missing brace—and change that part to make the effect easier to assess.

- Incorrect fractions: check both brace groups in `\frac{...}{...}`.
- Incorrect script ranges: enclose content that belongs together after `_` or `^` in braces.
- Correct recognition but an unexpected preview: read the preview message. The built-in renderer may differ from your destination LaTeX editor; copy the source there to check.

**Undo** and **Redo** restore source edits without resubmitting the image for recognition. **Show original image** checks the input image; the formula preview checks the current source.

## Copy and save

1. To use the whole formula, clear partial selections and click **Copy to clipboard**. For a subexpression, select its source and copy it.
2. Paste into the inline or display-math environment required by the destination. A correct Snow Shot preview does not put that application into formula mode.
3. Use **Save as file** to retain a **.txt** source file. Choose a folder and name; you can edit the formula text later in a text editor.

## Troubleshooting

| Message or symptom | Next step |
| --- | --- |
| Cannot preview this formula; check the LaTeX source | Check paired brackets, commands, and unclosed structures; undo recent edits gradually to locate the problem |
| Formula preview limit exceeded | Shorten the formula to the needed portion; handle complex content in the destination editor |
| Formula renderer unavailable | Copy the source to your formula tool first; restart the application and retry the preview |
| Recognition service or model unavailable | Check configuration, choose another available model, and use **Retry** |
| Multiple formulas or missing scripts | Capture one complete formula again, enlarging it in the source application first |

Continue with [Table recognition](./table.mdx), [Image conversion](./image-conversion.md), or [Translation services and custom models](../translation/services.md).
