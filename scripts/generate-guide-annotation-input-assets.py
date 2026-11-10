"""Focused bilingual annotation input-state teaching illustrations.

Writes only this generator's named SVGs, frame metadata and independent registry.
It does not operate Snow Shot or modify tutorial bodies.
"""
from pathlib import Path
from html import escape
import csv
import json
import math
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'docs/public/images/guides'
ART = ROOT / 'artifacts'
INK = '#263b51'
MUTED = '#587087'
BLUE = '#287dbc'
PURPLE = '#7654d6'
RED = '#d44f58'
GRAY = '#a6b4c2'


def L(zh, en):
    return {'zh': zh, 'en': en}


def pick(value, lang):
    return value[lang] if isinstance(value, dict) else str(value)


def wrap(value, width=350, size=19):
    lines, current, units, gap = [], '', 0.0, ''
    tokens = re.findall(r'\s+|[^\s\u3400-\u9fff]+|[\u3400-\u9fff]', value)
    for token in tokens:
        if token.isspace():
            gap = ' ' if current else ''
            continue
        cost = sum(1 if unicodedata.east_asian_width(c) in 'WF' else .56 for c in gap + token)
        if current and units + cost > width / size and token not in '，。；：！？、）】》':
            lines.append(current)
            current, units, gap = '', 0.0, ''
            cost = sum(1 if unicodedata.east_asian_width(c) in 'WF' else .56 for c in token)
        current += gap + token
        units += cost
        gap = ''
    if current:
        lines.append(current)
    return lines


def text(x, y, value, size=19, color=INK, weight=400, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{escape(value)}</text>'


def rect(x, y, w, h, fill='white', stroke='#cfdae6', radius=9, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>'


def circle(x, y, r, fill='white', stroke=BLUE, extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2" {extra}/>'


def line(x1, y1, x2, y2, color=RED, width=3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{d}/>'


def arrow(x1, y1, x2, y2, color=RED, width=3, dash=None):
    a = math.atan2(y2 - y1, x2 - x1)
    q = [(x2, y2)]
    for sign in [-1, 1]:
        q.append((x2 - 11 * math.cos(a) + sign * 5 * math.sin(a), y2 - 11 * math.sin(a) - sign * 5 * math.cos(a)))
    points = ' '.join(f'{x:.2f},{y:.2f}' for x, y in q)
    return line(x1, y1, x2, y2, color, width, dash) + f'<polygon points="{points}" fill="{color}"/>'


def canvas_scene(lang, draft=False, closed=False):
    s = rect(0, 0, 356, 218, '#fafcfe', '#c6d5e4', 6)
    if closed:
        s += text(22, 43, pick(L('回到原应用', 'Return to the original app'), lang), 22, INK, 600)
        for i, w in enumerate([275, 238, 266, 191]):
            s += rect(22, 70 + i * 27, w, 7, '#d1dce7', 'none', 3)
        s += text(22, 198, pick(L('本次截图未输出', 'This capture was not exported'), lang), 18, MUTED)
        return s
    for i, w in enumerate([98, 82, 106]):
        s += rect(46, 54 + i * 10, w, 3, '#d9e2eb', 'none', 1)
    s += rect(36, 36, 130, 67, 'none', PURPLE, 7)
    s += arrow(222, 92, 307, 43, PURPLE, 4)
    s += text(207, 115, pick(L('已完成', 'Completed'), lang), 17, PURPLE)
    if draft:
        s += line(47, 177, 151, 137, RED, 3)
        s += arrow(151, 137, 304, 181, RED, 3, '7 5')
        s += circle(47, 177, 5) + circle(151, 137, 5)
        s += circle(304, 181, 7, 'white', RED, 'stroke-dasharray="3 3"')
        s += text(174, 207, pick(L('未完成预览', 'Unfinished preview'), lang), 17, RED)
    return s


def path_scene(lang, state):
    s = rect(0, 0, 356, 236, '#fafcfe', '#c6d5e4', 6)
    A, B, C = (44, 141), (151, 67), (297, 153)
    s += line(*A, *B, RED, 3)
    if state == 'draft':
        s += arrow(*B, *C, RED, 3, '7 5')
    elif state == 'double':
        s += arrow(*B, *C, RED, 3)
    else:
        s += arrow(*A, *B, RED, 3)
    for name, p in [('A', A), ('B', B)]:
        s += circle(*p, 6) + text(p[0] - 6, p[1] - 16, name, 19, BLUE, 600)
    if state == 'double':
        s += circle(*C, 6) + text(C[0] + 12, C[1] + 6, 'C', 19, BLUE, 600)
        s += text(18, 213, pick(L('A → B → C，末点已加入', 'A → B → C; endpoint included'), lang), 18, INK)
    elif state == 'draft':
        s += circle(*C, 7, 'white', RED, 'stroke-dasharray="3 3"')
        s += text(C[0] + 13, C[1] + 6, 'C', 19, RED, 600)
        s += text(18, 213, pick(L('A、B已固定；C仍跟随指针', 'A/B fixed; C follows the pointer'), lang), 18, INK)
    else:
        s += circle(*C, 7, 'none', GRAY, 'stroke-dasharray="3 3"')
        s += text(C[0] + 13, C[1] + 6, 'C', 19, GRAY)
        s += text(18, 213, pick(L('只留下 A → B', 'Only A → B remains'), lang), 19, INK, 600)
    return s


def text_scene(lang, value='Step 12', caret=None, gone=False, moved=True, ghost=False):
    s = rect(0, 0, 356, 240, '#fafcfe', '#c6d5e4', 6)
    if ghost:
        s += rect(34, 35, 70, 45, 'none', '#bac7d4', 4, 'stroke-dasharray="5 4"')
        if moved:
            s += arrow(122, 57, 222, 57, GRAY, 2)
    x = 244 if moved else 34
    s += rect(x, 35, 70, 45, 'none', PURPLE, 4)
    s += text(203 if moved else 20, 108, pick(L('已完成的方框', 'Completed box'), lang), 17, PURPLE)
    if gone:
        s += text(25, 184, pick(L('整段文字已删除', 'Whole text object removed'), lang), 21, RED, 600)
    else:
        if caret is not None:
            s += rect(28, 142, 282, 56, '#f2f7fe', BLUE, 4)
        # Fixed glyph advances keep the caret between characters on every fallback font.
        glyphs = ''.join(f'<tspan x="{45 + i * 16}">{escape(c)}</tspan>' for i, c in enumerate(value))
        s += f'<text y="180" font-size="22" fill="{RED}" font-weight="500" font-family="Menlo,Consolas,monospace">{glyphs}</text>'
        if caret is not None:
            xx = 45 + caret * 16 - 2
            s += line(xx, 154, xx, 187, BLUE, 1.7)
    return s


def card(title, rows=None, scene=None, scene_height=0, setting=None):
    return {'title': title, 'rows': rows or [], 'scene': scene, 'scene_height': scene_height, 'setting': setting}


def frame(label, alt, caption, cards):
    return {'label': label, 'alt': alt, 'caption': caption, 'cards': cards}


FAMILIES = [
    {
        'name': 'ann-input-cancel',
        'title': L('丢弃草稿，还是退出截图', 'Discard a draft or end capture'),
        'ids': 'ANN-005;ANN-014;ANN-020;ANN-032;ANN-096',
        'pages': L('basics.mdx#撤销重做与取消', 'basics.mdx#undo-redo-and-cancel'),
        'source': 'screenshotoverlayshortcutcontroller.cpp:292-295,324-325,447-449; windowshortcutmanager.cpp:814-829,884-913; screenshotcontroller.cpp:1120-1140,1970-1989; imageeditingwindow.cpp:480-521; input/non_pointer.rs:148-189; lib.rs:329-348',
        'frames': [
            frame(L('先区分成品与草稿', 'Separate finished work from a draft'), L('截图画布上有紫色已完成标注和红色未完成路径，末段用虚线区分', 'A screenshot canvas has completed purple annotations and an unfinished red path with its preview shown dashed'), L('先完成紫色标注，再逐点创建红色路径但尚未结束。图中虚线帮助区分跟随指针的预览部分。下面三帧分别比较从这一状态采取不同操作的结果。', 'Complete the purple annotations, then start a red click-by-click path without finishing it. Dashes distinguish the pointer preview in this illustration. The next three frames compare different actions from this same state.'), [card(L('截图中的标注草稿', 'An annotation draft in a capture'), scene='draft', scene_height=218, rows=[L('紫色：已完成；红色：尚未完成', 'Purple: completed. Red: unfinished.')])]),
            frame(L('切换选择元素，保留成品', 'Select elements keeps finished work'), L('切换选择元素后红色未完成路径消失，紫色矩形和箭头保留，截图画布仍打开', 'Switching to Select elements removes the red draft while retaining the purple rectangle and arrow in the open capture'), L('从第1帧状态，点击选择元素。红色草稿丢弃，紫色成品保留；截图仍在编辑。再切回箭头或线条工具即可重画。', 'From frame 1, click Select elements. The red draft disappears, the purple annotations remain, and capture stays open. Return to Arrow or Line to draw again.'), [card(L('动作：切换选择元素', 'Action: Select elements'), scene='kept', scene_height=218, rows=[L('截图仍在编辑，可继续重画。', 'Capture remains open for editing.')])]),
            frame(L('同一草稿：Esc退出截图', 'Same draft: Esc ends capture'), L('默认Esc使截图标注层结束，回到原应用，本次结果未输出', 'Default Esc ends the screenshot layer and returns to the original app without exporting this capture'), L('重新从第1帧的截图草稿比较：按默认Esc。若显示退出确认，确认退出后截图界面关闭；不会只删去红色草稿再留在画布。', 'Compare again from the capture draft in frame 1: press the default Esc. If asked, confirm exit. Capture closes instead of leaving you on the canvas with only the draft removed.'), [card(L('动作：截图中按Esc', 'Action: Esc in screenshot capture'), scene='closed', scene_height=218, rows=[L('若显示退出确认，确认后关闭。', 'If confirmation appears, confirm to close.')])]),
            frame(L('换到图像编辑器：Esc丢草稿', 'Image editor: Esc drops the draft'), L('图像编辑器中Esc取消红色路径草稿，紫色已完成标注与底图保留', 'In the image editor, Esc removes the red path draft while retaining the purple annotations and base image'), L('在图像编辑器中创建相同路径草稿，并确保没有文字输入、裁剪或取色正在处理按键。按Esc后草稿消失，已完成标注保留，编辑器仍打开。', 'Create the same path draft in the image editor, with no text input, crop or color picker handling keys. Esc removes the draft while completed annotations remain and the editor stays open.'), [card(L('动作：图像编辑器中按Esc', 'Action: Esc in the image editor'), scene='kept', scene_height=218, rows=[L('已完成标注保留；编辑器仍打开。', 'Completed work stays; the editor remains open.')])]),
        ],
    },
    {
        'name': 'ann-input-path-finish',
        'title': L('右键与双击保留哪些点', 'Which points does finishing keep?'),
        'ids': 'ANN-020;ANN-032',
        'pages': L('arrows.mdx#连续点击绘制多点路径;lines.mdx#连续点击形成路径', 'arrows.mdx#create-a-multipoint-path-with-successive-clicks;lines.mdx#create-a-path-with-successive-clicks'),
        'source': 'creation_workflow.rs:336-352,736-771,837-851,891-972; screenshotoverlayinputhandler.cpp:792-825',
        'frames': [
            frame(L('A、B已固定，C仍是预览', 'A/B are fixed; C is a preview'), L('A到B是已固定的路径，B到C是跟随指针的虚线预览，C尚未单击', 'A to B is fixed; a dashed preview runs from B to the pointer at C, which has not been clicked'), L('在直线或曲线箭头、线条工具中，先单击A和B，再把指针移到C但不单击。此时C只是预览端点；虚线用于图中区分预览。', 'With a straight/curved arrow or Line, click A and B, then move to C without clicking. C is only the preview endpoint; dashes distinguish it in this illustration.'), [card(L('同一个未完成路径', 'The same unfinished path'), scene='path-draft', scene_height=236)]),
            frame(L('右键结束，只保留A和B', 'Right-click keeps A and B'), L('右键结束后路径停在B，原指针位置C以灰色参照表示未加入', 'After right-click completion the path ends at B; the former pointer position C is gray to show it was not added'), L('从第1帧状态右键结束。结果只有A和B；C未加入，灰色C仅保留为本图的比较参照。截图时在选区内右键操作。', 'Right-click from frame 1. The result contains only A and B. C was not added; its gray mark is only a comparison reference here. In screenshot capture, right-click inside the selection.'), [card(L('动作：右键结束', 'Action: right-click to finish'), scene='path-right', scene_height=236, rows=[L('当前指针位置不会自动成为末点。', 'The pointer position is not added as an endpoint.')])]),
            frame(L('同一草稿双击C，加入末点', 'Same draft: double-click C'), L('从同一未完成草稿在C双击后，完整路径依次经过A、B、C并结束', 'Double-clicking C from the same unfinished draft produces a completed path through A, B and C'), L('重新从第1帧的草稿比较：在C双击。C会先被固定，然后路径结束，结果依次经过A、B、C。不要接着第2帧已经结束的路径操作。', 'Start again from the draft in frame 1 and double-click C. C is fixed before completion, so the result passes through A, B and C. Begin this comparison from frame 1 rather than the already finished path in frame 2.'), [card(L('动作：在C双击', 'Action: double-click C'), scene='path-double', scene_height=236, rows=[L('C成为已固定的最后一个点。', 'C becomes the final fixed point.')])]),
        ],
    },
    {
        'name': 'ann-input-text-delete',
        'title': L('Delete的结果取决于设置', 'Delete depends on a setting'),
        'ids': 'ANN-046;ANN-047;ANN-106',
        'pages': L('text.mdx#重新修改内容', 'text.mdx#re-edit-the-content'),
        'source': 'snow_canvas_text_editor_input.cpp:83-93; snow_canvas_text_draft.cpp:205-228; snow_canvas_widget_text_interaction.cpp:1029-1072; configurationschema.cpp:1205',
        'frames': [
            frame(L('先看插入光标的位置', 'Locate the caret first'), L('输入状态的文字为Step12，光标位于1和2之间，紫色方框已经完成', 'Text input contains Step12 with the caret between 1 and 2; the purple box is already complete'), L('示例已有文字Step12，正在编辑，插入光标位于1和2之间。下面两帧都从这一状态比较Delete的结果；紫色方框用于检查其他标注是否保留。', 'The existing text Step12 is being edited, with the caret between 1 and 2. Both following frames compare Delete from this state. The purple box helps check that other annotations remain.'), [card(L('输入中：Step1|2', 'Typing: Step1|2'), scene='text-delete-start', scene_height=240, rows=[L('光标后面的字符是2。', 'Next character: 2')])]),
            frame(L('设置开启：只删除后一个字符', 'Setting on: delete the next character'), L('删除光标后的文字设置开启，按Delete后仅2消失，Step1和输入光标保留', 'Delete text after the cursor is on; Delete removes only 2 while Step1 and the active caret remain'), L('保持删除光标后的文字开启，这是默认配置。从第1帧按Delete，只删去光标后的2，文字输入继续。若选中了文字，则删去所选文字。', 'Keep Delete text after the cursor enabled, as in the default configuration. From frame 1, Delete removes the 2 after the caret and input continues. If text is selected, it removes that selection.'), [card(L('删除光标后的文字', 'Delete text after the cursor'), setting=True, scene='text-delete-on', scene_height=240, rows=[L('Step1仍保留，插入光标仍可输入。', 'Step1 remains and the caret stays active.')])]),
            frame(L('设置关闭：删除整个文字对象', 'Setting off: remove the text object'), L('相同输入状态但设置关闭，Delete使整段文字消失，输入结束，紫色方框不变', 'With the same input but the setting off, Delete removes the entire text object and ends input; the purple box stays'), L('重新从第1帧比较：关闭删除光标后的文字，再按Delete。整段文字对象被删掉，输入结束；其他标注保留。只想删字符时可使用Backspace。', 'Start again from frame 1 with Delete text after the cursor disabled, then press Delete. The whole text object is removed and input ends; other annotations remain. Use Backspace when you only want to delete characters.'), [card(L('删除光标后的文字', 'Delete text after the cursor'), setting=False, scene='text-delete-off', scene_height=240, rows=[L('文字对象与插入光标都不再显示。', 'The text object and caret disappear.')])]),
        ],
    },
    {
        'name': 'ann-input-text-undo',
        'title': L('文字撤销与画布撤销', 'Text Undo and canvas Undo'),
        'ids': 'ANN-005;ANN-046',
        'pages': L('text.mdx#修正与输出', 'text.mdx#correct-and-export'),
        'source': 'snow_canvas_widget.cpp:4193-4205,2219-2235; snow_canvas_text_editor_input.cpp:46-53; snow_canvas_text_draft.cpp:249-273; screenshotcontroller.cpp:1970-1989; canvashistoryshortcuts.h:24-35; document_ops.rs:803-965',
        'frames': [
            frame(L('先移动方框，再编辑文字', 'Move the box, then edit text'), L('紫色方框已从灰色参照位置移到右边，文字Step1正在输入中追加2，显示Step12和光标', 'The purple box has moved right from its gray reference position; Step1 is being edited to Step12 with a caret'), L('先创建Step1文字和方框，再只把方框向右移动。进入文字编辑，在Step1后输入2；此时Step12仍在本次输入中，灰框仅标出方框移动前位置。', 'Create Step1 and a box, then move only the box to the right. Edit Step1 and append 2. Step12 is still in the current input session; the gray box only marks its position before the move.'), [card(L('当前：文字正在输入', 'Current state: typing'), scene='history-typing', scene_height=240, rows=[L('最近完成的对象操作：方框右移。', 'Last completed object operation: move the box right.')])]),
            frame(L('输入中Undo只改文字', 'Undo during input changes text'), L('输入中的Undo删去刚追加的2，Step1和光标保留，紫色方框仍在右边', 'Undo in input removes the appended 2, leaving Step1 and the caret; the purple box remains on the right'), L('插入光标仍在时按Windows Ctrl+Z或macOS Command+Z。刚输入的2撤销，文字回到Step1，方框不动。文字历史用尽后继续按，也不会转而撤销方框移动。', 'With the caret active, press Ctrl+Z on Windows or Command+Z on macOS. The appended 2 is undone, returning to Step1 without moving the box. Exhausting text Undo does not switch to undoing the box move.'), [card(L('动作：输入中Ctrl+Z / Command+Z', 'Action: Ctrl+Z / Command+Z while typing'), scene='history-local-undo', scene_height=240, rows=[L('作用范围：当前文字输入。', 'Scope: the current text input.')])]),
            frame(L('重新输入2，再Esc提交', 'Type 2 again, then commit with Esc'), L('重新追加2并Esc结束输入后，Step12保留但光标消失，方框仍在右边', 'After retyping 2 and finishing with Esc, Step12 remains without a caret; the box is still on the right'), L('为比较画布历史，重新输入2，然后按Esc提交文字并结束输入。确认插入光标消失；本次文字修改现在是最近完成的一步。', 'To compare canvas history, type 2 again, then press Esc to commit and finish input. Confirm the caret disappears. This text change is now the most recently completed edit.'), [card(L('动作：输入2，再Esc结束', 'Action: type 2, then Esc'), scene='history-committed', scene_height=240, rows=[L('画布最近一步：Step1 → Step12。', 'Latest canvas edit: Step1 → Step12.')])]),
            frame(L('画布Undo先回退文字提交', 'Canvas Undo first reverts the text edit'), L('第一次工具条撤销把已提交的Step12恢复为Step1，没有光标，方框仍在右边', 'The first toolbar Undo restores committed Step12 to Step1 without a caret; the box stays on the right'), L('点击工具条撤销，先回退最近提交的文字修改：Step12变回Step1。方框仍在右边，因为移动发生得更早。', 'Click Undo in the toolbar. It first reverts the latest committed text change, from Step12 to Step1. The box remains on the right because its move happened earlier.'), [card(L('动作：工具条撤销一次', 'Action: toolbar Undo once'), scene='history-canvas-text', scene_height=240, rows=[L('按已完成操作的先后顺序回退。', 'Completed edits are undone in reverse order.')])]),
            frame(L('再Undo才回退方框移动', 'Undo again to revert the box move'), L('第二次工具条撤销使紫色方框回到左侧原位，Step1保留不变', 'The second toolbar Undo returns the purple box to its original left position while Step1 remains'), L('再点击一次工具条撤销，才回退更早的方框右移。方框回到原位，文字仍是Step1；需要恢复时按相反顺序重做。', 'Click toolbar Undo again to revert the earlier box move. The box returns left while Step1 remains. Redo restores these edits in the opposite order.'), [card(L('动作：工具条再撤销一次', 'Action: toolbar Undo again'), scene='history-canvas-box', scene_height=240, rows=[L('方框回到原位置，文字不再变化。', 'The box returns; the text does not change again.')])]),
        ],
    },
]


def scene_content(name, lang):
    if name in ['draft', 'kept', 'closed']:
        return canvas_scene(lang, draft=name == 'draft', closed=name == 'closed')
    if name.startswith('path-'):
        return path_scene(lang, name[5:])
    if name == 'text-delete-start':
        return text_scene(lang, 'Step12', caret=5)
    if name == 'text-delete-on':
        return text_scene(lang, 'Step1', caret=5)
    if name == 'text-delete-off':
        return text_scene(lang, gone=True)
    if name == 'history-typing':
        return text_scene(lang, 'Step12', caret=6, ghost=True)
    if name == 'history-local-undo':
        return text_scene(lang, 'Step1', caret=5, ghost=True)
    if name == 'history-committed':
        return text_scene(lang, 'Step12', ghost=True)
    if name == 'history-canvas-text':
        return text_scene(lang, 'Step1', ghost=True)
    if name == 'history-canvas-box':
        return text_scene(lang, 'Step1', moved=False, ghost=False)
    raise ValueError(name)


def draw_card(value, lang):
    body, y = '', 31
    for row in wrap(pick(value['title'], lang), 350, 21):
        body += text(18, y, row, 21, PURPLE, 600)
        y += 27
    y += 7
    if value['setting'] is not None:
        on = value['setting']
        body += rect(18, y, 57, 28, PURPLE if on else '#8a9bab', 'none', 14)
        body += circle(61 if on else 32, y + 14, 10, 'white', 'white')
        body += text(90, y + 22, pick(L('开启', 'On') if on else L('关闭', 'Off'), lang), 19, INK)
        y += 42
    if value['scene']:
        body += f'<g transform="translate(18 {y})">{scene_content(value["scene"], lang)}</g>'
        y += value['scene_height'] + 17
    for row in value['rows']:
        for part in wrap(pick(row, lang), 350, 19):
            body += text(18, y + 18, part, 19)
            y += 26
        y += 7
    return rect(0, 0, 392, y + 7, 'white', '#d0dbe7', 11) + body, y + 7


def render(family, index, lang, total_height):
    f = family['frames'][index]
    body, y = '', 34
    for row in wrap(pick(family['title'], lang), 390, 23):
        body += text(24, y, row, 23, INK, 700)
        y += 30
    for row in wrap(pick(f['label'], lang), 390, 20):
        body += text(24, y + 6, row, 20, BLUE, 600)
        y += 27
    y += 24
    for c in f['cards']:
        b, h = draw_card(c, lang)
        body += f'<g transform="translate(24 {y})">{b}</g>'
        y += h + 18
    footer = pick(L('操作示意', 'Instructional illustration'), lang)
    body += f'<path d="M24 {total_height-48} H416" stroke="#d9e2ed"/>'
    body += text(24, total_height - 22, footer, 17, MUTED)
    title = pick(family['title'], lang) + ': ' + pick(f['label'], lang)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="{total_height}" viewBox="0 0 440 {total_height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(pick(f["alt"],lang))}</desc><rect width="440" height="{total_height}" rx="15" fill="#f4f7fc"/><g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">{body}</g></svg>'


def needed_height(family, index, lang):
    f = family['frames'][index]
    y = 34 + 30 * len(wrap(pick(family['title'], lang), 390, 23))
    y += 27 * len(wrap(pick(f['label'], lang), 390, 20)) + 24
    for c in f['cards']:
        _, h = draw_card(c, lang)
        y += h + 18
    return int(math.ceil((y + 63) / 10) * 10)


def main():
    ART.mkdir(parents=True, exist_ok=True)
    rows, meta = [], []
    for family in FAMILIES:
        height = max(needed_height(family, i, lang) for i in range(len(family['frames'])) for lang in ['zh', 'en'])
        entry = {'name': family['name'], 'title': family['title'], 'ids': family['ids'], 'frames': {'zh': [], 'en': []}}
        for lang in ['zh', 'en']:
            folder = PUBLIC if lang == 'zh' else PUBLIC / 'en'
            folder.mkdir(parents=True, exist_ok=True)
            for i, f in enumerate(family['frames']):
                file = family['name'] + f'-{i+1}.svg'
                p = folder / file
                p.write_text(render(family, i, lang, height))
                src = '/images/guides/' + ('' if lang == 'zh' else 'en/') + file
                entry['frames'][lang].append({'src': src, 'alt': pick(f['alt'], lang), 'label': pick(f['label'], lang), 'caption': pick(f['caption'], lang)})
                pages = [f'docs/{lang}/guides/annotations/{part}' for part in pick(family['pages'],lang).split(';')]
                rows.append({'Asset': str(p.relative_to(ROOT)), 'Feature IDs': family['ids'], 'Teaching purpose': pick(f['caption'],lang), 'Documentation path': ';'.join(pages), 'Associated step': pick(f['label'],lang), 'Source': 'f02f50e; ' + family['source'] + '; artifacts/review-annotation-input-routing-20261110c/review.json', 'Production method': 'Original bilingual source-backed SVG; scripts/generate-guide-annotation-input-assets.py; explicit instructional label; narrow440px vertical layout; no app screenshot or video claim', 'Status': '已制作专属教学示意；离线复核与网站验收另记', 'Capture prerequisites and next action': 'No source-drawing prerequisite. Independently render/read all locale frames; integrate and check actual website players. Ordinary UI scope remains separate.'})
        meta.append(entry)
    with (ART / 'assets-annotation-input-followup-20261110c.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (ART / 'annotation-input-frames-20261110c.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'families': len(meta), 'logical_frames': sum(len(x['frames']['zh']) for x in meta), 'localized_svg': len(rows)}, indent=2))


if __name__ == '__main__':
    main()
