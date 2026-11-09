"""Generate bilingual crop illustrations from the documented pixel geometry."""

from pathlib import Path
from html import escape
import csv
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/public/images/guides"
INK = "#24384f"
MUTED = "#536b83"
BLUE = "#2877bd"
PURPLE = "#7154d9"
GREEN = "#258568"
RED = "#d84d53"
ROWS = []


def text(x, y, value, size=20, color=INK, weight=400, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def rect(x, y, w, h, fill="white", stroke="#c8d3e6", radius=8, extra=""):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>'
    )


def line(x, y, xx, yy, color=BLUE, width=2, dash=""):
    return (
        f'<path d="M{x} {y} L{xx} {yy}" fill="none" stroke="{color}" '
        f'stroke-width="{width}"'
        + (f' stroke-dasharray="{dash}"' if dash else "")
        + "/>"
    )


def arrow(x, y, xx, yy, color=PURPLE, width=3):
    return line(x, y, xx, yy, color, width) + (
        f'<path d="M{xx-10} {yy-6} L{xx} {yy} L{xx-10} {yy+6}" '
        f'fill="none" stroke="{color}" stroke-width="{width}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def wrap(value, width=240, size=20):
    """Wrap at words where possible, accounting for full-width glyphs."""
    result, current, units, gap = [], "", 0.0, ""
    limit = width / size
    for token in re.findall(r"\s+|[^\s\u3400-\u9fff]+|[\u3400-\u9fff]", value):
        if token.isspace():
            gap = " " if current else ""
            continue
        cost = sum(1 if unicodedata.east_asian_width(c) in "WF" else .55 for c in gap + token)
        if current and units + cost > limit and token not in "，。；：！？、）】》」』":
            result.append(current)
            current, units, gap = "", 0.0, ""
            cost = sum(1 if unicodedata.east_asian_width(c) in "WF" else .55 for c in token)
        current += gap + token
        units += cost
        gap = ""
    if current.strip():
        result.append(current.strip())
    return result


def notes(title, groups):
    body = rect(644, 98, 288, 396)
    body += text(666, 134, title, 22, PURPLE, 650)
    y = 182
    for group in groups:
        for row in wrap(group):
            body += text(666, y, row, 20)
            y += 28
        y += 22
    assert y <= 493, (title, groups, y)
    return body


def save(lang, name, title, subtitle, label, caption, body, footer, feature_ids):
    out = PUBLIC / ("en" if lang == "en" else "") / name
    out.parent.mkdir(parents=True, exist_ok=True)
    source_label = "Instructional illustration" if lang == "en" else "操作示意"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="560" '
        'viewBox="0 0 960 560" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title + ": " + label)}</title>'
        f'<desc id="desc">{escape(source_label + ". " + caption)}</desc>'
        '<rect width="960" height="560" rx="20" fill="#f5f7fc"/>'
        '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">'
        + text(28, 42, title, 28, INK, 700)
        + text(28, 77, subtitle, 19, MUTED)
        + body
        + line(28, 509, 932, 509, "#dbe3ef", 1)
        + text(28, 539, footer, 18, MUTED)
        + text(930, 539, source_label, 17, MUTED, anchor="end")
        + "</g></svg>"
    )
    out.write_text(svg, encoding="utf-8")
    ROWS.append({
        "Asset": out.relative_to(ROOT).as_posix(),
        "Feature IDs": feature_ids,
        "Teaching purpose": caption,
        "Documentation path": f"docs/{lang}/guides/image-editing/editor.mdx",
        "Associated step": label,
        "Source": (
            "artifacts/research-release-editor-crop.md; f02f50e "
            "imageeditingcanvas.cpp:71-143,228-300; imageeditingdocument.cpp:44-110,165-254; "
            "imageediting_tests.cpp:1798-1826"
        ),
        "Production method": (
            "原创双语SVG scripts/generate-guide-editor-crop-assets.py；固定源像素几何，"
            "不仿造工具条或未经核实的原生UI，不修改应用图片"
        ),
        "Status": "已制作操作示意；不是实际应用截图；普通UI实操及既有验收状态不变",
        "Capture prerequisites and next action": (
            "自有本地图片、普通UI浮动裁剪工具条；后续核对实际预览Npx、松开提交、取消及保存尺寸。"
            "行裁剪旧预览和取消专项图的缺口不由此关闭；源清单与验收状态保持。"
        ),
    })


def columns(stage, en):
    # Source pixels: A=[0,120), blank=[120,180), B=[180,300), height=180.
    scale, x, y = 1.8, 56, 136
    cropped = stage == 3
    width = 240 if cropped else 300
    body = rect(28, 98, 592, 396)
    body += text(x, 121, f"{width} × 180 px", 19, MUTED, 600)
    content = rect(0, 0, width, 180, "#fff", "#aabbd2", 0)
    content += rect(0, 0, 120, 180, "#e5effa", "none", 0)
    content += rect(120 if cropped else 180, 0, 120, 180, "#dcefe9", "none", 0)
    content += text(60, 95, "A", 42, BLUE, 700, "middle")
    content += text(180 if cropped else 240, 95, "B", 42, GREEN, 700, "middle")
    if stage == 2:
        content += rect(120, 0, 60, 180, "#df5961", "none", 0, 'opacity=".85"')
        content += line(120, 0, 120, 180, BLUE, 1.5, "4 3")
        content += line(180, 0, 180, 180, BLUE, 1.5, "4 3")
        content += text(150, 58, "60 px", 15, "white", 700, "middle")
        content += arrow(124, 125, 176, 125, "white", 2)
    elif cropped:
        content += line(120, 0, 120, 180, PURPLE, 1.5, "4 3")
    body += f'<g transform="translate({x} {y}) scale({scale})">{content}</g>'
    ticks = [0, 120, 240] if cropped else [0, 120, 180, 300]
    for value in ticks:
        xx = x + value * scale
        body += line(xx, 463, xx, 470, MUTED, 1)
        body += text(xx, 489, str(value), 16, MUTED, anchor="middle")
    if cropped:
        body += line(x + 300*scale, y, x + 300*scale, 460, "#aabbd2", 1, "5 5")
    groups = [
        ["Keep A and B.", "Blank strip: 60 columns.", "Image height: 180 px."],
        ["Drag horizontally.", "N = 60 px across the full height.", "Release to apply."],
        ["Width: 300 → 240 px.", "B moves left by 60 px.", "The seam is at x = 120."],
    ] if en else [
        ["保留 A 与 B。", "空白条带占 60 列。", "图像高度为 180 px。"],
        ["按住左键横向拖动。", "N = 60 px，贯穿整图高度。", "松开左键即提交。"],
        ["宽度：300 → 240 px。", "B 向左接合 60 px。", "接缝位于 x = 120。"],
    ]
    return body + notes("Horizontal crop" if en else "水平裁剪", groups[stage-1])


def history(stage, en):
    # Same canvas origin/scale throughout. Crop source y=[80,120), 40 rows.
    # The base B center moves 145->105; editable arrow y=145 never changes.
    scale, x, y = 1.6, 80, 136
    cropped = stage in [2, 4]
    height, b_y = (160, 105) if cropped else (200, 145)
    body = rect(28, 98, 592, 396)
    body += text(x, 121, f"300 × {height} px", 19, MUTED, 600)
    if cropped:
        body += rect(x, y, 480, 320, "none", "#aabbd2", 0, 'stroke-dasharray="5 5"')
    content = rect(0, 0, 300, height, "white", "#aabbd2", 0)
    content += rect(20, 20, 110, 40, "#e5effa", "none", 0)
    content += text(36, 49, "A", 25, BLUE, 700)
    content += rect(20, b_y-15, 260, 30, "#dcefe9", "none", 0)
    content += text(36, b_y+9, "B", 25, GREEN, 700)
    content += line(0, 145, 300, 145, PURPLE, 1, "4 4")
    content += arrow(160, 145, 260, 145, PURPLE, 3)
    if cropped:
        content += line(0, 80, 300, 80, RED, 1.2, "4 3")
    body += f'<g transform="translate({x} {y}) scale({scale})">{content}</g>'
    body += text(66, y+5, "0", 16, MUTED, anchor="end")
    body += text(66, y+145*scale+5, "145", 16, PURPLE, anchor="end")
    body += text(66, y+height*scale+5, str(height), 16, MUTED, anchor="end")
    body += text(86, 486, "A / B: image pixels" if en else "A / B：底图像素", 18, MUTED)
    body += arrow(318, 480, 362, 480, PURPLE, 2)
    body += text(374, 486, "Editable" if en else "可编辑标注", 18, PURPLE)
    groups = [
        ["B center: y = 145.", "Arrow: y = 145.", "Next: remove y = 80–120 (40 px)."],
        ["B: y = 145 → 105.", "Arrow stays at y = 145.", "Height: 200 → 160 px."],
        ["Undo restores 40 rows.", "B returns to y = 145.", "Arrow stays at y = 145."],
        ["Redo removes 40 rows.", "B returns to y = 105.", "Arrow stays at y = 145."],
    ] if en else [
        ["B 中心：y = 145。", "箭头：y = 145。", "下一步删除 y = 80–120 的 40 px 条带。"],
        ["B：y = 145 → 105。", "箭头仍为 y = 145。", "高度：200 → 160 px。"],
        ["撤销恢复 40 行。", "B 回到 y = 145。", "箭头仍为 y = 145。"],
        ["重做再次删除 40 行。", "B 回到 y = 105。", "箭头仍为 y = 145。"],
    ]
    action = ["Baseline", "Crop applied", "Undo crop", "Redo crop"] if en else ["标注基线", "裁剪已提交", "撤销裁剪", "重做裁剪"]
    return body + notes(action[stage-1], groups[stage-1])


for lang in ["zh", "en"]:
    en = lang == "en"
    for step in range(1, 4):
        labels = ["Inspect the original", "Preview 60 columns", "Inspect the join"] if en else ["查看原图", "预览 60 列条带", "检查左右接合"]
        captions = [
            "The 300×180 image contains A, a 60 px blank strip, and B.",
            "Drag horizontally to preview 60 full-height columns. Release to remove them.",
            "The output is 240×180. A and B join at x=120; B shifted left by 60 px.",
        ] if en else [
            "300×180 的原图包含 A、中间 60 px 空白条带与 B。",
            "横向拖动预览贯穿整高的 60 列；松开左键删除这些列。",
            "结果为 240×180；A 与 B 在 x=120 处接合，B 左移 60 px。",
        ]
        save(lang, f"img-crop-columns-{step}.svg",
             "Horizontal crop: remove columns" if en else "水平裁剪：删除整列",
             labels[step-1], labels[step-1], captions[step-1], columns(step, en),
             "Source pixels: the view scale stays fixed." if en else "数值为源图像像素；各帧保持相同显示比例。", "IMG-005")
    for step in range(1, 5):
        labels = ["Keep an editable marker", "Crop beneath annotations", "Undo the crop", "Redo the crop"] if en else ["保留可编辑标注基线", "裁剪底图，标注不动", "撤销恢复底图", "重做恢复裁剪"]
        captions = [
            "The base B and editable purple arrow meet at y=145 in a 300×200 image.",
            "Removing 40 rows moves base B to y=105. The arrow remains at y=145; height is 160.",
            "With no intervening edit, Undo restores the 300×200 base and B at y=145.",
            "Redo restores the 300×160 crop. Base B returns to y=105; the arrow stays at y=145.",
        ] if en else [
            "300×200 底图中的 B 与本次可编辑紫色箭头在 y=145 处对齐。",
            "删除 40 行后，底图 B 移至 y=105；箭头仍在 y=145，图像高度变为160。",
            "裁剪后未插入其他编辑时，撤销恢复300×200底图，B回到y=145。",
            "重做恢复300×160裁剪结果；B回到y=105，箭头仍在y=145。",
        ]
        save(lang, f"img-crop-history-{step}.svg",
             "Crop history and editable annotations" if en else "裁剪历史与可编辑标注",
             labels[step-1], labels[step-1], captions[step-1], history(step, en),
             "Same origin and scale; the purple arrow is editable." if en else "原点和显示比例不变；紫色箭头是本次可编辑标注。", "IMG-004;IMG-006")

with (ROOT / "artifacts/assets-editor-crop-diagrams.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(ROWS[0]))
    writer.writeheader()
    writer.writerows(ROWS)
print(f"Generated {len(ROWS)} bilingual crop diagrams and one independent source registry.")
