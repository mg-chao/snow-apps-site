---
title: Proxy, system integration, and MCP
description: Configure Snow Shot network proxies, Windows context-menu and administrator integration, scheduling and memory policies, and local MCP client connections.
---

# Proxy, system integration, and MCP

Network proxy settings control online connections. System integration provides entries such as editing from a file's context menu. MCP lets a client running as the same system user connect to the running Snow Shot app. Configure and troubleshoot each separately.

![Online requests use a proxy, while a local MCP client connects to the running Snow Shot application](/images/guides/en/set-network-integration.svg)

*Instructional illustration. ① Choose the network route, ② configure the local client, ③ keep Snow Shot running.*

## Set the network proxy

1. Open **Settings → Network & connections → Network proxy**. Under **Proxy**, choose **No proxy**, **Use system proxy**, or **Manual configuration**.
2. Choose **No proxy** for direct connections, **Use system proxy** to follow the operating system, or **Manual configuration** to specify your own valid server in **HTTP/HTTPS proxy**.
3. Return to the online operation that failed and submit it again. Judge recovery by the actual result; successfully saving a proxy address does not prove the connection works.
4. For a timeout or connection failure, check that the proxy service is running and the destination is reachable. When returning to a network that needs no proxy, select an appropriate mode.

The full edition also offers a server address for Snow Shot's built-in online services. It does not affect application updates. Configure third-party translation and custom AI endpoints and keys separately under [service configuration](../translation/services); a proxy field does not replace an API endpoint.

## Windows context menu and administrator mode

Under **Settings → General**, choose the **Windows context menu** mode in system integration: image files only, image and document files, or disabled. Once enabled, right-click a supported file in the system file manager and select **Edit with Snow Shot** to enter its pinning/editing workflow. For keyboard access, configure a single-letter or digit access key under **Settings → Application shortcuts → Windows context menu**.

Windows also offers an administrator-startup setting and a restart-as-administrator action. Use them when the task needs those privileges and follow the system prompt. Finish current editing or recording first because restarting changes the running application process. Administrator mode is not a general fix for network, encoding, or image-format errors.

On macOS, startup is managed through system login-item settings, separately from Windows context-menu and administrator options. See [installation and startup](../getting-started/install) for startup and update settings.

Windows also offers **Toggle always on top for the window under the cursor** under **Global shortcuts → Other**. Assign a shortcut, move the pointer over a target window, and invoke it to switch that real window between always-on-top and ordinary states. Invoke again to restore it. This differs from creating a pinned image from a screenshot. Target-window and system permissions affect control; test with an ordinary application window first.

## Scheduling and memory policies

| Setting | Platform and effect |
| --- | --- |
| Application priority | Windows offers Normal, Above normal, High, and Real time to control process scheduling. Observe responsiveness after changing it; this does not change recording resolution. |
| Quality of service (QoS) | macOS offers Responsive, User initiated, Default, Utility, and Background for UI and worker-thread scheduling. Takes effect after restart. |
| Memory optimization policy | Smart control or disabled. Windows trims resident memory while idle, which may briefly slow the next use. macOS releases unused heap memory while preserving active captures and pinned windows. |

These options are under **Settings → General**. Change one at a time when investigating responsiveness, restart when required, and repeat the same short task for comparison.

## Connect an MCP client

1. Open **Settings → Network & connections → MCP** and enable **Enable MCP integration**. Check that the connection status shows a running service. Snow Shot must remain open.
2. Inspect the generated configuration under **MCP connection and client setup**, then click **Copy configuration**.
3. Add it to your MCP client's configuration. If other services already exist, merge server entries instead of replacing the whole configuration. Use the locally generated program path.
4. Restart or reconnect as required by the client. Return to Snow Shot and check the connection count to confirm a client connection.
5. Disable integration when no longer needed. For a failed connection, check that Snow Shot is running, integration is enabled, and configured paths still exist, then restart the client.

Full and Mini configurations contain their respective command names. Copy the configuration again after changing installation location. The page also shows the local endpoint descriptor location, used for discovery rather than a public browser API.

Preserve connection errors and collect diagnostics through [log export](./storage-backup).

Related: [shortcuts](./shortcuts), [cloud upload](../output/cloud-upload), and [storage and backups](./storage-backup).
