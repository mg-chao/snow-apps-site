---
title: macOS permissions and first use
description: Check Snow Shot screen recording, Accessibility, Input Monitoring, and microphone permissions on macOS, restart when required, and verify each action.
---

# macOS permissions and first use

macOS controls screen capture, system input, and microphone access separately. Decide which features you need, then follow Snow Shot's permission prompts into system settings. Windows does not use this macOS permissions panel.

![Screen recording, Accessibility, Input Monitoring, and microphone permissions mapped to their tasks](/images/guides/en/start-permissions.svg)

*Instructional illustration: check each permission separately. Allowing one does not automatically allow the others.*

## Check permissions from the app

1. Open **Settings → App permissions** in Snow Shot's main window and inspect status. You can also use the guidance shown the first time a capture or another action needs access.
2. Find an ungranted permission and click its system-settings entry. Check that the app in the privacy list is the Snow Shot copy you are running.
3. Allow access as the system requests. If it asks you to quit and reopen, finish other editing or recording first, then restart Snow Shot.
4. Recheck the app's permission page and perform the relevant action. A granted status and a successful result are separate checks; investigate further if either is missing.

## When each permission is needed

| Permission | Related tasks | How to verify after allowing |
| --- | --- | --- |
| Screen & System Audio Recording | Screenshots, screen recording, live image capture | Use the capture shortcut, Control+1 for a fresh configuration, select an ordinary window, copy it, and check the image. |
| Accessibility | System controls interacting with other apps, selected-text operations | Run the required action and check that text or target control is available. |
| Input Monitoring | Some global keyboard/mouse actions and recorded input effects | Test your configured shortcut, mouse action, or recording effect. |
| Microphone | Recording your voice | Enable the microphone, record a short clip, and play it to check audio. |

Enabling a recording webcam may also trigger system camera permission. Microphone, webcam, and system audio are separate inputs. Having microphone access does not prove system audio was recorded. See [recording audio and webcam](../recording/audio-camera.mdx) for setup and sound checks.

## Capture remains black or an action still fails

**A permission change has not taken effect.** Check whether the system requires an app restart. Quit and reopen the copy you are using, then recheck status.

**Several Snow Shot entries appear in system settings.** Identify the actual launch path. Applications and the mounted DMG may each contain a separate copy. Allow the copy you are using and retry; do not rely on the displayed name alone.

**Only some content can be captured.** Compare with an ordinary window first. System- or application-protected content may remain uncapturable even when access is granted.

**A shortcut still does nothing.** Check your binding and key conflicts, then inspect registration under [shortcut settings](../settings/shortcuts.mdx). Fresh configurations use Control+1, not Command+1. Permissions do not explain every shortcut failure.

Before reporting an issue, note the macOS version, Snow Shot version, actual app path, and failed action. Use [log export](../settings/storage-backup.md) for diagnostics, and check for personal paths you need to remove before sharing.

Next: [take your first screenshot](./quick-start.mdx) · [start recording](../recording/start.mdx).
