#!/usr/bin/env python3
"""Reproduce the eight focused setting-operation illustrations.

Only writes the listed SVGs. The diagrams teach released behavior; they are
not screenshots and do not change an application or any acceptance ledger.
"""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path


CONTENT = {
    "set-storage-switch-no-history": {
        "zh": {
            "title": ["更换数据目录，保留原处历史"],
            "tag": "操作示意 · Windows",
            "subtitle": "目录 A 为当前目录，目录 B 为新目标。",
            "steps": [
                ("关闭迁移现有数据", ["设置 → 导出与存储 → 数据存储", "存储目录 → 选择目录", "将目标路径设为目录 B。", "迁移现有数据：关闭"]),
                ("核对范围，再开始切换", ["点击确定，阅读“更改存储目录？”。", "复制到 B：设置、打开的贴图", "留在 A：截图与已关闭贴图历史", "点击继续，等待处理结束。"]),
                ("检查当前目录和历史位置", ["当前有效目录：B", "B 中有复制的设置和打开的贴图。", "原有截图与已关闭贴图历史仍在 A。", "回到数据存储区域核对目录和占用。"]),
            ],
            "footer": "切换前，先决定是否需要一并迁移历史。",
        },
        "en": {
            "title": ["Switch folders while keeping", "history in its original location"],
            "tag": "Instructional illustration · Windows",
            "subtitle": "A is the current directory. B is the new target.",
            "steps": [
                ("Turn migration off", ["Settings → Export & storage → Data storage", "Storage directory → Choose directory", "Set the target path to directory B.", "Migrate existing data: Off"]),
                ("Check the scope, then proceed", ["Click OK. Read Change storage directory?", "Copy to B: settings and open pinned windows", "Keep in A: screenshot and closed-pin history", "Click Proceed and wait for completion."]),
                ("Check both locations", ["Current effective directory: B", "B has copied settings and open pins.", "Existing screenshot and closed-pin history", "remain in A. Check directory and usage."]),
            ],
            "footer": "Decide whether you need to move history before switching.",
        },
    },
    "set-storage-switch-cancel": {
        "zh": {
            "title": ["在二次确认中取消目录切换"],
            "tag": "操作示意 · Windows",
            "subtitle": "在开始处理前放弃，保留当前有效目录。",
            "steps": [
                ("填写目标目录草稿", ["当前有效目录为 A。", "存储目录 → 选择目录", "在弹窗中填写新目标 B。", "点击外层确定，进入下一层确认。"]),
                ("取消“更改存储目录？”", ["核对目标 B 与将要处理的数据范围。", "在这层确认中点击取消。", "此次目录切换尚未开始。"]),
                ("继续调整，或退出草稿", ["当前有效目录仍为 A。", "目录设置窗口仍可调整。", "要退出草稿，再取消目录设置窗口。", "原有数据仍由 A 提供。"]),
            ],
            "footer": "开始处理后，取消和关闭暂不可用。",
        },
        "en": {
            "title": ["Cancel the directory switch", "at the second confirmation"],
            "tag": "Instructional illustration · Windows",
            "subtitle": "Discard the switch before processing starts.",
            "steps": [
                ("Draft a new target", ["The current effective directory is A.", "Storage directory → Choose directory", "Enter directory B in the dialog.", "Click the outer OK to reach confirmation."]),
                ("Cancel the second confirmation", ["Read Change storage directory?", "Check target B and the data scope.", "Click Cancel in this confirmation.", "The directory switch has not started."]),
                ("Keep editing or leave the draft", ["The current effective directory is still A.", "You can adjust the directory-settings draft.", "To leave it, cancel that settings dialog too.", "A continues to provide the existing data."]),
            ],
            "footer": "Cancel and Close are unavailable during processing.",
        },
    },
    "set-skins-reset": {
        "zh": {
            "title": ["一次恢复整个皮肤分区"],
            "tag": "操作示意",
            "subtitle": "先核对范围，再决定确认或取消。",
            "steps": [
                ("找到皮肤分区的重置", ["设置 → 外观 → 皮肤", "点击标题右侧的重置圆箭头。", "范围：主界面、工具栏、自定义托盘菜单。"]),
                ("核对分区名称", ['确定重置"皮肤"为默认设置吗？', "确认：恢复整个皮肤分区。", "取消：保留全部当前设置。"]),
                ("确认后的结果", ["三个皮肤路径：全部清空", "三个表面的位置：恢复默认", "显示模式、不透明度：恢复默认", "模糊、遮罩：恢复默认"]),
            ],
            "footer": "只移除一个表面的背景时，清空它自己的路径。",
        },
        "en": {
            "title": ["Reset the whole Skins section"],
            "tag": "Instructional illustration",
            "subtitle": "Check the scope, then confirm or cancel.",
            "steps": [
                ("Locate the Skins reset", ["Settings → Appearance → Skins", "Click the reset arrow beside the heading.", "Surfaces: main interface, toolbars,", "and the custom tray menu."]),
                ("Check the section name", ['Reset "Skins" to default settings?', "Confirm → reset the whole Skins section.", "Cancel → keep every current setting."]),
                ("Result after confirming", ["All three skin paths: cleared", "Each surface alignment: default", "Display mode and opacity: defaults", "Blur and mask: defaults"]),
            ],
            "footer": "Clear one surface's path to remove only its background.",
        },
    },
    "set-theme-reset": {
        "zh": {
            "title": ["恢复主题、主色和字体"],
            "tag": "操作示意",
            "subtitle": "主题配置有独立的重置范围。",
            "steps": [
                ("找到主题配置的重置", ["设置 → 外观 → 主题配置", "点击标题右侧的重置圆箭头。", "此分区包括主题、主色、字体和字号。"]),
                ("核对分区名称", ['确定重置"主题配置"为默认设置吗？', "确认：恢复此分区的默认值。", "取消：保留全部当前设置。"]),
                ("确认后的结果", ["主题：跟随系统", "主题主色：默认主色", "应用字体：系统默认", "字体大小：14 px"]),
            ],
            "footer": "工具栏尺寸与皮肤在各自分区恢复。",
        },
        "en": {
            "title": ["Restore theme, accent, and font"],
            "tag": "Instructional illustration",
            "subtitle": "Theme configuration has its own reset scope.",
            "steps": [
                ("Locate the theme reset", ["Settings → Appearance", "Find Theme configuration.", "Click the reset arrow beside the heading.", "Scope: theme, accent, font, and font size."]),
                ("Check the section name", ['Reset "Theme configuration"', "to default settings?", "Confirm → restore this section's defaults.", "Cancel → keep every current setting."]),
                ("Result after confirming", ["Theme: Follow system", "Theme primary color: default", "App font: System default", "Font size: 14 px"]),
            ],
            "footer": "Toolbar size and skins use separate reset sections.",
        },
    },
}


def text(x: int, y: int, value: str, size: int = 28, color: str = "#33465e", weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def svg(data: dict) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1330" viewBox="0 0 720 1330" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(" ".join(data["title"]))}</title>',
        f'<desc id="desc">{escape(data["subtitle"])} {escape(" → ".join(s[0] for s in data["steps"]))}</desc>',
        '<rect width="720" height="1330" rx="24" fill="#f3f6fb"/>',
        '<g font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif">',
        text(32, 37, data["tag"], 22, "#58708d", 600),
    ]
    for i, line in enumerate(data["title"]):
        parts.append(text(32, 84 + i * 40, line, 32, "#172e50", 700))
    parts.append(text(32, 157, data["subtitle"], 23, "#4c6481"))
    colors = [("#eaf0ff", "#2c57a5"), ("#fff2da", "#865414"), ("#e6f6ee", "#20614a")]
    for i, (heading, lines) in enumerate(data["steps"]):
        y = 188 + i * 362
        fill, accent = colors[i]
        parts.extend([
            f'<rect x="32" y="{y}" width="656" height="316" rx="18" fill="#fff" stroke="#c8d4e4" stroke-width="2"/>',
            f'<rect x="48" y="{y+16}" width="624" height="64" rx="12" fill="{fill}"/>',
            f'<circle cx="78" cy="{y+48}" r="21" fill="{accent}"/>',
            text(71, y + 57, str(i + 1), 26, "#fff", 700),
            text(112, y + 58, heading, 28, accent, 700),
        ])
        for j, line in enumerate(lines):
            parts.append(text(58, y + 126 + j * 42, line))
        if i < 2:
            parts.append(f'<path d="M360 {y+327}v23m-10-10 10 10 10-10" fill="none" stroke="#7890ad" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append(text(32, 1284, data["footer"], 23, "#4c6481"))
    parts.extend(["</g>", "</svg>"])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    for stem, languages in CONTENT.items():
        for lang, data in languages.items():
            directory = args.root / "docs/public/images/guides"
            if lang == "en":
                directory /= "en"
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f"{stem}.svg").write_text(svg(data), encoding="utf-8")
    print("Generated 8 bilingual setting-operation SVGs.")


if __name__ == "__main__":
    main()
