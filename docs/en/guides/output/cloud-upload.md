---
title: S3 cloud upload and links
description: Add an S3-compatible upload target, configure its endpoint, region, bucket, and credentials, upload a capture or pinned image, and troubleshoot links.
---

# S3 cloud upload and links

Cloud upload writes the current screenshot or pinned image to your own S3-compatible storage, then copies the object link to the clipboard. Prepare a writable bucket, service endpoint, signing region, and credentials. Snow Shot does not create a storage account or bucket for you.

![Configure a target, upload to its bucket, then copy the object link after success](/images/guides/en/out-cloud-upload.svg)

*Instructional illustration. ① Configure the target, ② upload the image, ③ obtain the link. Read access follows the storage policy.*

## Create and select an upload configuration

1. Open **Settings → Export & storage → Image export → Cloud upload** and click **Add configuration**. The S3 configuration form opens.
2. Enter a unique **Configuration name** and select **S3** as the protocol. Copy the following values from your provider's console; the bucket's web-console page is not a service endpoint.

| Field | What to enter |
| --- | --- |
| Service endpoint | A complete HTTP/HTTPS URL without credentials, query parameters, or a fragment. |
| Signing region | The provider's region for signing requests. |
| Bucket | The bucket receiving the images. |
| Access key ID, secret access key | Credentials allowed to write to this target. |
| Session token | Required for temporary credentials when specified; leave empty for long-term credentials according to the provider's rules. |
| Object key prefix | The object-path prefix for images. |
| Public / CDN base URL | Optional public or CDN URL pointing to the bucket root, used to generate access links. |
| Addressing style | Path-style or virtual-host-style, as required by the provider. |

3. Click **Save**. Correct any missing fields, invalid URL, or duplicate name reported by the form. Resolve local configuration-storage errors before retrying a save.
4. Back in the list, select this configuration as the default target. The first usable configuration is selected automatically; still check the default target. **None** means no upload target is selected.

**Edit** changes a configuration. **Copy** creates a differently named copy for another prefix or bucket. **Delete** removes the local configuration. Deleting the default clears that selection; it does not delete cloud images.

## Upload a screenshot or pinned image

1. Finish selecting and annotating the screenshot, or open the pinned image. Find **Upload to cloud** on its action toolbar. Restore a hidden button in [toolbar settings](../settings/toolbars-tray).
2. Click upload. The image is prepared and encoded, then sent. Watch **Preparing cloud upload** and the percentage progress. Do not submit the same upload repeatedly while waiting.
3. After **Uploaded to cloud. Link copied to clipboard**, paste into a text editor or destination message and check the link. A failed upload shows an error; an old clipboard link is not this upload's result.
4. Open the link in a browser to confirm it is readable before sharing. Public access follows bucket/CDN policy. A successful write does not establish that the recipient can read it.

## Troubleshoot a failed upload

- **Unavailable button:** select a default other than **None**, fill required fields, and wait for any current output or upload task to finish.
- **HTTP error:** check endpoint, signing region, bucket, addressing style, and credentials. Pay particular attention to expired temporary credentials or a missing session token. Correct the configuration, then upload again.
- **Network error or timeout:** check service reachability and **Settings → Network & connections → Network proxy**, then retry after restoring the connection.
- **Upload succeeds but the link fails:** check that the public/CDN base URL points to the bucket root and inspect cloud read policy. Repeated uploads will not fix access policy.

Continue with [network proxy](../settings/network-integration), [local saving](./copy-save), or [configuration backups](../settings/storage-backup).
