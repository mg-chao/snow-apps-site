"""Draw a source-backed formula editing example, not an application recording."""
from html import escape
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/public/images/guides'


def text(x, y, value, size=22, color='#18233b', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def box(y, height):
    return f'<rect x="24" y="{y}" width="392" height="{height}" rx="14" fill="#fff" stroke="#c8d3e6" stroke-width="2"/>'


def formula(y, subscript):
    return (f'<text x="141" y="{y}" font-size="32" fill="#18233b">x'
            f'<tspan baseline-shift="sub" font-size="20">{subscript}</tspan>'
            '<tspan baseline-shift="baseline"> + y</tspan>'
            '<tspan baseline-shift="sub" font-size="20">1</tspan></text>'
            f'<path d="M130 {y+12} H302" stroke="#18233b" stroke-width="2"/>'
            + text(204, y+46, '2', 30))


rows = []
for locale in ('zh', 'en'):
    en = locale == 'en'
    titles = (['Find the wrong subscript', 'Replace l with 1', 'Undo the source edit', 'Redo the correction']
              if en else ['找出下标错误', '把字母 l 改为数字 1', '撤销这次源码修改', '重做，恢复正确下标'])
    labels = (['Original formula', 'Current LaTeX source', 'Preview after updating']
              if en else ['原始公式', '当前 LaTeX 公式源码', '内容更新后的公式预览'])
    actions = (['Compare l with the original 1.', 'Edit the source, then wait.', 'Undo restores the earlier l.', 'Redo restores the corrected 1.']
               if en else ['对照原图：这里应为数字 1。', '修改源码后，等待预览更新。', '撤销后，原来的 l 再次出现。', '重做后，正确的 1 恢复。'])
    for index, subscript in enumerate(('l', '1', 'l', '1'), 1):
        title = titles[index-1]
        source = r'\frac{x_' + subscript + r'+y_1}{2}'
        body = text(24, 43, title, 25, weight=700)
        body += box(68, 112) + text(42, 96, labels[0], 19, '#53627d') + formula(124, '1')
        body += box(198, 140) + text(42, 228, labels[1], 19, '#53627d')
        body += f'<rect x="153" y="245" width="18" height="30" rx="3" fill="{"#fff0de" if subscript=="l" else "#e1f5ed"}"/>'
        body += '<g font-family="Menlo,Consolas,monospace">' + text(42, 268, source, 23, '#2563c6') + '</g>'
        body += text(42, 309, actions[index-1], 18, '#53627d')
        body += box(356, 162) + text(42, 387, labels[2], 19, '#53627d') + formula(440, subscript)
        body += text(24, 558, 'Instructional illustration' if en else '操作示意', 18, '#53627d')
        body += text(24, 588, f'{index} / 4', 18, '#53627d')
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 610" role="img" aria-labelledby="title desc">'
               f'<title id="title">{escape(title)}</title><desc id="desc">{escape(actions[index-1])}</desc>'
               '<rect width="440" height="610" rx="20" fill="#f5f7fc"/>'
               '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">' + body + '</g></svg>')
        relative = f'{"en/" if en else ""}rec-formula-edit-{index}.svg'
        path = OUT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg)
        rows.append({
            'Asset': path.relative_to(ROOT).as_posix(),
            'Feature IDs': 'OCR-038;OCR-039',
            'Teaching purpose': title,
            'Documentation path': f'docs/{locale}/guides/recognition/formula.mdx',
            'Associated step': f'Formula editing sequence {index}/4: {actions[index-1]}',
            'Source': 'artifacts/research-formula-edit-followup-20261110.md; f02f50e screenshotrecognitionwindow.cpp:1544-1588,1618-1665; screenshotrecognitionsessioncontroller.cpp:1970-2008',
            'Production method': 'Original SVG comparison of formula source and mathematical meaning. Source-backed instructional illustration; no reconstructed application toolbar or native UI pass.',
            'Status': 'Produced; visual and website review pending',
            'Capture prerequisites and next action': 'Actual service recognition and editable LaTeX window require ordinary native UI verification; SVG sequence does not establish a runtime pass.',
        })
with (ROOT / 'artifacts/assets-formula-edit.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f'Produced {len(rows)} bilingual formula editing frames')
