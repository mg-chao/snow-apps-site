"""Illustrate language swapping and secondary-target routing, without fabricating app captures."""
from pathlib import Path
from html import escape
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/public/images/guides'
ROWS = []


def text(x, y, value, size=20, color='#28374e', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def card(y, height=110):
    return f'<rect x="24" y="{y}" width="392" height="{height}" rx="12" fill="white" stroke="#c8d4e4"/>'


def save(locale, name, svg, ids, purpose, step, doc):
    path = OUT / ('en' if locale == 'en' else '') / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)
    ROWS.append({'Asset': path.relative_to(ROOT).as_posix(), 'Feature IDs': ids,
                 'Teaching purpose': purpose, 'Documentation path': f'docs/{locale}/guides/translation/{doc}',
                 'Associated step': step,
                 'Source': 'f02f50e:translationpagecontroller.cpp:74-111;translationpagewidget.cpp:296-303,447-448;screenshottranslationsettingsdialog.cpp:90-113;translationlanguagedetector.cpp:20-57;translationservice.cpp:341-354;translation_page_controller_tests.cpp:116-122 (read only)',
                 'Production method': 'Dedicated original vector state/parameter comparison, generated from verified application behavior. Example translations and detection confidence are illustrative inputs, not service responses or native UI evidence.',
                 'Status': 'Produced; visual and website review pending',
                 'Capture prerequisites and next action': 'Native ordinary-UI language selection, copying and real translation require unlocked app and an available service; no runtime acceptance from this illustration.'})


for locale in ('zh', 'en'):
    en = locale == 'en'
    titles = (['Copy before swapping', 'Only the languages change', 'Replace Source text', 'Compare the new result'] if en
              else ['先复制完整译文', '交换的只是语言选择', '用旧译文替换原文', '比较新一轮译文'])
    actions = (['Copy the complete French result.', 'The English input is still unchanged.', 'Paste the result you copied.', 'Compare with the first English text.'] if en
               else ['复制第一轮完整的法语译文。', '英语原文仍未改变，先不要比较。', '把刚复制的法语译文粘贴到原文区。', '与第一轮英语原文比较意思。'])
    for index in range(1, 5):
        source = 'Open the window.' if index < 3 else 'Ouvrez la fenêtre.'
        result = 'Ouvrez la fenêtre.' if index == 1 else 'Open the window.' if index == 4 else '…'
        pair = ('English → French' if en else '英语 → 法语') if index == 1 else ('French → English' if en else '法语 → 英语')
        body = text(24, 45, titles[index-1], 25, weight=700)
        body += text(24, 96, pair, 24, '#2864ae', 700)
        body += card(125) + text(42, 158, 'Source text' if en else '原文', 18, '#53627d')
        body += text(42, 204, source, 25)
        body += card(265, 130) + text(42, 299, 'Translation' if en else '译文', 18, '#53627d')
        body += text(42, 347, result, 25)
        if index in (2, 3):
            body += text(42, 378, 'New request starts' if en else '新的处理会开始', 17, '#53627d')
        body += text(24, 449, actions[index-1], 20)
        body += text(24, 492, 'Copy → Swap → Paste → Wait' if en else '先复制 → 交换语言 → 粘贴 → 等待', 18, '#53627d')
        body += text(24, 550, 'Instructional illustration' if en else '操作示意', 17, '#53627d')
        body += text(365, 550, f'{index} / 4', 17, '#53627d')
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 580" role="img" aria-labelledby="title desc">'
               f'<title id="title">{escape(titles[index-1])}</title><desc id="desc">{escape(actions[index-1])}</desc>'
               '<rect width="440" height="580" rx="20" fill="#f5f7fc"/>'
               '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">' + body + '</g></svg>')
        save(locale, f'tr-language-swap-{index}.svg', svg, 'TR-012;TR-013', titles[index-1], f'{index}/4', 'text.mdx')

    title = 'Choose when the target can switch' if en else '目标语言何时会自动切换'
    body = text(32, 58, title, 36, weight=700)
    body += text(32, 109, 'Example: local detection finds English at 80%.' if en else '示例：本地检测为英语，置信度80%。', 28, '#53627d')
    cases = ([['Primary: English / Secondary: French', 'Threshold 60%: 80% reaches the threshold.', 'Actual target: French'],
              ['Primary: English / Secondary: French', 'Threshold 90%: 80% is below the threshold.', 'Actual target: English'],
              ['Primary: English / Secondary: English', 'Both targets are the same.', 'Actual target: English']] if en
             else [['主要：英语 / 次要：法语', '阈值60%：80%达到阈值。', '实际目标：法语'],
                   ['主要：英语 / 次要：法语', '阈值90%：80%低于阈值。', '实际目标：英语'],
                   ['主要：英语 / 次要：英语', '两种目标语言相同。', '实际目标：英语']])
    for i, lines in enumerate(cases):
        y = 154 + i*250
        body += f'<rect x="28" y="{y}" width="664" height="220" rx="16" fill="white" stroke="#c8d4e4"/>'
        body += text(50, y+49, f'{i+1}. '+lines[0], 29, '#2864ae', 700)
        body += text(50, y+106, lines[1], 30)
        body += text(50, y+166, lines[2], 32, '#23704a', 700)
    if en:
        body += text(32, 928, 'Specifying the source language alone', 30)
        body += text(32, 969, 'does not disable the target switch.', 30)
    else:
        body += text(32, 956, '指定源语言不会单独关闭这种目标切换。', 30)
    body += text(32, 1017, 'Threshold range: 30%–100%' if en else '阈值可设范围：30%–100%', 30)
    body += text(32, 1072, 'Instructional illustration' if en else '操作示意', 25, '#53627d')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1110" role="img" aria-labelledby="title desc">'
           f'<title id="title">{escape(title)}</title><desc id="desc">{escape(cases[0][1])}</desc>'
           '<rect width="720" height="1110" rx="22" fill="#f5f7fc"/>'
           '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">' + body + '</g></svg>')
    save(locale, 'tr-target-routing.svg', svg, 'TR-004', title, 'Compare threshold60%,90%, and identical targets', 'screenshot.md')

registry = ROOT/'artifacts/assets-translation-swap-20261110b.csv'
registry.parent.mkdir(parents=True, exist_ok=True)
with registry.open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(ROWS[0]))
    writer.writeheader()
    writer.writerows(ROWS)
print(f'Produced {len(ROWS)} bilingual translation states and routing comparisons')
