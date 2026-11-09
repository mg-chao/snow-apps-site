---
title: Exact dimensions, ratios and selection appearance
description: Enter selection coordinates and dimensions in Snow Shot, lock or choose aspect ratios, save region presets, and adjust rounded corners, borders, shadows and logical or physical pixel units for an exact capture.
---

# Exact dimensions, ratios and selection appearance

Use numeric selection controls for fixed-size illustrations, aligned captures or repeatedly identical regions. Start a selection with the screenshot shortcut (default F1 on Windows or Control+1 on macOS), then adjust it under **Move**. These controls change the captured region. For final file dimensions, see [output size](../output/copy-save.md).

![Diagram relating selection position, dimensions, units, aspect-ratio menu and numeric input](/images/guides/en/cap-precise.svg)

*Instructional illustration: position and size values belong to the selection toolbar. The ratio menu and lock button serve separate purposes.*

## Enter an exact region

1. Create a rectangular selection and locate the toolbar showing **X, Y, Width × Height**. Hover over a value to read its tooltip.
2. Click a coordinate or dimension to open **Resize selection**. Set the upper-left position with **X coordinate** and **Y coordinate**, then enter the dimensions.
3. To change width and have height follow, enable the ratio lock first. To enter independent dimensions, unlock it before entering both values.
4. Click **OK**. The dialog closes and the selection border updates. Inspect the position and bounds before copying or saving. **Cancel** discards the changes made in this dialog.

You can also scroll over a numeric value to fine-tune that field directly, watching the border change. Values are limited by the available canvas. Coordinates cannot retrieve content outside the captured screen.

**Settings → Screenshots → Interaction → Selection resize mode** controls edge-drag behavior. **Follow mouse movement** adjusts by the pointer's movement; **Follow mouse position** makes the dragged boundary follow its position. After changing the mode, drag from the same selection edge to compare the behavior. You can still confirm exact dimensions numerically.

## Ratio presets and temporary constraints

The **Selection aspect ratio** menu offers **Free, 1:1, 3:2, 4:3, 16:9, 2:3, 3:4 and 9:16**. For example, choose 16:9 for a landscape video cover or 1:1 for a square image. Recheck the bounds so the constraint does not crop important content.

**Lock selection aspect ratio** locks the current ratio; it does not force a standard preset. To resize freely again, unlock it and select Free. Holding the default **Shift** key while dragging a rectangular selection temporarily makes width and height equal (1:1), rather than preserving an arbitrary previous ratio.

Default **Q** snaps a rectangular selection to an aspect ratio:

1. With the ratio unlocked, hold Q during a selection or edge-resize drag. The rectangle snaps to the nearest standard ratio, and the border and ratio control update together.
2. Release Q. The snapped ratio stays locked. Keep watching the region while dragging to avoid losing important content.
3. Pressing Q again with the ratio locked unlocks it and restores Free. You can also restore it manually using the lock button and ratio menu.

Q does not apply to freehand regions or region-combination operations. If you changed the binding, check the ratio snap action under **Settings → Application shortcuts**.

## Reuse the previous selection or save presets

**Quick set** in the adjustment dialog can load the current region, previous region or saved presets. To reuse a position and size:

1. Set the current coordinates, dimensions and decoration correctly.
2. Use **Add preset**, enter a descriptive name and confirm. The preset appears in the list.
3. During a later capture, open the same dialog and select that name in Quick set. Check whether the current display layout still suits it, then confirm.

The selection toolbar's preset menu also includes the previous selection. Display arrangement or scaling changes can constrain an old region to the current canvas. Inspect the actual border rather than relying on its preset name.

## Corners, borders, shadows and units

Set **Corner radius** in the adjustment dialog for rounded rectangular output. **Border type** switches between **Shadow** and **Border**, revealing the corresponding width and color controls. Try a small width first and check that the decoration does not obscure content before saving. Custom irregular regions do not support rectangular corner-radius parameters.

Move also offers **Logical pixel selection / Physical pixel selection**. On scaled or Retina displays, logical coordinates may differ from image pixels. Decide whether you need an on-screen layout size or final file dimensions before choosing units. The Mac interface can also show points or `dp` unit hints. Open the saved image and inspect its dimensions rather than judging by visual size alone.

## Capture interface colors and guides

Open **Settings → Screenshots → Capture interface**, make a change, then start another screenshot to inspect it. Selection borders, masks and guides here are interface aids. They are separate from the output image's border and shadow in the adjustment dialog.

![Positions of the capture selection border, outside mask and center guides](/images/guides/en/set-capture-interface.svg)

*Instructional illustration: ① selection border, ② outside mask, ③ center guides.*

| Setting | Action and visible result |
| --- | --- |
| Screenshot selection transition animation | Choose fast, smooth or off, then watch transitions while moving between Smart Selection candidates |
| Selection border color | Choose a color and check that the current selection outline is distinguishable |
| Selection mask color | Adjust the overlay outside the region and compare inside/outside contrast |
| Shortcut hint opacity | Drag the slider and check legibility without obscuring content |
| Screenshot region type hint | Toggle the hint at the top of capture to identify rectangle or other region types |
| Show guides by default | Show guides at the start of new captures; default Alt (Option on macOS) temporarily toggles them |
| Cursor guide color | Set the dashed crosshair color at the pointer |
| Selection center guide color | Set the solid crosshair color at the selection center |
| Display center guide color | Set the display-center reference lines |
| Color picker center guide color | Set the guides near the sampled pixel to make its location clear |
| Show edit selection toolbar | Show or hide the selection editing sub-toolbar; check this first if numeric controls are missing |

**Color picker display mode** offers Hide outside selection, Always show and Always hide. If you cannot find the magnified grid, inspect this setting, then read [screen color picking](./color-picker.md).

## Values change unexpectedly

If width and height change together, check the ratio lock. If a preset cannot apply, check screen bounds. If corner radius is unavailable, check for a custom region. If a border is hard to see, inspect its width and color. To draw a box around content, use a [shape annotation](../annotations/shapes.mdx) rather than adding a border to the entire output selection.

Continue with [multiple regions](./multiple-regions.mdx), [irregular selections](./irregular-regions.mdx) or [copying and saving](../output/copy-save.md).
