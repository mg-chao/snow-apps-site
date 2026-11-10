#!/usr/bin/env python3
"""Generate bilingual pin gesture, menu-flow and window-alignment teaching SVGs."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path


GESTURES = {
    'select': {
        'zh': ('短单击选择，再移动整组', [
            ('短单击切换选择', ['非实时贴图，退出缩略图和鼠标穿透。', '按住 Ctrl；macOS 使用 Command。', '短单击 A、B，出现各自的选择标记。', '再次短单击同一张，可取消它的选择。']),
            ('两张以上：拖动整组', ['解除锁定，再拖选中贴图的可移动区域。', '选中的窗口一起移动。', '拖边缘可一起调整大小。', '松开提交；拖动中 Esc 取消。']),
            ('先区分短点和拖动', ['Ctrl/Command＋短单击：切换选择。', '只选一张时，修饰键拖动可导出内容。', '两张以上选中时，可能改为移动整组。', '用各窗口的选择标记取消选择。'])]),
        'en': ('Select with short clicks, then move', [
            ('Toggle selection with a short click', ['Use non-live pins outside thumbnail mode', 'and click-through. Hold Ctrl (Mac: Command).', 'Briefly click A and B to show their indicators.', 'Click again to deselect a window.']),
            ('Two or more: move the selection', ['Unlock, then drag a selected movable area.', 'Selected windows move together.', 'Drag an edge to resize them together.', 'Release to commit; Esc cancels the drag.']),
            ('Distinguish a click from a drag', ['Ctrl/Command + short click: toggle selection.', 'With one pin, a modifier drag exports content.', 'With multiple pins, it can move the group.', 'Use the indicators to clear the selection.'])]),
    },
    'export': {
        'zh': ('按住修饰键，把一张贴图拖出去', [
            ('准备要导出的当前视图', ['回到普通图像视图，退出鼠标穿透。', '确认当前裁剪范围和编辑结果。', '取消其他贴图的选择，避免移动整组。']),
            ('Ctrl/Command＋左键拖动', ['Windows：按住 Ctrl。', 'macOS：按住 Command。', '从图像内容区按住左键拖出。', '保持左键，等待拖动预览准备好。']),
            ('放到目标，检查接收结果', ['目标需要支持接收图像或文件。', '在目标处松开，再检查收到的内容。', '尚未放下时按 Esc 可取消。', '目标不接收时，改用复制或保存。'])]),
        'en': ('Drag one pin into another app', [
            ('Prepare the current visible view', ['Return to image view; leave click-through.', 'Check the visible crop and current edits.', 'Deselect other pins to avoid a group move.']),
            ('Ctrl/Command + left-drag', ['Windows: hold Ctrl.', 'macOS: hold Command.', 'Left-drag from the image content.', 'Keep holding while its preview is prepared.']),
            ('Drop, then inspect the result', ['Use a destination accepting images or files.', 'Release there and inspect what it received.', 'Press Esc before dropping to cancel.', 'If unsupported, copy or save instead.'])]),
    },
    'opacity': {
        'zh': ('同一个滚轮，两种操作', [
            ('不按修饰键：缩放', ['回到普通图像视图。', '把指针放在贴图上滚动。', '显示比例改变，内容细节变大或变小。']),
            ('按住 Ctrl/Command：不透明度', ['Windows 按 Ctrl；macOS 按 Command。', '保持按住，再滚动鼠标滚轮。', '窗口显示更透明或更不透明。', '可调范围：25%–100%。']),
            ('松开修饰键，再检查', ['松开后，滚轮恢复缩放用途。', '滚轮不透明度步长可在贴图设置调整。', '需要清楚阅读时，恢复到 100%。', '源文件不会因此被覆写。'])]),
        'en': ('One wheel, two operations', [
            ('Without a modifier: scale', ['Return to the ordinary image view.', 'Scroll over the pin.', 'The display scale changes; details grow', 'or shrink within the pin view.']),
            ('Hold Ctrl/Command: opacity', ['Windows: Ctrl. macOS: Command.', 'Keep holding it while scrolling.', 'The whole window becomes more or less opaque.', 'Range: 25%–100%.']),
            ('Release the modifier and inspect', ['The wheel returns to scaling.', 'Set the wheel-opacity step in pin settings.', 'Restore 100% when you need clear reading.', 'The source file is not overwritten.'])]),
    },
    'move': {
        'zh': ('在可选文字上移动贴图', [
            ('普通左键拖动：选择文字', ['先等待文字识别完成。', '文字可选时，在内容上左键拖动。', '选中文字范围，窗口保持原位。']),
            ('Alt/Option＋左键拖动：移动', ['先结束文字编辑，并解除锁定。', 'Windows 按住 Alt；macOS 按住 Option。', '从内容区按住左键拖动。', '贴图跟随指针移动。']),
            ('松开，回到需要的操作', ['松开左键，贴图停在新位置。', '松开 Alt/Option 后可继续选择文字。', '原图和文字内容保持。'])]),
        'en': ('Move a pin over selectable text', [
            ('Ordinary left-drag: select words', ['Wait for recognition to finish.', 'Left-drag over selectable text.', 'Words become selected; the pin stays put.']),
            ('Alt/Option + left-drag: move', ['Finish text editing and unlock first.', 'Windows: hold Alt. macOS: hold Option.', 'Left-drag from the content area.', 'The pin follows the pointer.']),
            ('Release and continue', ['Release the left button at the new position.', 'Release Alt/Option to select words again.', 'The original image and text stay intact.'])]),
    },
}


FLOWS = {
    'topmost': {
        'zh': ('决定当前贴图是否始终置顶', [
            ('找到当前窗口的开关', ['在要设置的贴图上打开右键菜单。', '进入「固定到屏幕管理」。', '找到「始终置顶」。']),
            ('勾选：保持在普通窗口上方', ['勾选「始终置顶」。', '切到另一个普通窗口，检查叠放关系。', '这不会同时开启锁定或鼠标穿透。']),
            ('取消：恢复普通叠放', ['再次打开同一菜单，取消勾选。', '检查贴图与其他普通窗口的前后关系。', '只改变当前贴图的置顶状态。'])]),
        'en': ('Choose whether this pin stays on top', [
            ('Find the current pin switch', ['Open this pin’s context menu.', 'Enter Pin to screen management.', 'Find Always on top.']),
            ('Checked: above ordinary windows', ['Check Always on top.', 'Focus another ordinary window to compare.', 'Lock and click-through remain separate.']),
            ('Unchecked: ordinary stacking', ['Open the same menu and uncheck it.', 'Compare the pin with ordinary windows.', 'This changes the current pin only.'])]),
    },
    'editor': {
        'zh': ('把贴图交给独立图像编辑器', [
            ('从贴图打开图像编辑', ['在贴图上右键打开「处理图像」。', '选择「图像编辑」。', '实时贴图需要有可用的当前帧。']),
            ('先核对新窗口的输入', ['在打开的图像编辑窗口检查图片。', '实时贴图发送一张当前帧。', '原实时贴图继续跟随来源更新。']),
            ('编辑并保存结果', ['按图像编辑教程修改和保存结果。', '保存后重新打开文件检查。', '这与在贴图内部进入标注模式不同。'])]),
        'en': ('Open a pin in the image editor', [
            ('Start from the pin', ['Open Process image in its context menu.', 'Choose Image editing.', 'A live pin needs an available current frame.']),
            ('Inspect the new editor input', ['Check the image in the opened editor.', 'A live pin sends one current frame.', 'The live pin keeps following its source.']),
            ('Edit and save the result', ['Follow Image editing to edit and save.', 'Reopen the saved file to check it.', 'This differs from Annotation mode in a pin.'])]),
    },
    'split': {
        'zh': ('从当前贴图进入图像分割', [
            ('从处理图像进入', ['在贴图上右键打开「处理图像」。', '选择「图像分割」。', '实时贴图需要有可用的当前帧。']),
            ('核对分割窗口的图片', ['检查输入预览是不是需要的内容。', '实时贴图发送一张当前帧。', '原实时贴图继续更新，不会被冻结。']),
            ('设置分割并保存', ['按分割教程设置方向、数量或尺寸。', '检查预览后选择「全部保存」。', '到输出文件夹核对每一张结果。'])]),
        'en': ('Send the current pin to splitting', [
            ('Start from Process image', ['Open Process image in the pin menu.', 'Choose Image splitting.', 'A live pin needs an available current frame.']),
            ('Check the splitting input', ['Inspect the source preview first.', 'A live pin sends one current frame.', 'The live pin keeps updating; it is not frozen.']),
            ('Configure and save the slices', ['Set directions, counts or dimensions.', 'Inspect the preview, then choose Save all.', 'Check the files in the output folder.'])]),
    },
    'selected-group': {
        'zh': ('只把所选贴图移到目标组', [
            ('从同组窗口中选 A、B', ['用 Ctrl/Command 短单击选中 A、B。', 'C 不选择，核对两个选择标记。', '右键选中窗口，打开「分组」。']),
            ('选择已有组，或新建分组', ['已有组：点击需要的目标名称。', '新建分组：填写不超过 16 字符的名称。', '名称不能空白，也不能与现有组重复。', '点击「添加」完成；取消则放弃新建。']),
            ('只移动这次所选的 A、B', ['A、B 被移入目标组。', '未选中的 C 保留在原组。', '这与托盘菜单切换当前组不同。'])]),
        'en': ('Move only selected pins to a group', [
            ('Select A and B from one group', ['Ctrl/Command-click A and B briefly.', 'Leave C unselected; check both indicators.', 'Right-click a selected pin and open Group.']),
            ('Choose a group, or create one', ['Choose the name of an existing group.', 'New group: enter up to 16 characters.', 'Use a nonblank name that is not a duplicate.', 'Add completes creation; Cancel abandons it.']),
            ('Only A and B move', ['A and B move to the chosen group.', 'Unselected C stays in the original group.', 'This differs from switching the active group.'])]),
    },
    'close-others': {
        'zh': ('保留所选贴图，关闭同组其他窗口', [
            ('先明确要留下的窗口', ['同一活动组有 A、B、C 三张贴图。', '用 Ctrl/Command 短点选 A、B。', 'C 保持未选，核对选择标记。']),
            ('打开所选窗口菜单', ['先保存仍需要的其他窗口内容。', '右键 A 或 B，查看选中数量。', '选择「关闭其他窗口」。']),
            ('保留 A、B，关闭 C', ['已选择的 A、B 保留。', '当前组中未选择的 C 被关闭。', '不要与「关闭」或「销毁」所选混淆。'])]),
        'en': ('Keep selected pins; close the others', [
            ('Choose which windows to keep', ['A, B and C belong to the active group.', 'Ctrl/Command-click A and B briefly.', 'Leave C unselected; check the indicators.']),
            ('Open the selected-window menu', ['Save other content you still need first.', 'Right-click A or B and check the count.', 'Choose Close other windows.']),
            ('Keep A and B; close C', ['Selected A and B remain open.', 'Unselected C in the active group closes.', 'Close or Destroy targets the selection instead.'])]),
    },
}

OPERATIONS = [
    ('align-left', '左对齐', 'Align left', 'x', 'start'),
    ('align-center-h', '水平居中', 'Center horizontally', 'x', 'center'),
    ('align-right', '右对齐', 'Align right', 'x', 'end'),
    ('distribute-h', '水平分布', 'Distribute horizontally', 'x', 'distribute'),
    ('align-top', '顶对齐', 'Align top', 'y', 'start'),
    ('align-center-v', '垂直居中', 'Center vertically', 'y', 'center'),
    ('align-bottom', '底对齐', 'Align bottom', 'y', 'end'),
    ('distribute-v', '垂直分布', 'Distribute vertically', 'y', 'distribute'),
]
FIXTURE = [(70., 60., 100., 70.), (260., 180., 80., 100.), (510., 420., 120., 80.)]


def text(x, y, value, size=28, color='#33465e', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def begin(title, height, lang):
    label = '操作示意' if lang == 'zh' else 'Instructional illustration'
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{height}" viewBox="0 0 720 {height}" role="img"><title>{escape(title)}</title>',
            f'<rect width="720" height="{height}" rx="24" fill="#f3f6fb"/>',
            '<g font-family="Arial, PingFang SC, Microsoft YaHei, sans-serif">', text(32, 38, label, 22, '#58708d', 600), text(32, 86, title, 31, '#172e50', 700)]


def gesture_svg(data, lang):
    title, steps = data
    parts = begin(title, 1280, lang)
    for i, (heading, lines) in enumerate(steps):
        y = 140 + i * 360
        accent = ['#2c57a5', '#865414', '#20614a'][i]
        fill = ['#eaf0ff', '#fff2da', '#e6f6ee'][i]
        parts += [f'<rect x="32" y="{y}" width="656" height="316" rx="18" fill="#fff" stroke="#c8d4e4" stroke-width="2"/>',
                  f'<rect x="48" y="{y+16}" width="624" height="64" rx="12" fill="{fill}"/>',
                  text(60, y+58, f'{i+1}. {heading}', 28, accent, 700)]
        parts += [text(58, y+128+j*42, line) for j, line in enumerate(lines)]
        if i < 2:
            parts.append(f'<path d="M360 {y+326}v22m-10-10 10 10 10-10" fill="none" stroke="#7890ad" stroke-width="4" stroke-linecap="round"/>')
    parts += [text(32, 1235, '先分清状态，再开始手势。' if lang == 'zh' else 'Check the current state before starting a gesture.', 24, '#4c6481'), '</g></svg>']
    return '\n'.join(parts)+'\n'


def target_rectangles(axis, mode):
    index = 0 if axis == 'x' else 1
    extent = index + 2
    starts = [r[index] for r in FIXTURE]
    ends = [r[index]+r[extent] for r in FIXTURE]
    low, high = min(starts), max(ends)
    result = [list(r) for r in FIXTURE]
    if mode == 'distribute':
        gap = (high-low-sum(r[extent] for r in FIXTURE))/2
        cursor = low
        for r in result:
            r[index] = cursor
            cursor += r[extent]+gap
        assert gap > 0
        assert abs(result[1][index]-(result[0][index]+result[0][extent])-gap) < 1e-8
        assert abs(result[2][index]-(result[1][index]+result[1][extent])-gap) < 1e-8
    else:
        for r in result:
            r[index] = low if mode == 'start' else high-r[extent] if mode == 'end' else (low+high-r[extent])/2
    assert all(a[2:] == tuple(b[2:]) for a, b in zip(FIXTURE, result))
    return result, (low if mode == 'start' else high if mode == 'end' else (low+high)/2)


def draw_windows(rectangles, top, axis=None, guide=None):
    p = [f'<rect x="32" y="{top}" width="656" height="420" rx="16" fill="#fff" stroke="#c8d4e4" stroke-width="2"/>']
    colors = ['#c9ddff', '#c3eadb', '#f8dfac']
    if guide is not None:
        coordinate = (80 if axis == 'x' else top+10)+guide*.8
        path = f'M{coordinate} {top+12}V{top+408}' if axis == 'x' else f'M52 {coordinate}H668'
        p.append(f'<path d="{path}" stroke="#dc6970" stroke-width="3" stroke-dasharray="8 6"/>')
    for i, (x, y, w, h) in enumerate(rectangles):
        x, y, w, h = 80+x*.8, top+10+y*.8, w*.8, h*.8
        p += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{colors[i]}" stroke="#42617e" stroke-width="2"/>', text(x+w/2-10, y+h/2+10, chr(65+i), 30, '#172e50', 700)]
    return p


def alignment_svg(operation, lang):
    stem, zh, en, axis, mode = operation
    name = zh if lang == 'zh' else en
    targets, guide = target_rectangles(axis, mode)
    parts = begin(name, 1220, lang)
    subtitle = '三张已选中且未锁定的贴图' if lang == 'zh' else 'Three selected, unlocked pins'
    parts += [text(32, 132, subtitle, 25), text(32, 176, '操作前' if lang == 'zh' else 'Before', 26, '#4c6481', 600)]
    parts += draw_windows(FIXTURE, 194)
    parts += [text(32, 674, '对齐位置 → '+name if lang == 'zh' else 'Align position → '+name, 27, '#2c57a5', 700)]
    parts += draw_windows(targets, 696, axis, None if mode == 'distribute' else guide)
    footer = ('至少三张；边缘间距相等，大小保持。' if mode == 'distribute' else '至少两张；位置改变，窗口大小保持。') if lang == 'zh' else ('At least three; equal edge gaps, unchanged sizes.' if mode == 'distribute' else 'At least two; positions change, sizes stay intact.')
    parts += [text(32, 1171, footer, 25, '#4c6481'), '</g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    for lang in ['zh', 'en']:
        directory = args.root/'docs/public/images/guides'
        if lang == 'en':
            directory /= 'en'
        directory.mkdir(parents=True, exist_ok=True)
        for stem, data in GESTURES.items():
            (directory/f'pin-gesture-{stem}.svg').write_text(gesture_svg(data[lang], lang), encoding='utf-8')
        for stem, data in FLOWS.items():
            value = gesture_svg(data[lang], lang)
            value = value.replace('先分清状态，再开始手势。', '先核对目标，再执行菜单操作。').replace('Check the current state before starting a gesture.', 'Check the target before using a menu command.')
            (directory/f'pin-flow-{stem}.svg').write_text(value, encoding='utf-8')
        for operation in OPERATIONS:
            (directory/f'pin-{operation[0]}.svg').write_text(alignment_svg(operation, lang), encoding='utf-8')
    print('Generated34 bilingual pin gesture, menu-flow and alignment SVGs.')


if __name__ == '__main__':
    main()
