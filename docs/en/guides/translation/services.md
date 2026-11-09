---
title: Translation services and custom models
description: Configure compatible DeepL, DeepLX, Baidu, or Youdao endpoints and OpenAI-compatible model URLs, credentials, IDs, vision, reasoning, concurrency, and saved connectivity settings.
---

# Translation services and custom models

Configure translation services and custom AI models under **Settings → Network & connections**. Dedicated translation endpoints translate text; vision models that accept image input can also handle image conversion, tables, and formulas. Obtain the provider's address, authentication details, and model ID first.

![Service configuration: dedicated translation uses a complete endpoint, while custom models use a base URL and actual model ID](/images/guides/en/tr-services.svg)

*Instructional illustration. The two URL formats follow different rules.*

## Add a dedicated translation configuration

1. Open **Settings → Network & connections → Translation services** and click **Add configuration** under **Translation configurations**.
2. Enter a recognizable **Configuration name** and select **DeepL**, **DeepLX**, **Baidu**, or **Youdao** under **Service format**. The format determines the request protocol and must match the real endpoint.
3. Enter the **complete translation endpoint**, including its path, in **API URL**. Query parameters are used as entered. A domain alone is insufficient; do not embed a username or password in the URL.
4. Supply the **API key** required by DeepL / DeepLX. DeepLX's optional token is sent as a Bearer token. Baidu and Youdao use their respective **Application ID** and **Application key**; the form shows fields for the selected service.
5. Set **Concurrency** from **1–16**. This is the configuration's shared simultaneous-request limit across translation tasks. Reduce it when the service rate-limits requests.
6. Click **Save**. Once the configuration appears in the list, select it under **Translation service** on the translation page and test a short sentence to confirm a real request succeeds.

## Add a custom model

1. Under **Network & connections → Custom AI models**, click **Add model** in **Custom models**.
2. Enter a display **Model name** and an OpenAI-compatible Chat Completions **base URL** in **API URL**. Snow Shot appends `/chat/completions`; do not include that path twice.
3. Enter the **API key** and **API model**. Type the provider's exact model ID, or expand the list to try fetching models. You can enter a known ID manually if fetching fails.
4. Enable **Vision support** only when the remote model actually accepts images. This switch cannot give a text-only model image understanding.
5. Select **Provider type**—OpenAI, Qwen, DeepSeek, or Doubao—to match reasoning controls to the interface. With OpenAI, the model controls reasoning; other types can explicitly configure **Reasoning support** using available options.
6. Set **Concurrency** to **1–16** and click **Save**. Select the model on the translation page to test text, then use image conversion to test image support.

**Base URL validation** requires HTTP or HTTPS and rejects embedded credentials, queries, and fragments. Keys must not contain line breaks. Names must not duplicate an existing configuration. Resolve field messages before saving.

## Edit configurations and troubleshoot connectivity

**Edit** changes an existing item, **Duplicate** creates a separately adjustable configuration, and **Delete** removes an unused item. Deleting a model in use makes the application choose another available option. Recheck the service in the task and retry if necessary.

| Problem | Check in this order |
| --- | --- |
| Saving fails or the configuration does not remain in the list | Read field validation, then check writable configuration storage; reopen the form to confirm before starting a network task |
| The model list cannot be fetched | Check the base URL and authentication; manually enter a known ID and test a short sentence |
| Translation authentication fails | Check service format, key, and application ID; remove unwanted pasted whitespace or line breaks |
| An image task rejects input | Confirm actual image support, enabled Vision support, image format, and API compatibility |
| Requests time out or cannot connect | Check **Network proxy**, endpoint, and whether a local service is running; fix the cause, then use **Retry** in the original task |
| An existing task still reports an error after configuration changes | Retry as prompted so the new request uses updated configuration |

The server address under **Snow Shot server** applies to built-in online services; clearing it restores the default. It is separate from a custom model's API URL. Changing it does not change the application update source.

This configuration feature requires Full. Mini does not provide these translation and API configuration entries.

Continue with [Screenshot translation](./screenshot.md), [Text translation](./text.md), [Image conversion](../recognition/image-conversion.md), or [Table recognition](../recognition/table.mdx).
