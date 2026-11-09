---
title: Live window pins
description: Identify a capturable window from a screenshot selection, create an updating pin, transform or crop its view, copy or save the current frame, freeze it as an image, and handle unavailable sources.
---

# Live window pins

**Pin window to screen** continuously displays a source window in an independent pin for side-by-side work. The source must continue to exist. Convert its current frame to an image when you need to retain one state.

![Live window pin: source updates appear in the pin; converting to an image stops live updates](/images/guides/en/pin-live.svg)

*Instructional illustration. Live display, saving one frame, and video recording produce different results.*

## Pin a live window

1. Open the source window and keep it visible. On macOS, grant Snow Shot the required screen-recording permission in System Settings and follow application permission prompts before retrying.
2. Start a screenshot—**F1** on Windows or **Control+1** on macOS by default—and select within the target window's content. The selection should correspond to a capturable window; avoid centering it on the desktop, blank toolbar space, or an overlapping window.
3. Click **Pin window to screen** and wait for initialization. It is a separate action from ordinary **Pin to screen**.
4. Change source content and check that the live pin updates. Position the pin while keeping the source running.

For “No capturable window found in the selection,” exit, fully display the source, and select again. For initialization failure, check capture permissions and that the target still exists, then retry.

## Adjust the view and freeze it

**Process image** in the live pin's context menu provides zoom, opacity, rotation, and flipping. Where cropping is available, right-drag the desired view and choose **Apply crop** as needed; see [Transforms and cropping](./transform.mdx). These change the observation area, not content inside the source application.

When **Convert to image** is available, click it to capture the currently available frame and turn the window into a static image. You can then use ordinary image recognition and annotation. It stops following updates; invoke Pin window to screen again for a new live connection.

**Copy to clipboard** and **Save as file** also retrieve an available current frame to share one moment. They do not generate video. Use [Screen recording](../recording/start.mdx) for continuous changes.

When a frame is temporarily unavailable, commands requiring one—copy, save, Convert to image, and image editing—may be unavailable. Restore the source window first.

## When updates stop

| Displayed state | Cause and action |
| --- | --- |
| Window minimized; latest content unavailable | Restore the source and wait for live content; do not treat an old frame as current |
| Window closed; latest content unavailable | The source ended. Reopen the application and create a pin for its new window |
| Live content unavailable; retrying | Wait for automatic retry; check visibility and permission, or close this live pin and create another |
| Window changed while preparing the image; retry | The source changed during copying or conversion. Wait for stability and repeat the command |

Live menus omit some ordinary-image features, including loading new clipboard content, thumbnails, hide at top, and static-canvas annotation. Convert to an image first when you need those operations.

After the source closes or the application exits, static-image recovery in management should not be interpreted as reconnecting the original live window. Copy or save important states explicitly.

Continue with [Ordinary image pins](./image.md), [Text and annotations](./text.md), or [Groups and recovery](./management.mdx).
