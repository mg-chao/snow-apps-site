"""Generate reviewed English teaching diagrams while preserving original drawings."""
from pathlib import Path
import csv
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs/public/images/guides'
ET.register_namespace('', 'http://www.w3.org/2000/svg')


def chinese_caption(text):
    text = re.sub(r'(?:Snow Shot|macOS)\s+1\.5\.2', lambda m: m[0].split()[0] if m[0].startswith('macOS') else 'Snow Shot', text)
    text = text.replace('源码核对的专属教学重建', '操作示意').replace('源码核对的教学示意', '操作示意')
    text = text.replace('源码核对的教学重建', '操作示意')
    text = text.replace('根据 Snow Shot 源码与中文翻译重建的操作示意', '操作示意')
    text = text.replace('菜单按源码顺序重建；未模拟某张图片的实际检测区域。', '单击一个类别，将滤镜应用到对应区域。')
    text = text.replace('代理不是 API 地址；MCP 不是普通用户的截图按钮。', '代理用于网络连接；MCP 用于连接本机客户端。')
    text = text.replace('按已核对的操作重建，非应用截图', '操作示意')
    text = re.sub(r'[，,；; ·]*非应用(?:截图\s*[/、或]\s*录屏|截图|录屏)', '', text)
    text = text.replace('教学示意', '操作示意')
    text = re.sub(r'(操作示意)[ ·]+操作示意', r'\1', text)
    return text.strip(' ·，,；;')


def english_caption(text):
    text = re.sub(r'(?:Snow Shot|macOS)\s+1\.5\.2', lambda m: 'macOS' if m[0].startswith('macOS') else 'Snow Shot', text)
    text = re.sub(r'[.,; ·—-]*\s*(?:not an app|not a native app|not a real app)\s+(?:capture\s*/\s*recording|screenshot or recording|capture or recording|recording|capture|screenshot)\.?', '', text, flags=re.I)
    text = re.sub(r'(?:Source[- ](?:backed|checked|verified)|Checked[- ]source)\s+', '', text, flags=re.I)
    return text.strip(' ·,;')



def estimated_text_width(text, size, bold=False):
    """Conservative Latin advance estimate; fit by font size, never distort glyphs."""
    units = 0.0
    for char in text:
        if char.isspace():
            units += .30
        elif char in "ilI.,:;'!|`":
            units += .28
        elif char in "ftjr()[]":
            units += .38
        elif char in "MW@%":
            units += .88
        elif char.isupper():
            units += .68
        elif char.isdigit():
            units += .58
        elif ord(char) > 255:
            units += .95
        else:
            units += .54
    return units * size * (1.05 if bold else 1.0)


def fit_translated_text(root, translated):
    """Use the containing panel and adjacent labels, keeping the original geometry."""
    def number(node, key, default=0):
        try:
            return float(node.get(key, str(default)).removesuffix('px'))
        except ValueError:
            return default
    view = [float(value) for value in root.get('viewBox', '0 0 960 480').split()]
    rectangles = [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'rect']
    texts = [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'text']
    for node in translated:
        if node.tag.rsplit('}', 1)[-1] not in ('text', 'tspan') or node.get('x') is None:
            continue
        x, y = number(node, 'x'), number(node, 'y')
        size = number(node, 'font-size', 16)
        left, right = view[0] + 14, view[0] + view[2] - 14
        containing = []
        for rect in rectangles:
            rx, ry = number(rect, 'x'), number(rect, 'y')
            width, height = number(rect, 'width'), number(rect, 'height')
            if rx <= x <= rx + width and ry <= y <= ry + height and width > 30:
                containing.append((width * height, rx + 10, rx + width - 10))
        if containing:
            _, left, right = min(containing)
        anchor = node.get('text-anchor', 'start')
        # Avoid a following label on the same baseline, including centered labels.
        for neighbor in texts:
            if neighbor is node or not neighbor.text:
                continue
            nx, ny = number(neighbor, 'x'), number(neighbor, 'y')
            if nx > x + 6 and abs(ny-y) <= max(3, size*.12):
                neighbor_width = estimated_text_width(neighbor.text, number(neighbor, 'font-size', 16))
                neighbor_left = nx - (neighbor_width/2 if neighbor.get('text-anchor') == 'middle' else 0)
                right = min(right, neighbor_left-12)
        available = right-x
        if anchor == 'middle':
            available = 2*min(x-left, right-x)
        elif anchor == 'end':
            available = x-left
        # Rotated diagram labels are reviewed separately; do not invent new layout geometry.
        if available <= 8:
            continue
        width = estimated_text_width(node.text or '', size, node.get('font-weight') in ('600', '700', 'bold'))
        node.attrib.pop('textLength', None)
        node.attrib.pop('lengthAdjust', None)
        if width > available:
            node.set('font-size', str(round(size * available / width, 2)))


catalog = {}
for path in sorted((ROOT / 'artifacts').glob('guide-svg-en-*.json')):
    for chinese, value in json.loads(path.read_text()).items():
        if not value['en'].strip():
            raise ValueError(f'Untranslated diagram text in {path.name}: {chinese}')
        for filename in value['assets']:
            catalog[(filename, chinese)] = english_caption(value['en'])
            catalog[(filename, chinese_caption(chinese))] = english_caption(value['en'])

output = ASSETS / 'en'
output.mkdir(exist_ok=True)
rows = []
for source in sorted(ASSETS.glob('*.svg')):
    tree = ET.parse(source)
    translated = []
    for node in tree.getroot().iter():
        if node.tag.rsplit('}', 1)[-1] not in ('text', 'tspan', 'title', 'desc') or not node.text:
            continue
        original = node.text
        if re.search('[\u4e00-\u9fff]', original):
            node.text = catalog[(source.name, original)]
            translated.append(node)
    if source.name == 'tr-text.svg':
        # Give the full English button label room without shrinking its type.
        # This is a teaching diagram; the source Chinese diagram is unchanged.
        for node in tree.getroot().iter():
            if (node.tag.rsplit('}', 1)[-1] == 'rect'
                    and node.get('x') == '541' and node.get('y') == '365'):
                node.set('width', '226')
            if node.tag.rsplit('}', 1)[-1] == 'text' and node.text == 'On error: retry':
                node.set('x', '785')
    fit_translated_text(tree.getroot(), translated)
    destination = output / source.name
    tree.write(destination, encoding='utf-8', xml_declaration=True)
    # Keep the public Chinese diagrams equally focused on the user's task.
    chinese_tree = ET.parse(source)
    changed = False
    for node in chinese_tree.getroot().iter():
        if node.tag.rsplit('}', 1)[-1] in ('text', 'tspan', 'title', 'desc') and node.text:
            cleaned = chinese_caption(node.text)
            if cleaned != node.text:
                node.text, changed = cleaned, True
    if changed:
        chinese_tree.write(source, encoding='utf-8', xml_declaration=True)
    rows.append({'Asset': destination.relative_to(ROOT).as_posix(), 'Source': source.relative_to(ROOT).as_posix(), 'Production method': 'Reviewed English text from artifacts/guide-svg-en-*.json; original vector geometry retained; text fitted by proportional font-size adjustment within panels and adjacent labels; no horizontal glyph compression. Instructional diagram, not runtime evidence.'})

for page in (ROOT / 'docs/en/guides').rglob('*'):
    if page.suffix not in ('.md', '.mdx'):
        continue
    text = page.read_text()
    text = re.sub(r'/images/guides/(?!en/)([A-Za-z0-9_.-]+\.svg)', r'/images/guides/en/\1', text)
    page.write_text(text)

with (ROOT / 'artifacts/assets-english-localization.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['Asset', 'Source', 'Production method'])
    writer.writeheader()
    writer.writerows(rows)
print(f'Generated {len(rows)} English teaching diagrams and updated English tutorial references.')
