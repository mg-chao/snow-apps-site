---
title: OCR models and offline preparation
description: Prepare local OCR components, choose an Ultra small, Small, or Medium V6 model, adjust detection scaling and processing, and configure acceleration, a resident process, and model warm start.
---

# OCR models and offline preparation

OCR waiting time includes component preparation, model loading, and recognition. Prepare resources first, then choose a model according to speed and detail needs. These settings apply to local text recognition; tables, formulas, and translation have separate service requirements.

![OCR models: prepare resources, choose a model, and compare speed and accuracy on the same sample](/images/guides/en/rec-models.svg)

*Instructional illustration. Model size alone does not establish whether your sample will be recognized correctly.*

## Prepare before going offline

| Installation | What to finish while online |
| --- | --- |
| Windows Full offline installer | Includes default OCR resources; recognize a sample containing the text you actually need after installation |
| Full online installer | Install required components online; enter Text recognition and wait for initial resource preparation |
| Mini | Launch the main-window Text recognition action, add the toolbar tool, or configure a separate shortcut; prepare resources online and run a sample |

To add the Mini toolbar entry, open **Settings → Screenshots → Action toolbar → Screenshot toolbar settings** and drag **Text recognition** from “Hidden tools” to a visible position. Alternatively, assign a separate **Text recognition** action under **Global shortcuts**. Capture again to confirm the toolbar button appears.

You do not need to assign keys just to try OCR. Search for “Text recognition” in the main window's **Search function**, select the result to locate the Global shortcuts row, then click the action title or empty area. The “Not set” button configures keys. Confirming the screenshot selection starts recognition.

Before switching to a different model size, select it while online and run recognition once. Wait for preparation to finish, then disconnect and repeat the same task. Successful ordinary screenshots do not prove OCR resources are ready.

For preparation errors, reconnect, check the proxy under **Settings → Network & connections**, and enter Text recognition again. Do not delete unfamiliar data directories as a repair attempt.

Mini names the corresponding settings page **Text recognition**; its model and output settings work in the same way.

## Choose a model

1. Open **Settings → Text recognition & translation** in the main window and expand **OCR models & performance**.
2. Under **Model type**, choose **Ultra small V6**, **Small V6**, or **Medium V6**. Small V6 is the default configuration.
3. Recognize the same clear screenshot, record waiting time, and check the text. Switch models and compare the same area so input differences do not distort the comparison.

Smaller models can reduce computation; larger models require more resources. Judge the fonts, sizes, and layouts you commonly use. Changing models does not guarantee that a particular error will be corrected.

## Detection and processing

**Text detection scaling** controls image resizing before recognition:

- **Limit long side (faster)** limits the longer edge to reduce processing. For tiny text, enlarge it in the source application before capturing.
- **Enlarge short side (more detail)** enlarges the shorter edge and may find smaller text, at additional processing cost.

**Text detection processing** offers **Accuracy first** and **Speed first**. Speed first reduces some short-text computation and may change results. Compare the same passage to make sure the faster setting does not omit needed content.

## Reduce waiting time

| Setting | What changes | What to check |
| --- | --- | --- |
| Hardware acceleration | Uses a GPU when available, otherwise falls back to CPU | Enabling it does not prove your device is currently using the GPU |
| Resident recognition process | Keeps the process alive to reduce subsequent startup time | Consumes memory while idle |
| Model hot start | Preloads the selected model to reduce subsequent loading time | Depends on the resident process and uses additional memory |

For occasional recognition, start with the resident process and warm start disabled. For frequent use, measure their benefit. Change one option at a time and compare first and subsequent recognitions. If acceleration misbehaves, disable it and check whether CPU recognition succeeds.

## Local OCR and online features

Once local text recognition completes, you can organize and copy text without a network connection. **Text translation**, online table services or vision models, formula recognition, and image conversion each require their own service conditions. Recognized text does not establish that those online services are ready.

Continue with [Text recognition](./text.md), [Table recognition](./table.mdx), or [Translation services and custom models](../translation/services.md).
