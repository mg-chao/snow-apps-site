"""Generate focused bilingual recognition diagrams and their independent registry.

Run from its staged or integrated location. Only this generator's named assets,
registry, and frame metadata are written. Practice-image bytes are embedded for
reproduction; they are input fixtures, never captured Snow Shot results.
"""

from pathlib import Path
from html import escape
import base64
import csv
import json
import math
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'docs/public/images/guides'
ART = ROOT / 'artifacts'
INK, MUTED, BLUE, PURPLE = '#24384f', '#536b83', '#267cba', '#7154d9'
GREEN, RED = '#258568', '#c34d56'
INPUTS = {
  "qr_text": {
    "filename": "rec-practice-qr-text.webp",
    "source_file": "guide-qr-text.png",
    "payload": "Snow Shot guide fixture",
    "png_sha256": "8f17fa9a9df99f7cfe7e448ea314c412bd16754fae42027b8af22540f82d0d56",
    "png_data": "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",
    "webp_data": "UklGRrQAAABXRUJQVlA4TKgAAAAvF8FFAA8w//M///MfeIDbSJIjKfx3OoWeeSJNPxEi+j8B/e/tXImS8/s1x1FpbgCSVJKwCdcWIpFFmFKU0lyAc5Ik5+e7i0rf+VgyC6HMDSBFJZ13IEUoZPB8RUpSQ59/MqU4IIgFEAWVlD77alVUEUFYAFJQENICFGr4YJ7vTgkVeT/nUinZgqYojVJaANzuxSociWUgSGkDpooOmgtwTqgi8/n+5QY="
  },
  "qr_url": {
    "filename": "rec-practice-qr-url.webp",
    "source_file": "guide-qr-url.png",
    "payload": "https://example.com/snow-shot-guide-fixture",
    "png_sha256": "452d2960e620aff40b37322eb927f951a69d381297c3aec291b389c862e2e434",
    "png_data": "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",
    "webp_data": "UklGRhABAABXRUJQVlA4TAQBAAAvV8FVAA8w//M///MfeIDbRpIkif47HULV7O5pdR8Q0f8J6H9Xe3mClP1umsNQoqR5OUhIKLHggkIppVMqa0kd0BwqJUGah7MvkiTJfjbP6gnpK49EZiEioszjSRTKrCVyNmWPzJJKorMhZKbMdk4nQVRS9lHOppSiKUqhcDmJQkKhRnQ3QtHS3Ga3E01IK1G5m0iQpCRFHA6KlKJEJaK7SQplKaTMw1GFFBUpRrdDoUklosjdlFKhSkpkdjhKRUghVOFwSiqpQsms7uZZKpmVStyNvaSghCzdTVNaCorKPBwMJAqypgNKJUpRlAOyqFQhevlcppLQRMrt7KkGVZDK3fzLCg=="
  },
  "ean13": {
    "filename": "rec-practice-ean13.webp",
    "source_file": "guide-ean13.png",
    "payload": "1234567890128",
    "png_sha256": "79e424355c0775cd2f48f18289b5fe603789ac16724d5b718fa9eb03dc485955",
    "png_data": "iVBORw0KGgoAAAANSUhEUgAAAdwAAADwCAYAAACqutUMAAAAAXNSR0IArs4c6QAAADhlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAAqACAAQAAAABAAAB3KADAAQAAAABAAAA8AAAAACiyeS7AAALf0lEQVR4Ae3XwWobWxRE0Sjk/39ZMW/mO2mEyWW/YmVmZKvrrGoo8np//fvlHwECBAgQIPBPBX7/02/35QQIECBAgMB/AgbXi0CAAAECBC4IGNwLyB5BgAABAgQMrneAAAECBAhcEDC4F5A9ggABAgQIGFzvAAECBAgQuCBgcC8gewQBAgQIEDC43gECBAgQIHBBwOBeQPYIAgQIECBgcL0DBAgQIEDggoDBvYDsEQQIECBAwOB6BwgQIECAwAUBg3sB2SMIECBAgIDB9Q4QIECAAIELAgb3ArJHECBAgAABg+sdIECAAAECFwQM7gVkjyBAgAABAgbXO0CAAAECBC4IGNwLyB5BgAABAgQMrneAAAECBAhcEDC4F5A9ggABAgQIGFzvAAECBAgQuCBgcC8gewQBAgQIEDC43gECBAgQIHBBwOBeQPYIAgQIECBgcL0DBAgQIEDggoDBvYDsEQQIECBAwOB6BwgQIECAwAUBg3sB2SMIECBAgIDB9Q4QIECAAIELAgb3ArJHECBAgAABg+sdIECAAAECFwQM7gVkjyBAgAABAgbXO0CAAAECBC4IGNwLyB5BgAABAgQMrneAAAECBAhcEDC4F5A9ggABAgQIGFzvAAECBAgQuCBgcC8gewQBAgQIEPjzfyd4vV7fTni/399+fvr82y9//fDT3z+/7ynP+ftPPz993/n5+X3nfefn58/n951///T50/edn58/Pz3v/P2nn5++7+nz8/s//f1P//7p+3/6+ad5zt8/fz7znJ+fPz+9P+fn59//9HlP33c+/+l55+8/ff/5+fn3nz7v098/n3/+/Znnp7//6d9/muf8/trP/odba0QeAgQIEJgUMLiTtTqKAAECBGoCBrfWiDwECBAgMClgcCdrdRQBAgQI1AQMbq0ReQgQIEBgUsDgTtbqKAIECBCoCRjcWiPyECBAgMCkgMGdrNVRBAgQIFATMLi1RuQhQIAAgUkBgztZq6MIECBAoCZgcGuNyEOAAAECkwIGd7JWRxEgQIBATcDg1hqRhwABAgQmBQzuZK2OIkCAAIGagMGtNSIPAQIECEwKGNzJWh1FgAABAjUBg1trRB4CBAgQmBQwuJO1OooAAQIEagIGt9aIPAQIECAwKWBwJ2t1FAECBAjUBAxurRF5CBAgQGBSwOBO1uooAgQIEKgJGNxaI/IQIECAwKSAwZ2s1VEECBAgUBMwuLVG5CFAgACBSQGDO1mrowgQIECgJmBwa43IQ4AAAQKTAgZ3slZHESBAgEBNwODWGpGHAAECBCYFDO5krY4iQIAAgZqAwa01Ig8BAgQITAoY3MlaHUWAAAECNQGDW2tEHgIECBCYFDC4k7U6igABAgRqAga31og8BAgQIDApYHAna3UUAQIECNQEDG6tEXkIECBAYFLA4E7W6igCBAgQqAkY3Foj8hAgQIDApIDBnazVUQQIECBQEzC4tUbkIUCAAIFJAYM7WaujCBAgQKAmYHBrjchDgAABApMCBneyVkcRIECAQE3A4NYakYcAAQIEJgUM7mStjiJAgACBmoDBrTUiDwECBAhMChjcyVodRYAAAQI1AYNba0QeAgQIEJgUMLiTtTqKAAECBGoCBrfWiDwECBAgMClgcCdrdRQBAgQI1AQMbq0ReQgQIEBgUsDgTtbqKAIECBCoCRjcWiPyECBAgMCkgMGdrNVRBAgQIFATMLi1RuQhQIAAgUkBgztZq6MIECBAoCZgcGuNyEOAAAECkwIGd7JWRxEgQIBATcDg1hqRhwABAgQmBQzuZK2OIkCAAIGagMGtNSIPAQIECEwKGNzJWh1FgAABAjUBg1trRB4CBAgQmBQwuJO1OooAAQIEagIGt9aIPAQIECAwKWBwJ2t1FAECBAjUBAxurRF5CBAgQGBSwOBO1uooAgQIEKgJGNxaI/IQIECAwKSAwZ2s1VEECBAgUBMwuLVG5CFAgACBSQGDO1mrowgQIECgJmBwa43IQ4AAAQKTAgZ3slZHESBAgEBNwODWGpGHAAECBCYFDO5krY4iQIAAgZqAwa01Ig8BAgQITAoY3MlaHUWAAAECNQGDW2tEHgIECBCYFDC4k7U6igABAgRqAga31og8BAgQIDApYHAna3UUAQIECNQEDG6tEXkIECBAYFLA4E7W6igCBAgQqAkY3Foj8hAgQIDApIDBnazVUQQIECBQEzC4tUbkIUCAAIFJAYM7WaujCBAgQKAmYHBrjchDgAABApMCBneyVkcRIECAQE3A4NYakYcAAQIEJgUM7mStjiJAgACBmoDBrTUiDwECBAhMChjcyVodRYAAAQI1AYNba0QeAgQIEJgUMLiTtTqKAAECBGoCBrfWiDwECBAgMClgcCdrdRQBAgQI1AQMbq0ReQgQIEBgUsDgTtbqKAIECBCoCRjcWiPyECBAgMCkgMGdrNVRBAgQIFATMLi1RuQhQIAAgUkBgztZq6MIECBAoCZgcGuNyEOAAAECkwIGd7JWRxEgQIBATcDg1hqRhwABAgQmBQzuZK2OIkCAAIGagMGtNSIPAQIECEwKGNzJWh1FgAABAjUBg1trRB4CBAgQmBQwuJO1OooAAQIEagIGt9aIPAQIECAwKWBwJ2t1FAECBAjUBAxurRF5CBAgQGBSwOBO1uooAgQIEKgJGNxaI/IQIECAwKSAwZ2s1VEECBAgUBMwuLVG5CFAgACBSQGDO1mrowgQIECgJmBwa43IQ4AAAQKTAgZ3slZHESBAgEBNwODWGpGHAAECBCYFDO5krY4iQIAAgZqAwa01Ig8BAgQITAoY3MlaHUWAAAECNQGDW2tEHgIECBCYFDC4k7U6igABAgRqAga31og8BAgQIDApYHAna3UUAQIECNQEDG6tEXkIECBAYFLA4E7W6igCBAgQqAkY3Foj8hAgQIDApIDBnazVUQQIECBQEzC4tUbkIUCAAIFJAYM7WaujCBAgQKAmYHBrjchDgAABApMCBneyVkcRIECAQE3A4NYakYcAAQIEJgUM7mStjiJAgACBmoDBrTUiDwECBAhMChjcyVodRYAAAQI1AYNba0QeAgQIEJgUMLiTtTqKAAECBGoCBrfWiDwECBAgMClgcCdrdRQBAgQI1AQMbq0ReQgQIEBgUsDgTtbqKAIECBCoCRjcWiPyECBAgMCkgMGdrNVRBAgQIFATMLi1RuQhQIAAgUkBgztZq6MIECBAoCZgcGuNyEOAAAECkwIGd7JWRxEgQIBATcDg1hqRhwABAgQmBQzuZK2OIkCAAIGagMGtNSIPAQIECEwKvN5f/yYvcxQBAgQIEAgJ+B9uqAxRCBAgQGBXwODudusyAgQIEAgJGNxQGaIQIECAwK6Awd3t1mUECBAgEBIwuKEyRCFAgACBXQGDu9utywgQIEAgJGBwQ2WIQoAAAQK7AgZ3t1uXESBAgEBIwOCGyhCFAAECBHYFDO5uty4jQIAAgZCAwQ2VIQoBAgQI7AoY3N1uXUaAAAECIQGDGypDFAIECBDYFTC4u926jAABAgRCAgY3VIYoBAgQILArYHB3u3UZAQIECIQEDG6oDFEIECBAYFfA4O526zICBAgQCAkY3FAZohAgQIDAroDB3e3WZQQIECAQEjC4oTJEIUCAAIFdAYO7263LCBAgQCAkYHBDZYhCgAABArsCBne3W5cRIECAQEjA4IbKEIUAAQIEdgUM7m63LiNAgACBkIDBDZUhCgECBAjsChjc3W5dRoAAAQIhAYMbKkMUAgQIENgVMLi73bqMAAECBEICBjdUhigECBAgsCtgcHe7dRkBAgQIhAQMbqgMUQgQIEBgV8Dg7nbrMgIECBAICRjcUBmiECBAgMCugMHd7dZlBAgQIBASMLihMkQhQIAAgV0Bg7vbrcsIECBAICRgcENliEKAAAECuwJ/AUPdY9ltByw1AAAAAElFTkSuQmCC",
    "webp_data": "UklGRkgAAABXRUJQVlA4TDwAAAAv28E7AA8w//M///MfeGAMSZKgNih/yzIogP3u3kX0fwI6mS8lSmPKwAwyVWI0QRyS6e+/3383qkM/kgA="
  }
}
SAVE_PATH = 'M198.4 64h456.96q33.6 0 57.12 23.52l170.24 170.24q23.52 23.52 23.52 57.12v564.48q0 80.64-80.64 80.64H198.4q-80.64 0-80.64-80.64V144.64q0-80.64 80.64-80.64Zm0 80.64v734.72h98.56V592.64q0-80.64 80.64-80.64h268.8q80.64 0 80.64 80.64v286.72h98.56V314.88L655.36 144.64v161.28q0 80.64-80.64 80.64H413.44q-80.64 0-80.64-80.64V144.64H198.4Zm215.04 0v161.28h161.28V144.64H413.44Zm-35.84 448v286.72h268.8V592.64H377.6Z'


def L(zh, en):
    return {'zh': zh, 'en': en}


def choose(value, lang):
    return value[lang] if isinstance(value, dict) and 'zh' in value else str(value)


def text(x, y, value, size=20, color=INK, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def rect(x, y, width, height, fill='white', stroke='#c8d3e6', radius=9, extra=''):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.4" {extra}/>'


def wrap(value, width=356, size=20):
    # Preserve real word spaces while allowing individual CJK characters to wrap.
    result, current, units, gap = [], '', 0.0, ''
    for token in re.findall(r'\s+|[^\s\u3400-\u9fff]+|[\u3400-\u9fff]', value):
        if token.isspace():
            gap = ' ' if current else ''
            continue
        cost = sum(1 if unicodedata.east_asian_width(c) in 'WF' else .56 for c in gap+token)
        if current and units+cost > width/size and token not in '，。；：！？、）】》':
            result.append(current)
            current, units, gap = '', 0.0, ''
            cost = sum(1 if unicodedata.east_asian_width(c) in 'WF' else .56 for c in token)
        current += gap+token
        units += cost
        gap = ''
    if current:
        result.append(current)
    return result


def field(label, value, disabled=False, options=None):
    return {'label': label, 'value': value, 'disabled': disabled, 'options': options}


def card(title, rows=None, fields=None, code=None, table=None, menu=None, image=None, save=False, selected=False, tone=None, buttons=None, top_buttons=None):
    return {'title': title, 'rows': rows or [], 'fields': fields or [], 'code': code, 'table': table, 'menu': menu, 'image': image, 'save': save, 'selected': selected, 'tone': tone, 'buttons': buttons or [], 'top_buttons': top_buttons or []}


def frame(label, caption, cards):
    return {'label': label, 'caption': caption, 'cards': cards}


def family(name, title, page, sections, ids, source, frames):
    return {'name': name, 'title': title, 'page': page, 'sections': sections, 'ids': ids, 'source': source, 'frames': frames}


BASE_TABLE = [L('项目', 'Item'), L('数量', 'Qty'), L('金额', 'Sum'), L('笔', 'Pen'), '2', '80', L('纸', 'Paper'), '3', '60']


def grid(values=None, selected=None, editor=None, merged=False):
    return {'values': values or BASE_TABLE, 'selected': selected, 'editor': editor, 'merged': merged}


FAMILIES = [
    family('rec-model-controls', L('本地文字识别设置', 'Local OCR controls'), 'models.mdx', L('选择模型', 'choose-a-model'), 'OCR-012;OCR-013;OCR-014;OCR-015;OCR-016;OCR-017;OCR-018', 'settingscatalog.cpp:2996-3118; settingsbackend.cpp:870-878,1273-1274; configurationschema.cpp:913-929; screenshotocrassets.cpp:917-1029', [
        frame(L('选模型，再新建识别任务', 'Choose a model, then a fresh task'), L('在模型类型中选择需要的大小，设置会保存。结束当前截图，重新框选同一样例；资源完整时直接识别，缺少所选模型资源时才准备组件。', 'Choose the required model size; the setting is saved. End the screenshot and capture the same sample again. Ready resources recognize directly; missing selected-model resources trigger preparation.'), [
            card(L('OCR 模型与性能', 'OCR models & performance'), fields=[field(L('模型类型', 'Model type'), L('小型 V6', 'Small V6'), options=[L('超小型 V6', 'Ultra small V6'), L('小型 V6', 'Small V6'), L('中型 V6', 'Medium V6')])]),
            card(L('新截图 → 文本识别', 'New capture → Text recognition'), rows=[L('资源已齐 → 可断网本地识别', 'Resources ready → local recognition can run offline'), L('资源缺少 → 准备组件 → 识别', 'Missing resources → prepare → recognize')]),
            card(L('下载时的示例进度', 'Example progress during download'), code=[L('正在准备文本识别组件（50%）', 'Preparing text recognition components (50%)')], rows=[L('保持联网等待；资源已齐不会出现此下载提示。', 'Stay online and wait. Ready resources do not show this download message.')]),
        ]),
        frame(L('分别比较检测策略', 'Compare detection options'), L('先选检测缩放，再选处理策略，每次只改一项并重新识别同一范围。放大短边可能找到更小文字；速度优先可能改变识别结果。', 'Change one detection option at a time and recognize the same area again. Enlarge short side may find smaller text; Speed first may change the result.'), [
            card(L('文本检测缩放', 'Text detection scaling'), rows=[L('限制长边（更快）', 'Limit long side (faster)'), L('放大短边（更多细节）', 'Enlarge short side (more detail)')]),
            card(L('文本检测处理', 'Text detection processing'), rows=[L('准确优先', 'Accuracy first'), L('速度优先', 'Speed first'), L('选回原规则可恢复比较基准。', 'Choose the preceding rule to restore your comparison baseline.')]),
        ]),
        frame(L('先看热启动为何变灰', 'Why hot start is unavailable'), L('常驻识别进程关闭时，模型热启动开关不可用。Mini 的新配置默认关闭常驻；这不代表不能执行普通文字识别。', 'Model hot start is unavailable while the resident process is off. New Mini configurations disable residency; ordinary text recognition still works.'), [
            card(L('当前开关', 'Current switches'), fields=[field(L('常驻识别进程', 'Resident recognition process'), L('关闭', 'Off')), field(L('模型热启动', 'Model hot start'), L('关闭', 'Off'), True)]),
            card(L('观察结果', 'What to observe'), rows=[L('灰色的是热启动开关，不是文字识别入口。', 'The hot-start switch is unavailable, not the Text recognition action.')]),
        ]),
        frame(L('开启常驻后再开热启动', 'Enable residency before hot start'), L('先开启常驻识别进程，模型热启动才可操作。开启热启动会预加载所选模型并增加内存占用；不需要时关闭热启动或常驻。', 'Enable Resident recognition process to make Model hot start available. Hot start preloads the selected model and uses more memory. Disable hot start or residency when unnecessary.'), [
            card(L('按顺序设置', 'Set in order'), fields=[field(L('常驻识别进程', 'Resident recognition process'), L('开启', 'On')), field(L('模型热启动', 'Model hot start'), L('开启', 'On'))]),
            card(L('再比较新识别任务', 'Compare fresh recognition tasks'), rows=[L('比较首次与后续等待，同时观察内存。', 'Compare first and later requests, and watch memory use.')]),
        ]),
        frame(L('硬件开关不等于正在用 GPU', 'A switch is not GPU-use proof'), L('硬件加速开启后，可用时使用 GPU，不可用时仍使用 CPU。若出现异常，关闭这一项，再用新识别任务检查 CPU 路径。', 'When acceleration is enabled, an available GPU can be used; otherwise recognition uses the CPU. If it misbehaves, disable the option and try a fresh CPU recognition task.'), [
            card(L('OCR 模型与性能', 'OCR models & performance'), fields=[field(L('硬件加速', 'Hardware acceleration'), L('开启', 'On'))]),
            card(L('实际处理路径', 'Actual processing path'), rows=[L('加速可用 → GPU', 'Acceleration available → GPU'), L('加速不可用 → CPU', 'Acceleration unavailable → CPU'), L('开关开启本身不能判断实际路径。', 'The enabled switch alone does not identify the active path.')]),
        ]),
    ]),
    family('rec-original-view', L('原图与结果的两种对照方式', 'Original and result views'), 'text.mdx', L('校对与编辑', 'compare-and-edit'), 'OCR-003', 'screenshotrecognitionwindow.cpp:1018-1029,1476-1483; screenshotrecognitionsessioncontroller.cpp:4170-4186', [
        frame(L('先查看识别结果', 'Start with recognized text'), L('这是截图识别的结果状态。显示原图按钮尚未开启；先记住要校对的字符，再切换查看输入图像。', 'This is a screenshot-recognition result. Show original image is off. Note the character to check before switching to the input image.'), [card(L('显示原图：关闭', 'Show original image: off'), code=['Error code: O12']), card(L('下一步', 'Next'), rows=[L('在属性栏单击“显示原图”。', 'Click Show original image in the property bar.')])]),
        frame(L('切回输入，再切回结果', 'Inspect input, then return'), L('开启显示原图后，文字结果暂时隐藏，输入图像里的012可用于校对。再单击同一按钮，回到上一帧的文字结果继续编辑。', 'Show original image hides the text result temporarily. Check 012 in the input, then click the same button again to return to the text result for editing.'), [card(L('显示原图：开启', 'Show original image: on'), code=['Error code: 012']), card(L('文字结果暂时隐藏', 'Text result temporarily hidden'), rows=[L('再单击同一按钮 → 返回结果', 'Click the same button again → return to the result')])]),
        frame(L('旁侧参照另有设置', 'A side reference has its own setting'), L('在识别结果设置中开启显示原图预览；返回文字结果后，可把单独的原图参照与文字一起对照。这不是把显示原图按钮设为默认开启。', 'Enable Show original image preview under Recognition output. Return to the text result and compare it with the separate input reference. This does not turn on the Show original image button by default.'), [card(L('识别结果', 'Recognition output'), fields=[field(L('显示原图预览', 'Show original image preview'), L('开启', 'On'))]), card(L('文字结果', 'Text result'), code=['Error code: O12']), card(L('单独的原图参照', 'Separate input reference'), code=['Error code: 012'])]),
    ]),
    family('rec-text-transforms', L('整理整段文字，再恢复', 'Transform and restore text'), 'text.mdx', L('调整格式与标点', 'line-breaks-and-punctuation'), 'OCR-006;OCR-007;OCR-008', 'screenshotocrtexttransform.cpp:42-88; screenshotocrtexteditingsession.cpp:96-177,304-325; screenshotrecognitionsessioncontroller.cpp:2239-2269,2706-2765', [
        frame(L('移除换行作用于整段', 'Remove breaks across the passage'), L('原始示例是两行Snow，和Shot！。即使只选了局部文字，属性栏移除换行仍整理整段，结果不会自动补入空格。', 'The original sample is two lines: Snow， and Shot！. The property-bar rule affects the passage even with a partial selection. Removing the line break does not insert a space.'), [card(L('原始识别文字', 'Initial recognized text'), code=['Snow，', 'Shot！']), card(L('选择格式：移除换行', 'Formatting: Remove line breaks'), code=['Snow，Shot！'])]),
        frame(L('再把标点改为半角', 'Convert supported punctuation'), L('选择半角后，支持转换的全角逗号和感叹号变为英文半角；文字仍是同一段，复制前检查它是否适合目标用途。', 'Choose Half-width to convert the supported full-width comma and exclamation mark. Check the resulting passage before copying it.'), [card(L('当前规则', 'Current rules'), fields=[field(L('格式', 'Formatting'), L('移除换行', 'Remove line breaks')), field(L('标点符号', 'Punctuation'), L('半角', 'Half-width'))]), card(L('当前文字', 'Current text'), code=['Snow,Shot!'])]),
        frame(L('重置回最初识别文字', 'Reset to the initial text'), L('单击重置后恢复最初的两行及全角标点，并清除格式与标点选择。这没有重新向识别服务提交图片。', 'Reset restores the initial two lines and full-width punctuation and clears both transform choices. It does not submit the image again.'), [card(L('单击：重置', 'Click: Reset'), code=['Snow，', 'Shot！']), card(L('转换选择已清除', 'Transform choices cleared'), fields=[field(L('格式', 'Formatting'), L('无', 'None')), field(L('标点符号', 'Punctuation'), L('无', 'None'))])]),
        frame(L('误重置后撤销', 'Undo an accidental Reset'), L('撤销可恢复重置前的文字Snow,Shot!。恢复的是文字内容，不会重新选中先前的格式和标点规则。', 'Undo restores the preceding text Snow,Shot!. It restores content without reselecting the earlier Formatting and Punctuation rules.'), [card(L('单击：撤销', 'Click: Undo'), code=['Snow,Shot!']), card(L('转换选择仍为空', 'Transform choices remain clear'), fields=[field(L('格式', 'Formatting'), L('无', 'None')), field(L('标点符号', 'Punctuation'), L('无', 'None'))])]),
    ]),
    family('rec-barcode-results', L('读取条码并取得所需内容', 'Use decoded barcode content'), 'barcode.mdx', L('识别并取得内容', 'recognize-and-retrieve-content'), 'OCR-032;OCR-033;OCR-034;OCR-035;OCR-036', 'screenshottoolpalette.cpp:2129-2220; screenshotqrrecognitionservice.cpp:114-205; screenshotrecognitionwindow.cpp:2170-2222; screenshotrecognitionsessioncontroller.cpp:1532-1544,2860-2863,3717-3764', [
        frame(L('完整框选，再选条码工具', 'Capture the whole practice code'), L('使用页面提供的练习原图，保留完整白边。展开表格/条码工具组选条码识别；组图标可能是上次使用的表格工具。', 'Use the original practice image from this page and keep its complete white border. Expand the table/barcode group and choose Barcode recognition; the group may show the last-used table tool.'), [card(L('练习二维码', 'Practice QR code'), image='qr_text'), card(L('展开工具组', 'Expand the tool group'), menu=[L('表格识别', 'Table recognition'), L('条码识别', 'Barcode recognition')])]),
        frame(L('全选与局部复制分开', 'Choose the copy range'), L('结果最初全选全部内容。下面用两个二维码的内容演示范围：只选第二项再右键复制，就只取得该项；要全部内容，再全选后复制。', 'Results start fully selected. These two QR payloads illustrate scope: select only the second and right-click Copy for that item. Select all again to copy everything.'), [card(L('内容示例', 'Example payloads'), code=['Snow Shot guide fixture', 'https://example.com/snow-shot-guide-fixture'], selected=True), card(L('局部选择第二项 → 右键复制', 'Select the second → right-click Copy'), code=['https://example.com/snow-shot-guide-fixture'])]),
        frame(L('TXT保存全部，链接看整项', 'TXT includes all; links need a URL'), L('保存为文件取得全部内容，多个结果以换行分隔，不随局部选择缩小。有效HTTP(S)整项网址才可点击；普通编号按文字复制。', 'Save as file includes all payloads separated by line breaks, regardless of a partial selection. Only a complete valid HTTP(S) URL is clickable; copy identifiers as text.'), [card('codes.txt', code=['Snow Shot guide fixture', 'https://example.com/snow-shot-guide-fixture']), card(L('链接与编号', 'Links and identifiers'), rows=[L('https://example.com → 可打开链接', 'https://example.com → can open as a link'), L('1234567890128 → 复制文字', '1234567890128 → copy as text'), L('保存成功结束截图；取消则保留结果。', 'Saving ends capture; canceling keeps the result.')])]),
        frame(L('空结果要新建截图', 'Start a fresh capture after no result'), L('没有识别结果时先取消截图，放大原应用或只框一个码，再重新进入条码识别。这里没有通用的结果重试按钮，切走再切回可能仍显示本轮空结果。', 'For no result, cancel the screenshot, enlarge the source or capture only one code, then enter Barcode recognition again. There is no generic result Retry button; switching away and back may retain the empty result.'), [card(L('未识别到条码', 'No barcode was recognized'), tone='error', rows=[L('取消截图 → 调整原图 → 新截图', 'Cancel screenshot → adjust input → new capture')]), card(L('若组件缺失或损坏', 'If components are missing or damaged'), rows=[L('修复或重新安装完整版，再从新截图尝试。', 'Repair or reinstall Full, then try a new capture.'), L('文字OCR模型与翻译API不是条码组件。', 'Text OCR models and translation APIs do not supply barcode components.')])]),
    ]),
    family('rec-table-input', L('区分格内文字与表格范围', 'Cell text or table range'), 'table.mdx', L('复制粘贴与导出', 'copy-paste-and-export'), 'OCR-021;OCR-022;OCR-026;OCR-027;OCR-028', 'screenshottableeditor.cpp:276-368,638-694,698-779,820-899,986-1015,1232-1281; screenshottabledocument.cpp:334-360', [
        frame(L('有输入光标时改的是文字', 'An input cursor means cell text'), L('单击单元格进入文字输入。此时右键剪切、粘贴和删除都作用于格内文字，不是表格行列范围。', 'Clicking a cell enters text editing. Cut, Paste and Delete in this menu affect cell text, not a rectangular table range.'), [card(L('单元格文字编辑', 'Editing cell text'), table=grid(editor=[1,1])), card(L('格内右键菜单', 'Cell-text context menu'), menu=[L('复制', 'Copy'), L('剪切', 'Cut'), L('粘贴', 'Paste'), L('删除', 'Delete'), L('全选', 'Select all')])]),
        frame(L('提交后再退出下一格输入', 'Commit, then leave the next editor'), L('把数量2改为4，Enter提交并进入下一行。接着Esc取消下一格尚未提交的输入，刚提交的4仍保留；再直接右键目标格进入范围菜单。', 'Change quantity 2 to 4. Enter commits and opens the next row; Esc leaves that next uncommitted editor while keeping 4. Right-click the target cell directly for range commands.'), [card(L('当前表格：4已提交', 'Current table: 4 is committed'), table=grid(values=BASE_TABLE[:4]+['4']+BASE_TABLE[5:],selected=[2,1])), card(L('表格区域菜单', 'Table-range context menu'), menu=[L('复制', 'Copy'), L('粘贴', 'Paste'), L('清空内容', 'Clear contents'), L('合并单元格', 'Merge cells'), L('拆分单元格', 'Split cells')])]),
        frame(L('从起点向右下放入数据', 'Paste right and down from the origin'), L('来源为2×2单元格。在目标数量格直接右键粘贴，来源覆盖右下2×2区域；项目列保留。普通文本用Tab分列、换行分行。', 'The source is 2×2 cells. Right-click the destination quantity cell and Paste; it replaces a 2×2 rectangle to its right and below, leaving Item unchanged. Plain text uses tabs for columns and line breaks for rows.'), [card(L('来源2×2', 'Source 2×2'), code=['7    90', '8    100']), card(L('结果：从数量格开始', 'Result: start in Qty'), table=grid(values=BASE_TABLE[:4]+['7','90',L('纸','Paper'),'8','100'],selected=[1,1])), card(L('不增加行列', 'Rows and columns are not added'), rows=[L('放不下时缩小来源或换起点；误贴可撤销。', 'If it does not fit, reduce the source or change the origin. Undo a mistaken paste.')])]),
        frame(L('合并格不能只覆盖一部分', 'Do not partially cover a merged cell'), L('另一个例子：数量与金额已合并，而来源只有1格。只选中整个合并格仍不足以放入；来源尺寸须覆盖完整目标区域，或先拆分目标格再粘贴。', 'Another example: Qty and Sum are merged but the source is one cell. Selecting the whole merged cell does not enlarge the source. Cover its complete dimensions or split the target before pasting.'), [card(L('目标仍为合并区域', 'Target remains merged'), table=grid(merged=True,selected=[1,1])), card(L('来源1×1：7', 'Source 1×1: 7'), tone='error', rows=[L('拒绝部分覆盖，表格内容未改。', 'Partial coverage is rejected; the table is unchanged.'), L('拆分目标 → 再从左上起点粘贴', 'Split target → paste again from its upper-left cell')])]),
        frame(L('回到初始表格后全选复制', 'Select and copy the full table'), L('继续练习时，先用重置回到初始表格。退出格内编辑，按Ctrl+A（macOS为Command+A）全选单元格，再在选区内右键复制。粘贴到电子表格后检查3行3列。', 'For this exercise, Reset to the initial table. Leave cell editing, press Ctrl+A (Command+A on macOS) to select all cells, then right-click Copy inside the selection. Paste into a spreadsheet and check its three rows and columns.'), [card(L('全选单元格，不是格内文字', 'Select cells, not text inside a cell'), table=grid(selected=[0,0,2,2])), card(L('粘贴后检查', 'Check after pasting'), table=grid(), rows=[L('表头、两条数据与3列都应保留。', 'Check the header, both data rows, and all three columns.')])]),
        frame(L('清空内容保留单元格结构', 'Clear text, retain cell structure'), L('在表格区域状态拖选右下2×2数字格，右键清空内容，或按Delete/Backspace。结果保留3行3列和项目文字，只清掉所选格内内容。', 'In table-range mode, select the lower-right 2×2 numeric cells and use Clear contents or Delete/Backspace. The three rows, three columns, and Item text remain; only selected cell contents disappear.'), [card(L('选择数字格', 'Select numeric cells'), table=grid(selected=[1,1,2,2])), card(L('清空内容后', 'After Clear contents'), table=grid(values=BASE_TABLE[:4]+['','',L('纸','Paper'),'',''],selected=[1,1,2,2]))]),
        frame(L('重置也可以撤销', 'Reset can also be undone'), L('在清空后的表格上单击重置，恢复最初内容；再撤销这一次重置，就回到刚才清空数字的状态。再重做这次重置，初始内容又会恢复；这些操作不会重新识别图片。', 'Reset the cleared table to restore its initial contents. Undo that Reset to return to the cleared-number state. Redo that Reset to restore the initial contents again. These operations do not recognize the image again.'), [card(L('重置：原始内容恢复', 'Reset: initial contents return'), table=grid()), card(L('撤销重置：回到清空后', 'Undo Reset: return to cleared cells'), table=grid(values=BASE_TABLE[:4]+['','',L('纸','Paper'),'',''])), card(L('重做重置：初始内容恢复', 'Redo Reset: initial contents return'), table=grid())]),
    ]),
    family('rec-table-workflow', L('表格的等待、重试与文件', 'Table states and files'), 'table.mdx', L('恢复与重试', 'restore-and-retry'), 'OCR-019;OCR-020;OCR-029;OCR-030;OCR-031', 'screenshotrecognitionsessioncontroller.cpp:1219-1237,1239-1335,2840-2879,3188-3264,3516-3565; screenshotcontroller.cpp:4978-5037; screenshotrecognitionfileexport.cpp:408-431', [
        frame(L('生成预览还不能编辑', 'Generating previews are read-only'), L('在识别模型选择表格专用模型或列表中可用视觉模型。视觉模型可能逐步显示只读预览；完成后再进入单元格编辑，不能把中途缺少行列当作最终结果。', 'Choose the dedicated table model or an available listed vision model. Vision generation may show a read-only preview; wait for completion before editing or treating missing rows as final.'), [card(L('识别模型', 'Recognition model'), fields=[field(L('默认选择', 'Default choice'), L('表格专用模型', 'Table-specific model'))], rows=[L('也可选择列表中的可用视觉模型。', 'Available vision models can also be selected.')]), card(L('生成期间', 'While generating'), table=grid(), rows=[L('预览只读 → 完成后才可编辑', 'Read-only preview → editable after completion')])]),
        frame(L('先修复条件，再重试', 'Fix the condition before Retry'), L('无有效单元格、模型不可用或网络错误时，读提示，检查模型与服务后再单击重试。换模型立即生效；切回用过的模型可能恢复已有编辑。', 'For no valid cells, an unavailable model, or a network error, read the message, check the model/service, then Retry. Model changes apply immediately; a previously used model may restore its edits.'), [card(L('未识别到表格单元格', 'No table cells were recognized'), tone='error', rows=[L('检查输入范围、服务与返回的表格结构。', 'Check the input area, service and returned table structure.')]), card(L('结果中的操作', 'Result action'), buttons=[L('重试', 'Retry')], rows=[L('原图不清楚时，新截图比重复同一请求更有用。', 'For unclear input, recapture rather than repeating the same request.')])]),
        frame(L('保存完整表格或临时打开', 'Save the full table or open it'), L('保存为文件始终输出当前整表XLSX，不按局部选区裁切；取消保留编辑，成功后结束截图。打开电子表格文件则生成临时XLSX并交给默认应用，需要长期保留时再另存。', 'Save as file exports the entire current table as XLSX, not just selected cells. Cancel keeps edits; success ends capture. Open spreadsheet file creates a temporary XLSX for the default app; save a lasting copy there.'), [card('table.xlsx', table=grid()), card(L('两种去向', 'Two destinations'), rows=[L('保存为文件 → 指定目录 → 重开核对', 'Save as file → chosen folder → reopen and check'), L('打开电子表格文件 → 临时XLSX → 默认应用', 'Open spreadsheet file → temporary XLSX → default app'), L('取消保存 → 回到当前表格', 'Cancel save → return to the current table')])]),
    ]),
    family('rec-formula-output', L('公式源码：等待、纠错与保存', 'Formula states and source files'), 'formula.mdx', L('遇到问题时', 'troubleshooting'), 'OCR-037;OCR-038;OCR-040;OCR-041', 'screenshotrecognitionwindow.cpp:1544-1588; screenshotrecognitionsessioncontroller.cpp:3337-3384,3630-3669,2840-2858; screenshot_latex_renderer_tests.cpp:313-314; screenshotcontroller.cpp:4978-5037', [
        frame(L('生成中的源码只读', 'Generated source is initially read-only'), L('视觉模型逐步返回内容时先等待。源码仍在增加时不能开始校正；等识别完成、源码可输入后再修改。', 'Wait while the vision model streams content. Source that is still being generated is read-only. Start correcting only after recognition finishes and editing becomes available.'), [card(L('LaTeX公式源码：生成中', 'LaTeX formula source: generating'), code=[r'\frac{x']), card(L('完成后', 'After completion'), code=[r'\frac{x}{2}'], rows=[L('可编辑，再等待当前源码的公式预览。', 'Edit, then wait for the current source preview.')])]),
        frame(L('预览错误不等于识别失败', 'Preview errors differ from recognition errors'), L('示例源码缺少分母参数，预览无法显示。补回参数或撤销最近编辑；已经取得源码时，不必为了修复预览重新识别图片。', 'This example lacks a denominator argument, so preview fails. Add the argument or undo the recent edit; available source does not need another recognition request just to repair its preview.'), [card(L('当前源码', 'Current source'), code=[r'\frac{x}']), card(L('无法预览此公式。请检查 LaTeX 源码', 'Unable to preview this formula. Check the LaTeX source'), tone='error', rows=[L('补为 \\frac{x}{2} → 等待预览更新', 'Change to \\frac{x}{2} → wait for the preview')])]),
        frame(L('局部复制与全文TXT', 'Partial copy or complete TXT'), L('只要表达式时选中源码复制；保存TXT则取得完整当前源码，不受局部选择影响。取消保存保留编辑，保存成功结束截图；重开文件核对命令。', 'Select source to copy only an expression. TXT saving includes the entire current source regardless of selection. Cancel keeps edits; success ends capture. Reopen the file and check its commands.'), [card(L('当前源码', 'Current source'), code=[r'\frac{x}{2}']), card('formula.txt', code=[r'\frac{x}{2}']), card(L('确认结果', 'Check the result'), rows=[L('复制片段 ≠ 保存整条源码', 'Copy a fragment ≠ save all source'), L('重开TXT，再放入目标公式环境。', 'Reopen TXT, then use it in the target formula environment.')])]),
    ]),
    family('rec-conversion-workflow', L('图片转换的模型、复制与输出', 'Image conversion controls'), 'image-conversion.mdx', L('预览复制与保存', 'preview-copy-and-save'), 'OCR-042;OCR-043;OCR-044;OCR-045;OCR-046;OCR-047', 'screenshotimageconversioncontroller.cpp:323-451,464-658; screenshotimageconversionview.cpp:90-98,152-175; screenshotimageconversionclipboard.h:13-29; screenshotrecognitionsessioncontroller.cpp:2840-2853,2891-2909; screenshotcontroller.cpp:4978-5037', [
        frame(L('设置窗口的重试刷新列表', 'Settings Retry refreshes the list'), L('属性栏设置打开图像转换设置。列表加载失败时，检查连接后用这个窗口里的重试刷新；选可用视觉模型后确定。取消只放弃本次选择，不是结果重试。', 'Open Image conversion settings from Settings in the property bar. If the list fails to load, check the connection and Retry in this window. Choose an available vision model and OK; Cancel discards the choice.'), [card(L('图像转换设置', 'Image conversion settings'), fields=[field(L('视觉模型', 'Vision model'), L('从可用列表选择', 'Choose from the available list'))], top_buttons=[L('重试', 'Retry')], buttons=[L('确定', 'OK'), L('取消', 'Cancel')]), card(L('模型来源', 'Model sources'), rows=[L('可用Snow Shot视觉模型，或支持图像的自定义模型。', 'Available Snow Shot vision models or image-capable custom models.')])]),
        frame(L('预览复制与源码复制不同', 'Preview copy differs from source copy'), L('选中预览标题后右键复制，取得可见的Guide文字；工具栏复制到剪贴板取得完整Markdown源码，即使预览仍有局部选择。HTML还提供HTML剪贴板格式。', 'Select the preview heading and right-click Copy for the visible text Guide. Toolbar Copy to clipboard retrieves all Markdown source even with that selection. HTML also supplies an HTML clipboard format.'), [card(L('预览：选中标题', 'Preview: selected heading'), code=['Guide'], selected=True), card(L('预览右键复制', 'Preview context Copy'), code=['Guide']), card(L('工具栏复制到剪贴板', 'Toolbar Copy to clipboard'), code=['# Guide', '- Start'])]),
        frame(L('部分内容不代表完成', 'Partial content is not completion'), L('出现结果不完整时，可先在预览右键复制保留现有内容。结果区域重试会清空这一轮生成内容，从头处理同一张图片。', 'For Incomplete result, first use preview context Copy if you want to retain the visible content. Retry in the result clears generated content and starts again with the same image.'), [card(L('结果不完整：连接中断', 'Incomplete result: connection interrupted'), tone='error', code=['# Guide'], buttons=[L('重试', 'Retry')], rows=[L('先右键复制，按需保留这一部分。', 'Context-copy first if you need this part.')]), card(L('单击结果重试后', 'After result Retry'), rows=[L('旧内容清空 → 重新生成', 'Generated content clears → generation starts again'), L('它不等于设置窗口的模型列表重试。', 'This differs from retrying the model list in Settings.')])]),
        frame(L('保存两份同名配套文件', 'Save the document and its companion'), L('Markdown输出.md与同名.txt，HTML输出.html与同名.txt。保存完整源码，不按预览选区裁切；取消不替换现有文件，成功后结束截图。分别重开文档和TXT核对。', 'Markdown outputs .md plus a matching .txt; HTML outputs .html plus a matching .txt. Saving includes all source, not the preview selection. Cancel does not replace files; success ends capture. Reopen both outputs to check.'), [card(L('Markdown示例', 'Markdown example'), code=['note.md', 'note.txt'], rows=[L('两份都是本轮完整生成源码。', 'Both contain the complete generated source.')]), card(L('HTML示例', 'HTML example'), code=['page.html', 'page.txt']), card(L('取消或保存', 'Cancel or Save'), rows=[L('取消 → 保留当前结果与原文件', 'Cancel → keep the result and existing files'), L('保存成功 → 结束截图 → 打开文件检查', 'Save succeeds → capture ends → open and check')])]),
    ]),
    family('rec-main-ocr-entry', L('不用先绑定按键也能识别', 'Start OCR without assigning keys'), 'models.mdx', L('离线前准备', 'prepare-before-going-offline'), 'OCR-048;OCR-060', 'applicationsearchwidget.cpp:492-504; contentcardwidget.cpp:113-161; settingspagewidget.cpp:506-554; screenshottoolbarlayoutmodel.h:462-470; settingscatalog.cpp:711-720', [
        frame(L('搜索结果只定位动作', 'Search locates the action'), L('在主窗口搜索功能输入文本识别并选择结果。页面定位到全局快捷键中的动作行；选搜索结果本身不会立即截图。', 'Search for Text recognition in the main window and choose the result. This locates its Global shortcuts action row; selecting the search result does not immediately capture.'), [card(L('搜索功能', 'Search function'), fields=[field(L('输入', 'Enter'), L('文本识别', 'Text recognition'))]), card(L('选择结果后', 'After choosing the result'), rows=[L('定位：全局快捷键 → 文本识别', 'Locate: Global shortcuts → Text recognition'), L('这一步尚未启动截图。', 'Capture has not started yet.')])]),
        frame(L('点动作标题，不是未设置', 'Click the title, not Not set'), L('单击文本识别这一行的标题或空白区域启动截图，确认选区后识别。右侧未设置按钮进入快捷键录入；想试用识别不需要先配置它。', 'Click the Text recognition row title or its blank area to capture, then confirm the selection to recognize it. Not set on the right records a shortcut; it is not needed just to try OCR.'), [card(L('全局快捷键动作行', 'Global shortcut action row'), fields=[field(L('可单击的动作标题', 'Clickable action title'), L('文本识别', 'Text recognition'))]), card(L('两个点击去向', 'Two click destinations'), rows=[L('标题或空白区域 → 启动截图识别', 'Title or blank area → capture and recognize'), L('未设置 → 配置快捷键', 'Not set → configure a shortcut')])]),
        frame(L('Mini的两套工具栏分开', 'Mini has separate toolbar layouts'), L('要显示Mini隐藏的文本识别按钮，截图入口改截图工具栏，图像编辑器改固定到屏幕工具栏。把隐藏的工具拖入可见位置；不要只改一套布局就去另一处找按钮。', 'To reveal Mini\'s hidden Text recognition button, edit the screenshot toolbar for screenshots and the Pin to screen toolbar for the image editor. Drag it from Hidden tools to a visible position; the layouts are separate.'), [card(L('截图入口', 'Screenshot entry'), rows=[L('设置 → 截图 → 操作工具栏', 'Settings → Screenshots → Action toolbar'), L('截图工具栏设置', 'Screenshot toolbar settings')]), card(L('图像编辑器入口', 'Image-editor entry'), rows=[L('设置 → 固定到屏幕 → 操作工具栏', 'Settings → Pin to screen → Action toolbar'), L('固定到屏幕工具栏设置', 'Pin to screen toolbar settings')]), card(L('同一个工具', 'The same tool'), rows=[L('隐藏的工具：文本识别 → 可见位置', 'Hidden tools: Text recognition → visible position')])]),
    ]),
    family('rec-editor-save-control', L('文字结果的保存按钮', 'Save the text result'), 'text.mdx', L('复制文字与保存图片', 'copy-text-and-save-an-image'), 'OCR-062', 'screenshottoolpalette.cpp:6826-6827; icons/resources/save.svg; imageeditingwindow.cpp:422-423,1193-1204; imageeditingexportcontroller.cpp:171-269', [
        frame(L('悬停核对保存为文件', 'Check the Save as file tooltip'), L('这是保存为文件按钮的图标。保持图像编辑器中的文本识别结果，悬停核对名称后单击，选择TXT位置；取消保留文字，保存后重开TXT核对。这个文字输出不同于保存原始图片。', 'This is the Save as file glyph. Keep the image editor\'s text-recognition result active, check the tooltip, click it and choose a TXT destination. Cancel keeps text; reopen TXT after saving. This differs from saving the original image.'), [card(L('保存为文件', 'Save as file'), save=True), card(L('保持文字识别结果', 'Keep Text recognition active'), code=['Start', 'Goal']), card(L('文件对话框的去向', 'File-dialog outcomes'), rows=[L('取消 → 当前文字仍可修改', 'Cancel → current text remains editable'), L('保存 → recognized-goal.txt', 'Save → recognized-goal.txt'), L('重开TXT → 检查Start与Goal两行', 'Reopen TXT → check the two lines Start and Goal')])]),
    ]),
]

# An asset is attributed only to the operation actually shown in that frame.
FRAME_BINDINGS = {
    'rec-model-controls': [
        ('OCR-012;OCR-013', L('选择模型', 'choose-a-model')),
        ('OCR-014;OCR-015', L('检测与处理策略', 'detection-and-processing')),
        ('OCR-017;OCR-018', L('降低等待时间', 'reduce-waiting-time')),
        ('OCR-017;OCR-018', L('降低等待时间', 'reduce-waiting-time')),
        ('OCR-016', L('降低等待时间', 'reduce-waiting-time')),
    ],
    'rec-text-transforms': [
        ('OCR-006', None), ('OCR-007', None), ('OCR-008', None), ('OCR-008', None),
    ],
    'rec-barcode-results': [
        ('OCR-032', None), ('OCR-033;OCR-034', None),
        ('OCR-034;OCR-035', L('复制与打开链接', 'copy-and-open-links')),
        ('OCR-036', L('没有识别结果时', 'when-no-result-is-found')),
    ],
    'rec-table-input': [
        ('OCR-021;OCR-027', L('修正单元格', 'correct-cells')),
        ('OCR-022;OCR-027', L('修正单元格', 'correct-cells')),
        ('OCR-027', None), ('OCR-027', None),
        ('OCR-026', None), ('OCR-027', None),
        ('OCR-028', L('恢复与重试', 'restore-and-retry')),
    ],
    'rec-table-workflow': [
        ('OCR-019;OCR-020', L('选择识别模型', 'select-a-recognition-model')),
        ('OCR-031', None),
        ('OCR-029;OCR-030', L('复制粘贴与导出', 'copy-paste-and-export')),
    ],
    'rec-formula-output': [
        ('OCR-037;OCR-038', L('校正与预览', 'correct-and-preview')),
        ('OCR-041', None),
        ('OCR-040', L('复制与保存', 'copy-and-save')),
    ],
    'rec-conversion-workflow': [
        ('OCR-042;OCR-043;OCR-044', L('完成一次转换', 'run-a-conversion')),
        ('OCR-045', None),
        ('OCR-047', L('失败时重新处理', 'retry-after-a-failure')),
        ('OCR-046', None),
    ],
    'rec-main-ocr-entry': [('OCR-048;OCR-060', None), ('OCR-048;OCR-060', None), ('OCR-048', None)],
}


def code_lines(value):
    # Visual wrapping never changes the sample's underlying source/payload.
    result=[]
    for row in wrap(value,332,20):
        current,units='',0.0
        for character in row:
            cost=1 if unicodedata.east_asian_width(character) in 'WF' else .56
            if current and units+cost>16.6:
                result.append(current);current,units='',0.0
            current+=character;units+=cost
        if current:
            result.append(current)
    return result or ['']


def draw_card(item, lang):
    out, y = '', 30
    title_lines = wrap(choose(item['title'], lang), 356, 22)
    for value in title_lines:
        out += text(18, y, value, 22, RED if item['tone']=='error' else PURPLE, 650)
        y += 28
    y += 5
    if item['top_buttons']:
        for value in item['top_buttons']:
            out += rect(260,y,114,36,'#f1edfb','#bdb0ea',8)+text(273,y+25,choose(value,lang),20,PURPLE,600)
            y += 47
    if item['save']:
        out += rect(18, y, 58, 58, '#f0edfb', '#bdb0ea', 9)
        out += f'<g transform="translate(26 {y+8}) scale(0.041015625)"><path d="{SAVE_PATH}" fill="{PURPLE}" fill-rule="evenodd"/></g>'
        label = choose(L('悬停提示：保存为文件', 'Tooltip: Save as file'), lang)
        for value in wrap(label, 252, 20):
            out += text(90, y+25, value, 20)
            y += 26
        y = max(y+18, 113)
    for f in item['fields']:
        for value in wrap(choose(f['label'], lang), 356, 18):
            out += text(18, y+15, value, 18, MUTED)
            y += 23
        value_lines = wrap(choose(f['value'], lang), 320, 20)
        height = 16+26*len(value_lines)
        is_switch = choose(f['label'], 'en') in ['Hardware acceleration', 'Resident recognition process', 'Model hot start', 'Show original image preview']
        if is_switch:
            on=choose(f['value'],'en')=='On'
            color='#a8b5c6' if f['disabled'] else (PURPLE if on else '#8493a8')
            out += rect(18,y+5,59,30,color,color,15)
            out += f'<circle cx="{62 if on else 33}" cy="{y+20}" r="11" fill="white"/>'
            out += text(93,y+28,choose(f['value'],lang),20,'#8393a4' if f['disabled'] else INK)
        else:
            out += rect(18, y, 356, height, '#eef1f5' if f['disabled'] else '#fff', '#c8d3e6', 6)
            for i, value in enumerate(value_lines):
                out += text(30, y+28+26*i, value, 20, '#8393a4' if f['disabled'] else INK)
        y += height+9
        if f['options']:
            for option in f['options']:
                out += text(34, y+18, choose(option, lang), 20, PURPLE)
                y += 29
            y += 7
    if item['image']:
        source = INPUTS[item['image']]
        out += f'<image x="58" y="{y}" width="276" height="276" href="data:image/png;base64,{source["png_data"]}"/>'
        y += 288
    if item['table']:
        t = item['table']; cell_w, cell_h = 116, 42
        for row in range(3):
            for column in range(3):
                if t['merged'] and row==1 and column==2:
                    continue
                width = cell_w*2 if t['merged'] and row==1 and column==1 else cell_w
                x, yy = 18+column*cell_w, y+row*cell_h
                selection=t['selected']
                selected = selection==[row,column] or t['editor']==[row,column]
                if selection and len(selection)==4:
                    selected=selected or selection[0]<=row<=selection[2] and selection[1]<=column<=selection[3]
                out += rect(x, yy, width, cell_h, '#eee9fb' if selected else ('#eaf0f8' if row==0 else 'white'), '#b9c9da', 0)
                if t['merged'] and row==1 and column==1:
                    out += text(x+10, yy+17, '2', 18) + text(x+10, yy+37, '80', 18)
                else:
                    value=choose(t['values'][row*3+column],lang)
                    out += text(x+10, yy+28, value, 20)
                    if t['editor']==[row,column]:
                        out += f'<path d="M{x+27} {yy+9} V{yy+32}" stroke="{BLUE}" stroke-width="1.5"/>'
        y += cell_h*3+18
    if item['code'] is not None:
        lines=[line for value in item['code'] for line in code_lines(choose(value,lang))]
        out += rect(18, y, 356, 20+28*len(lines), '#f5f7fb', 'none', 6)
        for index, value in enumerate(lines):
            if item['selected']:
                out += rect(26, y+7+28*index, min(338,max(44,len(value)*10.8)), 27, '#dbeafb', 'none', 2)
            out += text(29, y+30+28*index, value, 20)
        y += 33+28*len(lines)
    if item['menu']:
        for index,value in enumerate(item['menu']):
            out += rect(18,y,356,34,'#f4f1fc' if index==0 else 'white','#e3e6ef',3)
            out += text(30,y+24,choose(value,lang),20)
            y += 37
        y += 8
    if item['buttons']:
        xx=18
        for value in item['buttons']:
            label=choose(value,lang)
            width=max(84,min(164,28+sum(20 if unicodedata.east_asian_width(c) in 'WF' else 11 for c in label)))
            out += rect(xx,y,width,39,'#f1edfb','#bdb0ea',8)+text(xx+14,y+27,label,20,PURPLE,600)
            xx += width+12
        y += 54
    for row in item['rows']:
        for value in wrap(choose(row,lang),356,20):
            out += text(18,y+18,value,20,INK)
            y += 27
        y += 8
    return rect(0,0,392,y+7,'#fff','#d1dbE8',11)+out, y+7


def draw_body(family_data, step, lang):
    out, y = '', 0
    for item in family_data['frames'][step]['cards']:
        value, height=draw_card(item,lang)
        out += f'<g transform="translate(24 {y})">{value}</g>'
        y += height+17
    return out,y


def render(family_data, step, lang, height):
    frame_data=family_data['frames'][step]
    title, label=choose(family_data['title'],lang),choose(frame_data['label'],lang)
    kind='Instructional illustration' if lang=='en' else '操作示意'
    body=''
    y=35
    for value in wrap(title,390,23):
        body += text(24,y,value,23,INK,700);y+=29
    for value in wrap(label,390,20):
        body += text(24,y+6,value,20,BLUE,600);y+=27
    y+=20
    content,_=draw_body(family_data,step,lang)
    body+=f'<g transform="translate(0 {y})">{content}</g>'
    body+=f'<path d="M24 {height-49} H416" stroke="#dce3ef"/>'
    body+=text(24,height-22,kind,17,MUTED)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="{height}" viewBox="0 0 440 {height}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title+": "+label)}</title><desc id="desc">{escape(choose(frame_data["caption"],lang))}</desc>'
        f'<rect width="440" height="{height}" rx="16" fill="#f5f7fc"/>'
        '<g font-family="system-ui,-apple-system,PingFang SC,Microsoft YaHei,sans-serif">'+body+'</g></svg>'
    )


def main():
    rows, snippets, geometry=[],[],[]
    for group in FAMILIES:
        # Every locale/frame in one player has an equal outer size.
        heights=[]
        for lang in ['zh','en']:
            for index, data in enumerate(group['frames']):
                header=35+29*len(wrap(choose(group['title'],lang),390,23))+27*len(wrap(choose(data['label'],lang),390,20))+20
                _,body_height=draw_body(group,index,lang)
                heights.append(header+body_height+58)
        height=math.ceil(max(heights)/10)*10
        per_step={}
        if group['name']=='rec-model-controls':
            count=len(group['frames'])
            for index in [0,1]:
                per_step[index]=math.ceil(max(heights[index],heights[count+index])/10)*10
            shared=math.ceil(max(heights[index] for index in [2,3,4,count+2,count+3,count+4])/10)*10
            per_step.update({index:shared for index in [2,3,4]})
        assert height<=1250,(group['name'],height)
        for lang in ['zh','en']:
            frames=[]
            for index,data in enumerate(group['frames']):
                frame_height=per_step.get(index,height)
                name=group['name']+(f'-{index+1}' if len(group['frames'])>1 else '')+'.svg'
                asset=PUBLIC/('en' if lang=='en' else '')/name;asset.parent.mkdir(parents=True,exist_ok=True)
                asset.write_text(render(group,index,lang,frame_height),encoding='utf-8')
                frames.append({'src':'/images/guides/'+('en/' if lang=='en' else '')+name,'alt':choose(data['caption'],lang),'label':choose(data['label'],lang),'caption':choose(data['caption'],lang)})
                bound_ids,bound_section=FRAME_BINDINGS.get(group['name'],[(group['ids'],None)]*len(group['frames']))[index]
                rows.append({
                    'Asset':asset.relative_to(ROOT).as_posix(),'Feature IDs':bound_ids,
                    'Teaching purpose':choose(data['caption'],lang),
                    'Documentation path':f'docs/{lang}/guides/recognition/{group["page"]}#{choose(bound_section or group["sections"],lang)}',
                    'Associated step':choose(data['label'],lang),'Source':'release f02f50e; '+group['source']+'; artifacts/review-recognition-depth-20261110b/review.json',
                    'Production method':'原创专属双语SVG；scripts/generate-guide-recognition-followup-assets.py；精确控制名与状态/数据变化；无不确定完整工具栏；不是运行截图',
                    'Status':'已制作专属教学示意；native_ui与逐项验收另记',
                    'Capture prerequisites and next action':'先做离线几何/逐图双语检查及当前网站播放器检查；真实产品/服务行为需独立运行证据，不从示意图推导通过',
                })
                geometry.append({'asset':asset.relative_to(ROOT).as_posix(),'width':440,'height':frame_height,'family':group['name'],'step':index+1})
            snippets.append({'family':group['name'],'locale':lang,'page':f'docs/{lang}/guides/recognition/{group["page"]}','title':choose(group['title'],lang),'frames':frames})
    for key,data in INPUTS.items():
        path=PUBLIC/data['filename'];path.write_bytes(base64.b64decode(data['webp_data']))
        rows.append({'Asset':path.relative_to(ROOT).as_posix(),'Feature IDs':'OCR-032;OCR-033;OCR-036','Teaching purpose':'公开练习输入；仅说明编码内容：'+data['payload'],
            'Documentation path':'docs/zh/guides/recognition/barcode.mdx#识别并取得内容; docs/en/guides/recognition/barcode.mdx#recognize-and-retrieve-content','Associated step':'打开原尺寸练习图，保留完整白边再框选',
            'Source':'artifacts/ui-fixtures/barcode-20261110b/'+data['source_file']+'; fixture-independent-decode.json; original PNG SHA256='+data['png_sha256'],
            'Production method':'input fixture；CoreImage二维码/确定性EAN13生成；原始PNG解码RGBA逐字节相同的lossless WebP；固定bytes嵌入generator可复现；不是Snow Shot UI截图或成功输出',
            'Status':'已制作可下载练习输入；独立码解码不是Snow Shot运行验证','Capture prerequisites and next action':'在普通Snow Shot UI中独立读取、复制并核对payload；不承诺所有条码格式，Code128不用于应成功示例'})
    ART.mkdir(exist_ok=True)
    with (ART/'assets-recognition-followup-20261110b.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (ART/'recognition-followup-frames-20261110b.json').write_text(json.dumps({'players':snippets,'geometry':geometry},ensure_ascii=False,indent=2)+'\n')
    print(f'Generated {len(geometry)} bilingual instructional SVGs, {len(INPUTS)} shared practice inputs and {len(rows)} independent registry rows.')


if __name__=='__main__':
    main()
