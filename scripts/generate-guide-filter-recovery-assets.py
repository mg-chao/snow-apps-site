"""Source-backed Auto Filter recovery states, without inventing detection output."""

from pathlib import Path
from xml.sax.saxutils import escape
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/public/images/guides'
INK, BLUE, RED = '#24384f', '#2877bd', '#c53b45'


def text(x, y, value, size=21, color=INK):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(value)}</text>'


def rect(x, y, w, h, fill='white', stroke='#b9cce0'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}"/>'


records = []
steps = [
    ('识别失败', '确认提示，再切换工具重试', '失败提示不是识别结果；此时不能按类别填充。'),
    ('切换工具', '先选矩形滤镜，再返回自动滤镜', '不是寻找“重试”按钮；重新进入工具会再次检测。'),
    ('重新扫描', '返回自动滤镜后等待扫描', '等待当前图像的真实检测结果，不预设区域或类别。'),
]
for i, (label, subtitle, footer) in enumerate(steps, 1):
    active = '矩形滤镜' if i == 2 else '自动滤镜'
    body = rect(36, 92, 688, 48, '#edf4fb')
    body += text(52, 123, '滤镜', 20)
    for x, name in [(140, '画笔滤镜'), (300, '矩形滤镜'), (460, '自动滤镜')]:
        chosen = name == active
        body += rect(x, 99, 145, 34, '#d8eafb' if chosen else 'white', BLUE if chosen else '#b9cce0')
        body += text(x + 23, 123, name, 19, BLUE if chosen else INK)
    body += rect(45, 160, 430, 176)
    body += text(66, 190, '已加载的虚构图像', 18, '#536c86')
    body += rect(67, 208, 55, 55, '#c5dcee')
    body += text(142, 231, '示例消息', 22)
    body += text(142, 260, '只展示恢复流程', 18, '#536c86')
    body += rect(503, 163, 201, 44, '#eef1f4', '#ccd3da')
    body += text(543, 192, '填充区域', 22, '#657887')
    if i == 1:
        body += rect(56, 279, 642, 42, '#fff0f0', '#dc9aa0')
        body += text(73, 307, '区域识别失败。请再次尝试自动滤镜', 24, RED)
        body += text(514, 241, '尚无可用识别区域', 18, '#536c86')
    elif i == 2:
        body += text(506, 247, '下一步：', 19)
        body += text(506, 277, '选择自动滤镜', 22, BLUE)
        body += '<path d="M534 286 V303 H661 V141" fill="none" stroke="#2877bd" stroke-width="3"/>'
        body += '<path d="M653 154 L661 141 L669 154" fill="none" stroke="#2877bd" stroke-width="3"/>'
    else:
        body += '<defs><linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4096ff" stop-opacity="0"/><stop offset=".8" stop-color="#60dcff" stop-opacity=".55"/><stop offset="1" stop-color="#4096ff" stop-opacity="0"/></linearGradient></defs>'
        body += '<rect x="46" y="264" width="428" height="38" fill="url(#scan)"/>'
        body += text(509, 247, '等待扫描结束', 21, BLUE)
        body += text(509, 279, '再检查真实区域', 18, '#536c86')
    filename = f'ann-filter-retry-{i}.svg'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="430" viewBox="0 0 760 430" role="img" aria-labelledby="title desc" font-family="system-ui,sans-serif"><title id="title">自动滤镜：{escape(label)}</title><desc id="desc">源码核对的教学重建，非应用截图或录屏。{escape(footer)}</desc><rect width="760" height="430" rx="12" fill="#f3f7fc"/>{text(24, 34, "自动滤镜识别失败后重试", 25)}{text(24, 63, subtitle, 18, "#536c86")}{body}{text(24, 370, footer, 19)}{text(24, 412, "教学示意，非应用录屏；控件布局为流程示意", 15, "#536c86")}</svg>'
    (OUT / filename).write_text(svg)
    records.append({
        'Asset': filename,
        'Feature group': 'annotations/filters',
        'Teaching purpose and step': f'{i}. {label}',
        'Documentation path': 'docs/zh/guides/annotations/filters.mdx',
        'Source and production method': 'v1.5.2_snow-shot f02f50e：screenshotautofiltercontroller.cpp:244-338；imageeditingwindow.cpp:367-373；capture_zh_CN.ts:26-27；手工专属SVG重建；scripts/generate-guide-filter-recovery-assets.py',
        'Caption': '教学示意，非应用录屏；未复现实际失败，未伪造识别结果',
        'Status': '已制作；三帧原尺寸浏览器渲染与逐图检查通过；独立源码/视觉复核通过；未声称实际错误复现',
        'Feature IDs': 'ANN-066',
    })

registry = ROOT / 'artifacts/assets-annotations.csv'
with registry.open(newline='') as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames
    rows = [row for row in reader if not row['Asset'].startswith('ann-filter-retry-')]
with registry.open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows + records)
print(f'Produced {len(records)} dedicated recovery states and registered them.')
