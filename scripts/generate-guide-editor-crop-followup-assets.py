"""Create complementary crop/cancel, flattening and mixed-history illustrations."""

from pathlib import Path
from html import escape
import csv
import math
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/public/images/guides"
INK, MUTED = "#24384f", "#536b83"
BLUE, PURPLE, GREEN, RED, ORANGE = "#2877bd", "#7154d9", "#258568", "#d84d53", "#c26b2c"
RECORDS = []


def text(x, y, value, size=20, color=INK, weight=400, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def rect(x, y, width, height, fill="white", stroke="#c8d3e6", radius=8, extra=""):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>'


def line(x, y, xx, yy, color=BLUE, width=2, dash=""):
    return f'<path d="M{x} {y} L{xx} {yy}" fill="none" stroke="{color}" stroke-width="{width}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>"


def circle(x, y, radius, fill="none", stroke=ORANGE, width=3):
    return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def arrow(x, y, xx, yy, color=PURPLE, width=3, head=10):
    length = math.hypot(xx-x, yy-y)
    ux, uy = (xx-x)/length, (yy-y)/length
    return line(x, y, xx, yy, color, width) + (
        f'<path d="M{xx-head*ux+head*.6*uy} {yy-head*uy-head*.6*ux} '
        f'L{xx} {yy} L{xx-head*ux-head*.6*uy} {yy-head*uy+head*.6*ux}" '
        f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def wrap(value, width=240, size=20):
    result, current, units, gap = [], "", 0.0, ""
    for token in re.findall(r"\s+|[^\s\u3400-\u9fff]+|[\u3400-\u9fff]", value):
        if token.isspace():
            gap = " " if current else ""
            continue
        cost = sum(1 if unicodedata.east_asian_width(c) in "WF" else .55 for c in gap+token)
        if current and units+cost > width/size and token not in "，。；：！？、）】》」』":
            result.append(current)
            current, units, gap = "", 0.0, ""
            cost = sum(1 if unicodedata.east_asian_width(c) in "WF" else .55 for c in token)
        current += gap+token
        units += cost
        gap = ""
    if current:
        result.append(current)
    return result


def notes(title, groups, history=None, en=False):
    out = rect(644, 98, 288, 396) + text(666, 134, title, 22, PURPLE, 650)
    yy = 181
    for group in groups:
        for row in wrap(group):
            out += text(666, yy, row)
            yy += 28
        yy += 20
    assert yy <= (360 if history else 492), (title, yy)
    if history is not None:
        out += text(666, 382, "Applied edits" if en else "当前已应用", 17, MUTED)
        for index, (label, active, color) in enumerate([
            ("Crop 40 rows" if en else "裁剪 40 行", history[0], PURPLE),
            ("New orange circle" if en else "新画橙圈", history[1], ORANGE),
        ]):
            y = 413+38*index
            out += circle(679, y-5, 7, color if active else "white", color if active else "#aabbd2", 2)
            out += text(697, y, label, 18, INK if active else "#8293a4")
    return out


def image_content(height=200, cropped=False, marker="none", orange=False, preview=False, guide=None):
    # Coordinates are image pixels: remove y=[80,120), so B moves 145->105.
    b_y = 105 if cropped else 145
    out = rect(0, 0, 300, height, "white", "#aabbd2", 0)
    out += rect(20, 20, 110, 40, "#e5effa", "none", 0)
    out += text(36, 49, "A", 25, BLUE, 700)
    out += rect(20, b_y-15, 260, 30, "#dcefe9", "none", 0)
    out += text(36, b_y+9, "B", 25, GREEN, 700)
    if marker != "none":
        marker_y = b_y if marker == "saved" else 145
        out += line(0, 145, 300, 145, "#aabbd2", 1, "4 4")
        out += arrow(160, marker_y, 260, marker_y)
    if orange:
        out += circle(45, 40, 19)
    if preview:
        out += rect(0, 80, 300, 40, "#df5961", "none", 0, 'opacity=".85"')
        out += line(0, 80, 300, 80, BLUE, 1.3, "4 3")
        out += line(0, 120, 300, 120, BLUE, 1.3, "4 3")
        out += text(150, 106, "40 px", 16, "white", 700, "middle")
        out += arrow(279, 85, 279, 115, "white", 1.6, 6)
    if guide is not None:
        out += line(0, guide, 300, guide, BLUE, 1, "4 4")
    return out


def canvas(height, content, tool=None, en=False, marker=False):
    x, y, scale = 80, 136, 1.6
    out = rect(28, 98, 592, 396)
    out += text(x, 121, f"300 × {height} px", 19, MUTED, 600)
    if height != 200:
        out += rect(x, y, 480, 320, "none", "#aabbd2", 0, 'stroke-dasharray="5 5"')
    out += f'<g transform="translate({x} {y}) scale({scale})">{content}</g>'
    out += text(66, y+5, "0", 16, MUTED, anchor="end")
    out += text(66, y+height*scale+5, str(height), 16, MUTED, anchor="end")
    if marker:
        out += text(66, y+145*scale+5, "145", 16, PURPLE, anchor="end")
    if tool:
        out += text(86, 485, tool, 19, PURPLE, 550)
    else:
        out += text(86, 485, "Purple arrow: earlier annotation" if en else "紫色箭头：此前已有标注", 18, PURPLE)
    return out


def save(lang, name, title, label, caption, body, footer, ids, section):
    out = PUBLIC / ("en" if lang == "en" else "") / name
    out.parent.mkdir(parents=True, exist_ok=True)
    kind = "Instructional illustration" if lang == "en" else "操作示意"
    out.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="560" viewBox="0 0 960 560" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title+": "+label)}</title><desc id="desc">{escape(kind+". "+caption)}</desc>'
        '<rect width="960" height="560" rx="20" fill="#f5f7fc"/>'
        '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">'
        + text(28, 42, title, 28, INK, 700) + text(28, 77, label, 19, MUTED) + body
        + line(28, 509, 932, 509, "#dbe3ef", 1) + text(28, 539, footer, 18, MUTED)
        + text(930, 539, kind, 17, MUTED, anchor="end") + "</g></svg>", encoding="utf-8"
    )
    RECORDS.append({
        "Asset": out.relative_to(ROOT).as_posix(),
        "Feature IDs": ids,
        "Teaching purpose": caption,
        "Documentation path": f"docs/{lang}/guides/image-editing/editor.mdx#{section}",
        "Associated step": label,
        "Source": "artifacts/research-release-editor-crop.md; f02f50e imageeditingcanvas.cpp:71-143,174-180,228-300; imageeditingdocument.cpp:165-254; imageediting_tests.cpp:1798-1826",
        "Production method": "原创双语SVG scripts/generate-guide-editor-crop-followup-assets.py；固定源图像坐标与比例，不画不确定的实际工具条，不使用应用截图作为示意底图",
        "Status": "已制作操作示意；普通UI、真实入口与原缺口/覆盖/验收状态保持不变",
        "Capture prerequisites and next action": "后续由普通UI在自有图像核对浮动裁剪按钮、N px预览/取消/提交、活动和已合成标注及混合Undo顺序；示意图不替代真实操作证据",
    })


for lang in ["zh", "en"]:
    en = lang == "en"
    section = "vertical-crop-remove-a-horizontal-strip" if en else "垂直裁剪去掉一段横向条带"
    labels = ["Hold to preview 40 rows", "Esc, then release", "Start a new drag", "Release to apply"] if en else ["按住预览 40 行", "按 Esc 后松开鼠标", "重新按下并拖动", "松开提交"]
    captions = [
        "Hold the left button to preview the full-width 40 px strip. The image is still 300×200.",
        "Press Esc, then release the left button. The red range disappears without cropping; Vertical crop stays active.",
        "Press the left button again and drag out a new 40 px preview. Canceling did not submit the earlier drag.",
        "Release to apply the new drag. Height becomes 160 px; B shifts up 40 px. The remaining blue line is only a guide.",
    ] if en else [
        "按住左键预览贯穿整宽的40 px横带；底图仍为300×200，尚未提交。",
        "按Esc后再松开左键，红色范围消失，原图未改；仍留在垂直裁剪工具。",
        "重新按下左键，再拖出40 px预览；前一次取消的拖动不会被提交。",
        "松开左键提交新拖动，图像高变为160，B上移40 px；剩余蓝线只是定位线。",
    ]
    groups = [
        ["Left button held.", "N = 40 px, full width.", "Pixels are unchanged."],
        ["Press Esc, then release.", "No red range; no crop.", "Vertical crop stays active."],
        ["Press and drag again.", "Preview a new 40 px strip.", "Pixels are still unchanged."],
        ["Release applies the crop.", "Height:200 →160 px.", "Blue line: guide only."],
    ] if en else [
        ["左键仍然按住。", "N = 40 px，贯穿整宽。", "底图像素还没有改变。"],
        ["按Esc，再松开左键。", "没有红带，也没有裁剪。", "仍是垂直裁剪工具。"],
        ["重新按住左键拖动。", "新预览仍为40 px。", "像素还没有改变。"],
        ["松开即提交这次裁剪。", "高度：200 →160 px。", "蓝色定位线不是红带。"],
    ]
    for step in range(1, 5):
        cropped = step == 4
        content = image_content(160 if cropped else 200, cropped, preview=step in [1, 3], guide=120 if step in [2, 4] else None)
        body = canvas(160 if cropped else 200, content, "Tool: Vertical crop" if en else "当前工具：垂直裁剪", en)
        body += notes("Vertical crop" if en else "垂直裁剪", groups[step-1])
        save(lang, f"img-crop-rows-cancel-{step}.svg", "Preview, cancel and apply rows" if en else "垂直裁剪：预览、取消与提交", labels[step-1], captions[step-1], body,
             "Same pixel scale; no automatic fit between frames." if en else "各帧保持原点和比例；预览与提交是不同状态。", "IMG-004", section)

    section = "undo-output-and-further-work" if en else "撤销输出与后续处理"
    for step in [1, 2]:
        cropped = step == 2
        height = 160 if cropped else 200
        body = ""
        for index, mode in enumerate(["editable", "saved"]):
            panel_x, image_x, image_y, scale = (28, 72, 177, 1.2) if index == 0 else (494, 538, 177, 1.2)
            body += rect(panel_x, 98, 438, 396)
            heading = ["Editable annotation", "Saved image pixels"][index] if en else ["本次可编辑标注", "保存再打开的图片"][index]
            body += text(panel_x+20, 133, heading, 22, PURPLE, 650)
            body += text(image_x, 161, f"300 × {height} px", 18, MUTED, 600)
            if cropped:
                body += rect(image_x, image_y, 360, 240, "none", "#aabbd2", 0, 'stroke-dasharray="5 5"')
            body += f'<g transform="translate({image_x} {image_y}) scale({scale})">{image_content(height, cropped, mode)}</g>'
            body += text(image_x-8, image_y+145*scale+5, "145", 16, MUTED, anchor="end")
            if cropped and index == 1:
                body += text(image_x-8, image_y+105*scale+5, "105", 16, GREEN, anchor="end")
            lines = (["B and arrow at y =145.", "Arrow can be selected."] if index == 0 else ["Same starting appearance.", "Arrow is part of the pixels."]) if en else (["B与箭头都在y =145。", "箭头仍可单独选择。"] if index == 0 else ["起始外观相同。", "箭头已是图像像素。"])
            if cropped:
                lines = (["B shifts to y =105.", "Arrow stays at y =145."] if index == 0 else ["B and the saved arrow", "both shift to y =105."]) if en else (["B移到y =105。", "箭头仍在y =145。"] if index == 0 else ["B与已合成箭头一起", "移到y =105。"])
            for i, value in enumerate(lines):
                body += text(panel_x+20, 451+27*i, value, 19, MUTED)
        labels = ["Same appearance, different content", "Remove the same 40 rows"] if en else ["外观相同，内容状态不同", "删除相同的40行"]
        captions = ["The left arrow is editable. The right arrow was saved into image pixels; both start at y = 145.", "After removing 40 rows, both base images move B to y = 105. Only the editable arrow stays at y = 145."] if en else ["左侧箭头仍可编辑，右侧箭头已保存成图像像素；起始均在y=145。", "删除40行后，两边底图B均移到y=105；只有可编辑箭头仍保留y=145。"]
        save(lang, f"img-crop-flattened-{step}.svg", "Crop editable and saved annotations" if en else "裁剪：可编辑标注与已合成图片", labels[step-1], captions[step-1], body,
             "Same crop and scale; compare the arrow positions." if en else "相同裁剪范围与显示比例；比较箭头的位置。", "IMG-004;IMG-006", section)

    states = [(True, True), (True, False), (False, False), (True, False), (True, True)]
    labels = ["Crop, then add a circle", "Undo 1: remove the circle", "Undo 2: restore the strip", "Redo 1: apply the crop", "Redo 2: restore the circle"] if en else ["裁剪后新画橙圈", "撤销一次：先去橙圈", "再撤销：恢复条带", "重做一次：恢复裁剪", "再重做：橙圈恢复"]
    captions = [
        "After the 40-row crop, add an orange circle. This circle is now the most recent edit.",
        "Undo removes the orange circle first. The base remains 300×160; the crop has not been undone.",
        "Undo again restores the 40 rows and the 300×200 base. The earlier purple arrow remains.",
        "Redo first reapplies the 40-row crop. The orange circle is still absent.",
        "Redo again restores the orange circle. The image remains 300×160.",
    ] if en else [
        "裁去40行后再新画橙圈；橙圈成为最近一次编辑。",
        "第一次撤销先移除橙圈；底图仍为300×160，裁剪尚未撤销。",
        "再撤销一次才恢复40行与300×200底图；此前的紫色箭头仍保留。",
        "第一次重做先恢复40行裁剪，橙圈还没有恢复。",
        "再重做一次，橙圈恢复；图像仍为300×160。",
    ]
    groups = [
        ["The crop is complete.", "The orange circle is newer."],
        ["The newest edit goes first.", "Height stays at 160 px."],
        ["Now Undo reaches the crop.", "Height returns to 200 px."],
        ["Redo reapplies the crop.", "Height returns to 160 px."],
        ["Redo restores the circle.", "Height stays at 160 px."],
    ] if en else [
        ["先完成裁剪。", "之后才新画橙圈。"],
        ["最近的橙圈先被撤销。", "高度仍为160 px。"],
        ["这次才撤销裁剪。", "高度恢复为200 px。"],
        ["先重做裁剪。", "高度重新变为160 px。"],
        ["再恢复新画的橙圈。", "高度仍为160 px。"],
    ]
    for step, (cropped, orange) in enumerate(states, 1):
        height = 160 if cropped else 200
        content = image_content(height, cropped, "editable", orange)
        body = canvas(height, content, en=en, marker=True)
        body += notes(["New edit", "Undo 1", "Undo 2", "Redo 1", "Redo 2"][step-1] if en else ["新画一笔", "撤销一次", "再撤销一次", "重做一次", "再重做一次"][step-1], groups[step-1], (cropped, orange), en)
        save(lang, f"img-crop-undo-order-{step}.svg", "Undo follows the most recent edit" if en else "裁剪后再标注：按顺序撤销", labels[step-1], captions[step-1], body,
             "Canvas history; finish text editing before using it." if en else "以下为图片画布历史；先结束文字编辑再操作。", "IMG-006", section)


with (ROOT / "artifacts/assets-editor-crop-followup.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(RECORDS[0]))
    writer.writeheader()
    writer.writerows(RECORDS)
print(f"Generated {len(RECORDS)} complementary bilingual SVGs and an independent 9-column registry.")
