---
title: Barcode and QR code recognition
description: Select barcodes or QR codes on screen, choose the grouped recognition tool, inspect multiple results, copy content, save text or open links, and troubleshoot unreadable codes.
---

# Barcode and QR code recognition

**Barcode recognition** reads barcode and QR code content from the screen, such as URLs or identifiers in images. Reading content does not establish its authenticity; check an address before opening it. This tool is available in Full, not Mini.

![Barcode recognition: select the whole code, read its content, then copy it or open a link](/images/guides/en/rec-barcode.svg)

*Instructional illustration. The blocks explain the input area and are not a scannable QR code.*

## Recognize and retrieve content

1. Display the entire code. Start a screenshot—**F1** on Windows or **Control+1** on macOS by default—and include the whole code with a little surrounding whitespace. Do not capture only part of its blocks or bars.
2. Expand the table/barcode tool group and choose **Barcode recognition**. Its group button shows the current or last-used tool, so identify it by its label rather than position alone.
3. Wait for completion. The result area displays decoded text. If the selection contains several readable codes, inspect each result and identify the one you need.
4. Select text in the relevant result and right-click **Copy**. For all content, use **Select all**, then copy.

## Automatic QR detection and markers

Full can also discover QR codes automatically after you confirm a screenshot selection:

1. Enable **Automatically recognize QR codes** in **Settings → Screenshots** interaction settings. Capture again and confirm a selection containing complete QR codes.
2. Keep the **Move** tool active and wait for circular markers on readable codes. Click a marker to open its text bubble; inspect multiple codes individually.
3. Click **Copy text** in the bubble to copy selected text, or the whole code's content if there is no partial selection, and end the screenshot. Valid URLs also offer **Open link**. Successful opening ends the screenshot; a failed opening shows an error in the bubble.
4. To remove markers from view, click **Show QR codes** in the Move tool's property bar to toggle their visibility.

**Show QR codes** controls detected markers; it does not generate QR codes. If markers do not appear, check automatic recognition, the active tool, and image clarity, or use manual Barcode recognition above.

![Automatic QR detection: a confirmed selection gains markers; clicking opens a content bubble, and copying ends capture](/images/guides/en/rec-autoqr.svg)

*Instructional illustration. Circular markers open detection results; successful copy or open actions end the current screenshot.*

## Copy and open links

- **Copy content**: right-click **Copy** in the result, then paste into a text editor. Check for content from multiple codes or extra line breaks.
- **Save results**: use **Save as file**, choose a location, and save **.txt** text. This saves decoded content, not a QR code image.
- **Open links**: recognized clickable URLs can open in the default browser. Only link portions have that interaction; copy ordinary identifiers as text.
- **Keep the code image**: leave recognition results and save the original using screenshot output. TXT is not an image file.

## When no result is found

For “No barcode recognized,” check complete boundaries and whether compression, blur, obstruction, or strong perspective affects the image. Enlarge the code in its source application and capture again.

For many codes, first capture one and confirm it can be read, then expand the area. Enlarging a screenshot cannot recover details already absent from the source.

For service or request errors, click **Retry** in the result to process the current input again. If the input is unclear, select a new area instead. Exiting and restarting capture gives a new input range.

Continue with [Table recognition](./table.mdx), [Text recognition](./text.mdx), or [Image and clipboard pins](../pinning/image.md).
