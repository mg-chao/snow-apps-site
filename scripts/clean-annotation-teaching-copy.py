# -*- coding: utf-8 -*-
"""Keep public annotation captions about the user's action and visible result."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def links(line):
    return ' '.join(re.findall(r'<a\b[^>]*>.*?</a>', line))


for language in ['zh', 'en']:
    for page in (ROOT / f'docs/{language}/guides/annotations').glob('*.mdx'):
        text = page.read_text()
        if language == 'en':
            text = text.replace('**Alt**', '**Alt (Option on macOS)**', 1) if page.stem in ['shapes', 'elements'] and 'Option on macOS' not in text else text
            text = text.replace('Normal brush', 'Regular brush').replace('Pressure brush', 'Pressure-sensitive brush')
            text = text.replace('**Shapes**', '**Shape**').replace("editing('Shapes')", "editing('Shape')")
            text = text.replace('return to Shapes', 'return to Shape').replace('switch to Shapes', 'switch to Shape')
            text = text.replace('**Tools excluded from quick selection of same-type elements**', '**Tools that forbid quick selection of same-type elements**')
            text = text.replace('**Remember the last used tool**', '**Remember last used tool**')
            text = text.replace('**Always show the first button in a group**', '**Keep group main buttons visible**')
            text = text.replace('Smart erase processes locally without selecting an OCR or AI model or configuring an online service. ', '')
            text = text.replace('The message is reconstructed from the shipped translation. This is not an actual error screenshot or a successful-detection claim.', 'Read the failure message; category filling is not available yet.')
            text = text.replace('Actual Snow Shot detection and category filling for Text and Text in box, using mosaic intensity 85%. The mosaic was not drawn manually.', 'Text and Text in box are filled with mosaic at 85% intensity.')
            text = text.replace('sourceLabel="Teaching illustration \\u00b7 not an app recording"', 'sourceLabel="Instructional illustration"')
            text = text.replace('sourceLabel="Actual rendered frames \\u00b7 not a video recording"', 'sourceLabel="Actual app output"')
            text = text.replace('sourceLabel="Native step screenshots \\u00b7 not a video recording"', 'sourceLabel="In-app steps"')
            text = text.replace('sourceLabel="Teaching illustration · not an app recording"', 'sourceLabel="Instructional illustration"')
            text = text.replace('sourceLabel="Actual rendered frames · not a video recording"', 'sourceLabel="Actual app output"')
            text = text.replace('sourceLabel="Native step screenshots · not a video recording"', 'sourceLabel="In-app steps"')
        else:
            text = text.replace('智能擦除在本地处理，不需要选择 OCR 或 AI 模型。', '')
            text = text.replace('提示内容按发行版中文翻译重建；这不是实际错误截图，也不表示当前图片已识别成功。', '确认失败提示；此时还不能按类别填充。')
            text = text.replace('Snow Shot实际检测并填充文本、框内文本两类，使用85%马赛克强度；这是运行结果，未手工绘制马赛克。', '文本与框内文本两类已填充马赛克，此处强度为85%。')
            text = text.replace('sourceLabel="实机步骤截图 · 非视频录屏"', 'sourceLabel="操作步骤"')
            text = text.replace('sourceLabel="实际渲染分镜 · 非视频录屏"', 'sourceLabel="实际效果"')
        output = []
        for line in text.splitlines():
            if line.startswith('*') and not line.startswith('**'):
                link = links(line)
                if language == 'en':
                    if line in [
                        '*Teaching illustration, not an app recording. The diagrams emphasize the operation; refer to the app for the actual control layout.*',
                        '*A dedicated, source-checked teaching reconstruction, not an app screenshot or recording. Step through the frames or enlarge them.*',
                    ]:
                        continue
                    if '19 regions' in line:
                        line = '*The scan found **19 regions in total**, not 19 text regions. Parts of avatar shapes were also processed. Check for unintended coverage and exposed text after category filling.*'
                    elif 'Both sides start' in line:
                        line = '*Only the right-hand text is removed; the left text and both blue bars remain. A small area on a simple background is a useful first attempt. Inspect complex textures separately. ' + link + '.*'
                    elif 'lower-right white image' in line:
                        line = '*Smart erase is selected and intensity is disabled. The completed image is at lower right. ' + link + '.*'
                    elif 'thin red arrow' in line:
                        line = '*The thin red arrow was created by dragging, then curved by moving its middle control. The thick purple arrow is part of the background image.*'
                    elif 'red arrow is in' in line:
                        line = '*The red arrow is in the white canvas at lower right. On a phone, use “Enlarge current illustration” to inspect its points and path.*'
                    elif 'using icons directly' in line:
                        line = '*Compare the end symbols below; the start end has corresponding directions. ' + link + '.*'
                    elif 'top row compares' in line:
                        line = '*The top row compares line patterns; the bottom row compares outline widths. ' + link + '.*'
                    elif 'shaft-ratio-engine' in line:
                        line = '*Compare Plain and Tapered shafts with endpoint scales 0.5, 1 and 2. ' + link + '.*'
                    elif 'filter-effects-engine' in line:
                        line = '*Compare different filters on the same content and bounds. ' + link + '.*'
                    elif 'filter-strength-engine' in line:
                        line = '*Compare 10%, 50% and 90% mosaic intensity on the same content. ' + link + '.*'
                    elif 'same fictional texture' in line:
                        line = '*The first frame is unfiltered; the next two show how coverage expands along the brush path.*'
                    elif 'failure and re-entry states' in line:
                        line = '*A blank image can finish normally with no regions. Retry after an error; use manual ranges when no suitable regions are found.*'
                    elif 'Menu order and immediate application' in line:
                        line = '*Choose one category to fill it immediately, then reopen the menu for another category. ' + link + '.*'
                    elif 'fictional text material and MCP' in line:
                        line = '*A completed curved arrow over a text example.*'
                    else:
                        line = re.sub(r'^\*Teaching illustration(?:, not an app screenshot or recording|, not an app recording)?\.\s*', '*', line)
                else:
                    if line in ['*教学示意，非应用录屏。图中用局部结构突出本页操作，控件位置以应用实际布局为准。*', '*源码核对的专属教学重建，非应用截图或录屏；可逐步播放或放大查看。*']:
                        continue
                    if '19个检测区域总数' in line:
                        line = '*本例共识别到 **19个区域**，不是19个文本区域。部分头像形状也被处理，说明分类可能误判；填充后仍要检查误遮挡和漏出的文字。*'
                    elif '仅在右侧文字处' in line:
                        line = '*只擦除了右侧文字，左侧文字和两侧蓝条保留。可先从简单背景上的小范围开始，复杂纹理需另行检查。' + link + '。*'
                    elif '样式条显示“智能擦除”' in line:
                        line = '*样式条显示“智能擦除”，强度滑块不可用；右下方白色素材区域为处理结果。' + link + '。*'
                    elif '细红箭头通过鼠标拖动创建' in line:
                        line = '*细红箭头通过拖动创建，再拖中间控制点改变弧度；粗紫箭头是背景图的一部分。*'
                    elif '红色箭头位于右下方' in line:
                        line = '*红色箭头位于右下方白色画布；手机上可点“放大查看当前图示”检查路径与控制点。*'
                    elif '图标直接取自' in line:
                        line = '*下图对照末端符号，起始端有对应方向的选择。' + link + '。*'
                    elif '上排比较线型' in line:
                        line = '*上排比较线型，下排比较轮廓宽度。' + link + '。*'
                    elif 'shaft-ratio-engine' in line:
                        line = '*比较普通、渐宽箭杆与0.5倍、1倍、2倍端点比例。' + link + '。*'
                    elif 'filter-effects-engine' in line:
                        line = '*对照相同内容和范围下的不同滤镜效果。' + link + '。*'
                    elif 'filter-strength-engine' in line:
                        line = '*比较相同内容下10%、50%、90%马赛克强度。' + link + '。*'
                    elif '每步轨迹通过 MCP' in line:
                        line = '*第一帧未加滤镜，后两帧展示画笔轨迹延伸时覆盖范围的变化。*'
                    elif '分类顺序与立即填充' in line:
                        line = '*选择一个类别即可填充，需要处理另一类时再打开菜单。' + link + '。*'
                    elif '分镜重建源码中的失败' in line:
                        line = '*空白图片也可能正常识别结束但没有区域，这与报错不同。报错后可重试；没有合适区域时改用手动范围。*'
                    elif '通过 MCP 创建' in line:
                        line = '*文字示例上已完成的曲线箭头。*'
                    else:
                        line = line.replace('*教学示意，非应用截图或录屏。', '*')
            output.append(line)
        text = '\n'.join(output) + '\n'
        text = re.sub(r'\n{3,}', '\n\n', text)
        page.write_text(text)
print('Simplified public annotation captions in both languages; internal evidence unchanged.')
