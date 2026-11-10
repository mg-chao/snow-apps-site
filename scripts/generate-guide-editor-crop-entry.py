"""Draw an identification card using the released product's exact crop glyph paths."""
from pathlib import Path
from html import escape
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/public/images/guides"
SOURCE = "f02f50e snow_shot/src/presentation/components/icons/resources/"
GLYPHS = (
    ("crop-vertical.svg",
     "M164 348V172a36 36 0 0 1 36-36h624a36 36 0 0 1 36 36v176M164 676v176a36 36 0 0 0 36 36h624a36 36 0 0 0 36-36V676",
     "M128 512h128m192 0h128m192 0h128"),
    ("crop-horizontal.svg",
     "M348 164H172a36 36 0 0 0-36 36v624a36 36 0 0 0 36 36h176M676 164h176a36 36 0 0 1 36 36v624a36 36 0 0 1-36 36H676",
     "M512 128v128m0 192v128m0 192v128"),
)


def text(x, y, value, size=22, color="#334155", weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


rows = []
for en in (False, True):
    title = "Find the crop tools" if en else "辨认裁剪工具"
    subtitle = "Image editor · floating main toolbar" if en else "图像编辑器 · 浮动主工具条"
    labels = ("Vertical crop", "Horizontal crop") if en else ("垂直裁剪", "水平裁剪")
    descriptions = (
        ("Drag down/up; remove full rows.", "Full-width horizontal strip."),
        ("Drag left/right; remove full columns.", "Full-height vertical strip."),
    ) if en else (
        ("沿高度方向拖动，删除整行。", "红色横带贯穿图片宽度。"),
        ("沿宽度方向拖动，删除整列。", "红色竖带贯穿图片高度。"),
    )
    body = text(24, 46, title, 32, "#1e293b", 700) + text(24, 79, subtitle, 20, "#53627d")
    for i, (_, path1, path2) in enumerate(GLYPHS):
        y = 108 + i * 180
        body += f'<rect x="24" y="{y}" width="592" height="164" rx="14" fill="#fff" stroke="#c8d3e6" stroke-width="2"/>'
        body += f'<rect x="43" y="{y+28}" width="108" height="108" rx="12" fill="#edf2fa"/>'
        body += f'<g transform="translate(55 {y+40}) scale(0.08203125)" fill="none" stroke="#334155" stroke-width="72" stroke-linecap="round"><path d="{path1}"/><path d="{path2}"/></g>'
        body += text(177, y + 48, labels[i], 28, "#6146bd", 600)
        body += text(177, y + 92, descriptions[i][0], 21)
        body += text(177, y + 127, descriptions[i][1], 21)
    footer = "Instructional illustration · hover to check tool names" if en else "操作示意 · 悬停图标核对名称"
    body += text(24, 495, footer, 19, "#53627d")
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 520" role="img" aria-labelledby="title desc">'
    svg += f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}. {escape(footer)}.</desc>'
    svg += '<rect width="640" height="520" rx="20" fill="#f5f7fc"/><g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">' + body + '</g></svg>\n'
    path = OUT / ("en/img-crop-tool-icons.svg" if en else "img-crop-tool-icons.svg")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    rows.append({
        "Asset": path.relative_to(ROOT).as_posix(),
        "Feature IDs": "IMG-004;IMG-005",
        "Teaching purpose": "辨认浮动主工具条的两枚相邻裁剪图标；横虚线删整行，竖虚线删整列",
        "Documentation path": f"docs/{'en' if en else 'zh'}/guides/image-editing/editor.mdx",
        "Associated step": "选择垂直或水平裁剪工具前",
        "Source": SOURCE + "crop-vertical.svg; " + SOURCE + "crop-horizontal.svg; f02f50e screenshottoolpalette.cpp:6626-6653; artifacts/research-release-editor-crop.md",
        "Production method": "原创辨认卡复用两枚实际产品SVG路径；只呈现图标与名称，不重建未知工具条布局，不是应用截图或录屏",
        "Status": "已制作操作示意；产品普通UI操作验收独立保留",
        "Capture prerequisites and next action": "如后续取得原生工具条截图可替换辨认卡；不因此提升工具点击或裁剪结果的实操证据",
    })

with (ROOT / "artifacts/assets-editor-crop-entry.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print("Generated two bilingual crop-icon identification cards.")
