---
title: Convert images to Markdown and HTML
description: Use vision models to turn screenshot headings, paragraphs, and tables into Markdown or HTML, check previews and copy ranges, save documents with source text, and resolve model or network errors.
---

# Convert images to Markdown and HTML

Use **Convert to Markdown** or **Convert to HTML** to reorganize image content containing headings, paragraphs, lists, and tables. A vision model generates the result; check its text and structure before using it in a finished document. Both tools are available in Full, not Mini.

![Image conversion: choose Markdown or HTML for the same document and obtain a document plus source text](/images/guides/en/rec-conversion.svg)

*Instructional illustration. The example compares formats; models do not necessarily preserve the entire original layout.*

## Prepare a vision model

Configure a model under **Settings → Network & connections → Custom AI models**, enable **Vision support**, and confirm that the actual server model accepts images. Enabling the option makes a model selectable for relevant features; it does not change the remote model itself. See [Translation services and custom models](../translation/services.md) for individual fields.

Conversion sends the selected image to the chosen model service. Make sure that service is reachable. Image conversion works separately from local OCR and needs its own model-service setup.

## Run a conversion

1. Capture the document area—**F1** on Windows or **Control+1** on macOS by default. Include complete paragraphs and table boundaries; exclude nearby navigation, advertising, and other articles.
2. Choose **Convert to Markdown** or **Convert to HTML** in the screenshot toolbar. Markdown suits notes and repository documentation; HTML suits web-document structure.
3. To change models, click **Settings** in the result property bar, choose a prepared model under **Image conversion settings → Vision model**, and click **OK**. Changing the model starts a new conversion; **Cancel** discards the selection. If no model is available, finish model configuration first, then return to the result and click **Retry**. Content appears progressively in the result area; wait for completion before using it.
4. Compare heading levels, list order, table contents, and numbers with the original. Conversion can reformat content; the preview is not an exact copy of the source image.

## Preview, copy, and save

The result area previews the document for checking paragraphs and structure. It is not a source editor. Copy or save the result to your destination editor to correct the generated document.

- **Copy a selection**: select text in the preview, right-click **Copy**, and paste into the destination to check the range.
- **Copy the complete result**: clear partial text selections and copy. Destinations may use different clipboard formats; inspect headings and tables after pasting.
- **Save the document**: click **Save as file** and choose a folder and name. Markdown uses **.md**; HTML uses **.html**.
- **Keep generated source**: saving also creates a matching **.txt** companion file. Check both files. Confirming replacement of existing names overwrites the corresponding files.

For precise spreadsheet cell editing, use [Table recognition](./table.mdx) and export XLSX. For plain text, use [Text recognition](./text.mdx).

## Retry after a failure

If no vision model is selectable, return to configuration and check Vision support and whether the model still exists. A name in the list does not prove that the server accepts image input.

For network, authentication, or model errors, check the API address, key, model ID, and proxy as prompted, then click **Retry**. For incomplete output, capture a smaller single-document area. Repeated requests for the same unclear image may not improve the result.

Use **Cancel screenshot** to leave the session. Copy or save existing content before exiting if you need it.

Continue with [Text recognition](./text.mdx), [LaTeX recognition](./formula.md), or [Translation services and custom models](../translation/services.md).
