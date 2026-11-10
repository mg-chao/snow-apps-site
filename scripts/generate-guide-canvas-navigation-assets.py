"""Render bilingual canvas-viewport teaching frames from one affine model.

This writes only its twelve SVGs and its independent registry/model artifacts.
It does not update coverage, acceptance, localization catalogs, or other assets.
"""

from pathlib import Path
from html import escape
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/public/images/guides"
ARTIFACTS = ROOT / "artifacts"
WIDTH, HEIGHT = 960, 600
SCENE_X, SCENE_Y, SCENE_W, SCENE_H = 60, 154, 840, 280
INK, MUTED, PURPLE, BLUE = "#24384f", "#536b83", "#7946cb", "#267cba"
SOURCE = (
    "f02f50e:snow_shot/src/presentation/globalcanvas/globalcanvascontroller.cpp:"
    "506-526,614-687; snow_shot/src/shortcuts/shortcutbinding.cpp:214-220,345-349"
)


def text(x, y, value, size=22, color=INK, weight=400, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def rect(x, y, width, height, fill="white", stroke="#c8d3e6", radius=10, extra=""):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>'
    )


def line(x, y, xx, yy, color=BLUE, width=3, extra=""):
    return (
        f'<path d="M{x} {y} L{xx} {yy}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round" {extra}/>'
    )


def arrow(x, y, xx, yy, color=BLUE, width=4, head=12):
    length = math.hypot(xx-x, yy-y)
    ux, uy = (xx-x)/length, (yy-y)/length
    return line(x, y, xx, yy, color, width) + (
        f'<path d="M{xx-head*ux+head*.6*uy} {yy-head*uy-head*.6*ux} '
        f'L{xx} {yy} L{xx-head*ux-head*.6*uy} {yy-head*uy+head*.6*ux}" '
        f'fill="none" stroke="{color}" stroke-width="{width}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def fixed_application(en):
    """The exact same geometry and content is reused in all six frames."""
    out = rect(0, 0, SCENE_W, SCENE_H, "#fff", "#aebdd0", 8)
    out += rect(1, 1, SCENE_W-2, 42, "#e8edf4", "none", 7)
    out += text(20, 30, "Application underneath — fixed" if en else "下方应用内容：保持不动", 21, MUTED, 600)
    out += rect(22, 63, 112, 188, "#f1f4f8", "none", 6)
    for y, width in [(85, 76), (113, 62), (141, 75), (169, 54), (197, 68)]:
        out += line(39, y, 39+width, y, "#ccd5df", 6)
    for x, letter, fill in [(170, "A", "#e5eef7"), (510, "B", "#e3eee9")]:
        out += rect(x, 99, 120, 82, fill, "#b5c5d4", 4)
        out += text(x+60, 155, letter, 36, INK, 700, "middle")
    out += line(175, 222, 350, 222, "#d5dee8", 9)
    out += line(515, 222, 690, 222, "#d5dee8", 9)
    return out


def annotation_layer(transform, ghost=False):
    scale, tx, ty = transform
    # These marks are never edited individually: only this shared transform changes.
    extra = ' opacity=".32" stroke-dasharray="6 5"' if ghost else ""
    return (
        f'<g transform="translate({tx:.9f} {ty:.9f}) scale({scale:.9f})"{extra}>'
        f'<ellipse cx="230" cy="140" rx="78" ry="59" fill="none" stroke="{PURPLE}" stroke-width="4"/>'
        + arrow(415, 205, 559, 158, PURPLE, 5)
        + "</g>"
    )


def pointer(x, y):
    # The ring center is the pointer anchor; it remains fixed during the zoom.
    return (
        f'<circle cx="{x}" cy="{y}" r="8" fill="white" stroke="{BLUE}" stroke-width="2.5"/>'
        + line(x-13, y, x+13, y, BLUE, 1.8)
        + line(x, y-13, x, y+13, BLUE, 1.8)
    )


def mouse(x, y, held=False):
    color = BLUE if held else MUTED
    out = rect(x-13, y-21, 26, 41, "white", color, 12)
    out += line(x-12, y-6, x+12, y-6, color, 1.3)
    out += rect(x-3, y-16, 6, 15, BLUE if held else "white", color, 3)
    return out


zoom = math.exp(120 * .001)
anchor = (230.0, 140.0)
zoomed = (zoom, anchor[0]*(1-zoom), anchor[1]*(1-zoom))
horizontal = (zoom, zoomed[1]+40, zoomed[2])
vertical = (zoom, horizontal[1], horizontal[2]+40)
dragged = (zoom, vertical[1]-60, vertical[2]-30)
TRANSFORMS = [(1.0, 0.0, 0.0), zoomed, horizontal, vertical, dragged, dragged]
IDS = ["IMG-046;IMG-047;IMG-048;IMG-049", "IMG-046", "IMG-047", "IMG-048", "IMG-049", "IMG-049"]
LABELS = {
    "zh": ["准备：关闭穿透", "围绕指针缩放", "Shift：水平平移", "组合键：垂直平移", "按住中键拖动", "松开中键结束"],
    "en": ["Prepare the drawing layer", "Zoom around the pointer", "Shift: pan horizontally", "Pan vertically", "Hold the middle button and drag", "Release the middle button"],
}
CAPTIONS = {
    "zh": [
        "关闭鼠标穿透，结束文字编辑与取色，切到选择元素。紫色圈与箭头属于标注层，A、B属于下方应用。",
        "指向A中心，按住Windows的Ctrl或macOS的Command向上滚动；本例100%约变为113%。指针下的标注位置不动，周围标注随整层缩放。",
        "松开缩放组合键，改按Shift滚动。本例紫色圈与箭头一起向右40 px；A、B不动。",
        "按住Windows的Ctrl+Shift或macOS的Command+Shift滚动。本例整层向下40 px，比例与下方应用不变。",
        "只按住鼠标中键，从虚线鼠标处向左60 px、向上30 px拖动；圈与箭头随指针一起平移。",
        "松开中键结束拖动，标注层停在新位置；没有新增标注，下方应用仍保持原位。",
    ],
    "en": [
        "Disable click-through, finish text editing and color sampling, then choose Select elements. The purple ring and arrow are annotations; A and B belong to the application underneath.",
        "Point at the center of A, hold Ctrl on Windows or Command on macOS, and scroll up. This example changes 100% to about 113%. The annotation point under the pointer stays fixed while the layer scales around it.",
        "Release the zoom modifier, hold Shift, and scroll. Here the ring and arrow both move 40 px right; A and B stay fixed.",
        "Hold Ctrl+Shift on Windows or Command+Shift on macOS and scroll. Here the whole layer moves 40 px down, with no change to its scale or the application underneath.",
        "Hold only the middle mouse button and drag from the dashed mouse position 60 px left and 30 px up. Both annotations follow the pointer.",
        "Release the middle button to finish. The layer stays at its new position; no annotation is added and the underlying application remains fixed.",
    ],
}
ACTIONS = {
    "zh": ["关闭穿透 · 选择元素", "Ctrl / Command + 滚轮 ↑", "Shift + 滚轮 ↑", "Ctrl+Shift / Command+Shift + 滚轮 ↑", "按住中键：向左、向上拖动", "松开中键：停在当前位置"],
    "en": ["Click-through off · Select elements", "Ctrl / Command + wheel ↑", "Shift + wheel ↑", "Ctrl+Shift / Command+Shift + wheel ↑", "Middle button held: drag left and up", "Middle button released: keep this view"],
}
RESULTS = {
    "zh": [
        ["A、B位置固定；紫色是标注层。", "接下来只改变标注层的观看位置与比例。"],
        ["100% → 约113%；蓝色十字为指针。", "A中心的标注点不动；圈变大，箭头远离指针。"],
        ["本例：整层向右40 px。", "圈和箭头一起移动；A、B都没有移动。"],
        ["本例：整层向下40 px。", "只改变位置，不改变上一帧的缩放比例。"],
        ["从虚线鼠标拖到实线鼠标：左60、上30 px。", "两处标注一起移动，彼此关系不变。"],
        ["中键已松开，拖动结束。", "位置与上一帧相同；没有新画任何标注。"],
    ],
    "en": [
        ["A and B stay fixed; purple marks are annotations.", "Only the layer's view will move or scale."],
        ["100% → about 113%; blue cross = pointer.", "The anchor stays fixed; the ring and arrow scale around it."],
        ["Here: the whole layer moves 40 px right.", "Both annotations move together; A and B stay fixed."],
        ["Here: the whole layer moves 40 px down.", "Its scale stays the same as in the preceding frame."],
        ["Dashed mouse → solid mouse: 60 px left, 30 px up.", "Both marks move together, retaining their relative positions."],
        ["The middle button is released; dragging ends.", "Same position as before; no new annotation is drawn."],
    ],
}


def render(lang, index):
    en = lang == "en"
    title = "Navigate the annotation layer" if en else "缩放与平移：只改变标注层"
    kind = "Instructional illustration" if en else "操作示意"
    body = text(32, 43, title, 29, INK, 700)
    body += text(928, 42, f"{index+1} / 6", 22, MUTED, 600, "end")
    body += text(32, 82, ACTIONS[lang][index], 25, BLUE, 650)
    body += text(32, 124, "Application: fixed · Purple: annotation layer" if en else "应用内容固定不动 · 紫色：标注层", 22, MUTED)
    body += f'<g transform="translate({SCENE_X} {SCENE_Y})">'
    body += '<g id="fixed-application">' + fixed_application(en) + "</g>"
    body += '<g clip-path="url(#scene-clip)">'
    if index in [1, 2, 3, 4]:
        body += annotation_layer(TRANSFORMS[index-1], ghost=True)
    body += '<g id="annotation-layer">' + annotation_layer(TRANSFORMS[index]) + "</g>"
    if index in [0, 1]:
        body += pointer(*anchor)
    if index == 2:
        body += arrow(320, 70, 360, 70, BLUE, 3, 8) + text(382, 77, "+40 px", 21, BLUE, 600)
    if index == 3:
        body += arrow(370, 80, 370, 120, BLUE, 3, 8) + text(390, 108, "+40 px", 21, BLUE, 600)
    if index in [4, 5]:
        if index == 4:
            body += '<g opacity=".45" stroke-dasharray="4 3">' + mouse(727, 244) + "</g>"
            body += arrow(713, 237, 679, 219, BLUE, 2.5, 7)
        body += mouse(667, 214, index == 4)
    body += "</g></g>"
    for row, value in enumerate(RESULTS[lang][index]):
        body += text(32, 479+31*row, value, 23, INK, 600 if row == 0 else 400)
    body += line(32, 538, 928, 538, "#dbe3ef", 1)
    body += text(32, 568, "Dashed purple = previous view" if en else "紫色虚线：上一帧位置", 19, MUTED)
    body += text(928, 568, kind, 19, MUTED, anchor="end")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title+": "+LABELS[lang][index])}</title>'
        f'<desc id="desc">{escape(kind+". "+CAPTIONS[lang][index])}</desc>'
        '<defs><clipPath id="scene-clip"><rect x="0" y="0" width="840" height="280" rx="8"/></clipPath></defs>'
        '<rect width="960" height="600" rx="20" fill="#f5f7fc"/>'
        '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">'
        + body + "</g></svg>"
    )


def main():
    records, frame_facts = [], []
    for lang in ["zh", "en"]:
        section = "zoom-and-pan-the-annotation-layer" if lang == "en" else "缩放与平移标注层"
        for index, transform in enumerate(TRANSFORMS):
            asset = PUBLIC / ("en" if lang == "en" else "") / f"img-canvas-navigation-{index+1}.svg"
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_text(render(lang, index), encoding="utf-8")
            records.append({
                "Asset": asset.relative_to(ROOT).as_posix(),
                "Feature IDs": IDS[index],
                "Teaching purpose": CAPTIONS[lang][index],
                "Documentation path": f"docs/{lang}/guides/image-editing/canvas.mdx#{section}",
                "Associated step": LABELS[lang][index],
                "Source": SOURCE,
                "Production method": "原创双语SVG；scripts/generate-guide-canvas-navigation-assets.py；同一固定应用底层与单一仿射标注层；精确角度步120、缩放exp(0.12)、平移40px，中键差量(-60,-30)",
                "Status": "已制作教学示意；不构成普通UI运行或验收通过证据",
                "Capture prerequisites and next action": "核对两语播放/移动端布局；后续在普通UI独立验证每个手势与平台绑定，不扩大现有运行或验收状态",
            })
            frame_facts.append({
                "asset": asset.relative_to(ROOT).as_posix(),
                "feature_ids": IDS[index].split(";"),
                "scale": transform[0], "translation": list(transform[1:]),
                "ring_center": [230*transform[0]+transform[1], 140*transform[0]+transform[2]],
                "middle_held": index == 4,
                "application_A": [230, 140], "application_B": [570, 140],
            })
    ARTIFACTS.mkdir(exist_ok=True)
    with (ARTIFACTS / "assets-canvas-navigation-20261110.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    (ARTIFACTS / "canvas-navigation-frame-model-20261110.json").write_text(json.dumps({
        "source": SOURCE,
        "ordinary_angle_delta_y": 120,
        "zoom_formula": "clamp(previousScale * exp(delta * 0.001), 0.1, 8)",
        "non_precise_pan_formula": "delta / 120 * 40 view pixels",
        "precise_pan_formula": "pixelDelta.y, falling back to pixelDelta.x when y=0",
        "middle_drag_delta": [-60, -30],
        "frame_facts": frame_facts,
        "runtime_evidence": False,
    }, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Generated {len(records)} bilingual SVGs and an independent 9-column registry.")


if __name__ == "__main__":
    main()
