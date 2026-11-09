---
title: Storage, cleanup, configuration backups, and logs
description: Inspect Snow Shot storage usage, clean history and recording work files, change Windows data storage, and export configuration or diagnostic ZIP archives.
---

# Storage, cleanup, configuration backups, and logs

Application data, independently exported images/videos, and configuration backups have different purposes. Check storage health and the source of its usage before migrating, cleaning, or backing it up.

![Inspect storage usage, then choose configuration backup, history cleanup, or recording temporary-file cleanup](/images/guides/en/set-storage-backup.svg)

*Instructional illustration. ① Check usage and errors, ② back up settings, ③ clean the relevant data type.*

## Inspect usage and storage location

1. Open **Settings → Export & storage → Data storage** and inspect the data directory, mode, total usage, and latest error.
2. Refresh to inspect screenshot history, pinned content, OCR, recording temporary files, and other usage separately. Identify the growing data type before cleaning it.
3. Check diagnostics, log location, and log status. Preserve this information when investigating a permission or write error.

Modes can include application data, custom directory, portable, read-only (newer configuration), or unavailable. If configuration comes from a newer version, use a compatible version rather than manually editing the database to bypass protection.

## Change the data directory on Windows

The Windows data-storage section offers directory selection. Choose a writable location and follow the dialog's migration/use options. Wait for the change to finish, then check its location and usage. Do not run cleanup or move files during migration.

On macOS, this area primarily displays status and does not offer the same Windows migration button. To change only image or video output, edit the save directory under **Image export** or **Video export**, rather than migrating all application data.

## Export and restore configuration

1. In the same data-storage section, click **Export** under **Export configuration**. In the dialog, choose whether to include **Canvas style configuration** when migrating saved annotation styles, then click **Export** to create the archive. **Cancel** leaves without exporting.
2. After the message confirms export to the clipboard, paste into a file manager and keep the ZIP with a recognizable date or purpose. Clipboard content alone is not a durable backup.
3. Back up your current settings before restoring. Click **Import** under **Import configuration** and select the earlier ZIP. Canceling the file chooser leaves settings unchanged.
4. Read the replacement confirmation: archive values replace current application settings, and some changes require a restart. Click **Import** to replace them, or **Cancel** to keep the current configuration.
5. After success, check theme, shortcuts, and save directories, and restart if needed. When moving between computers, recheck local paths and device availability.

The configuration archive contains app settings; it is not a backup of every screenshot or video. Preserve important output files separately. A log archive is another ZIP type and must not be imported as configuration.

## Choose what to clean

| Entry | Scope and checks before use |
| --- | --- |
| Screenshot-history age, entry, and disk limits | Affect retained history. Save important images independently first. |
| Clear screenshot history | Removes all screenshot records after confirmation; this is not a temporary filter. |
| Pinned-window retention limits | Apply only to closed windows; retained windows are protected. |
| Clear closed records | Removes closed pinned records without clearing retained windows. |
| Delete temporary recording files | Removes work files left by completed or interrupted recordings. Finish any recovery first. |

Read each confirmation before cleanup, or cancel to return. If an interrupted recording still needs source-data recovery, use [recording recovery and export](../recording/trim-export) before cleaning. See [screenshot history](../output/history) for retention details.

## Export logs and diagnose save errors

Click **Copy** under **Export logs** to package logs and crash reports into a ZIP on the clipboard. Paste the archive into a file manager, then give it to the person investigating the issue. Logs are diagnostics, separate from screenshot output.

For unwritable storage, check whether the data directory exists, whether disk space is available, and whether system access is allowed. Refresh after fixing it and try a small save. For a settings-save failure, resolve data storage before repeatedly changing options. Changes that have not persisted may be lost at restart.

Related: [copying and saving](../output/copy-save) and [network and system integration](./network-integration).
