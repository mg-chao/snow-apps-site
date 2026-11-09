"""Merge original asset registries and localized copies without duplicating teaching tasks."""
from pathlib import Path
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
ASSETS = ROOT / 'docs/public/images/guides'
COLS = ['Asset', 'Feature IDs', 'Teaching purpose', 'Documentation path', 'Associated step',
        'Source', 'Production method', 'Status', 'Capture prerequisites and next action']
MIG = json.loads((ART / 'mdx-route-migration.json').read_text())
SOURCE_NAMES = ['assets-annotations.csv', 'assets-capture-start.csv',
                'assets-recognition-pinning.csv', 'assets-recording-settings.csv',
                'assets-image-audit.csv', 'assets-editor-crop-diagrams.csv']
LOCALIZATION = ART / 'assets-english-localization.csv'


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def ids(value):
    return sorted(set(re.findall(r'\b[A-Z][A-Z0-9]*-\d+\b', value)),
                  key=lambda x: (x.split('-')[0], int(x.split('-')[1])))


def norm_doc(raw):
    result = []
    for item in re.split(r'\s*;\s*', raw or ''):
        if not item.strip():
            continue
        path, *anchor = item.strip().split('#', 1)
        if not path.startswith(('docs/', 'artifacts/')):
            path = 'docs/zh/guides/' + path
        path = MIG.get(path, path)
        if not (ROOT / path).exists() and path.endswith('.md') and (ROOT / (path + 'x')).exists():
            path += 'x'
        if (ROOT / path).exists():
            result.append(path + ('#' + anchor[0] if anchor else ''))
    return sorted(set(result))


docs = {p.relative_to(ROOT).as_posix(): p.read_text()
        for locale in ('zh', 'en') for p in (ROOT / f'docs/{locale}/guides').rglob('*')
        if p.suffix in ('.md', '.mdx')}
coverage = {}
for path in ART.glob('coverage-*.csv'):
    for row in read_csv(path):
        if row.get('Feature ID'):
            coverage[row['Feature ID']] = row


def doc_from_ids(feature_ids):
    paths = []
    for fid in feature_ids:
        paths += norm_doc(coverage.get(fid, {}).get('Documentation path and section', ''))
    return sorted(set(x.split('#')[0] for x in paths if x.startswith('docs/')))


def asset_path(raw):
    if raw.startswith('GuideRecordingDemo '):
        return 'theme/components/GuideRecordingDemo.tsx'
    raw = raw.lstrip('/')
    if raw.startswith('images/'):
        raw = 'docs/public/' + raw
    elif '/' not in raw:
        raw = 'docs/public/images/guides/' + raw
    # Keep original evidence inputs intact while resolving optimized public assets.
    path = ROOT / raw
    if path.suffix == '.png' and not path.exists() and path.with_suffix('.webp').is_file():
        return Path(raw).with_suffix('.webp').as_posix()
    return raw


def references(path):
    if path.startswith('docs/public/images/guides/'):
        needle = '/images/guides/' + path.removeprefix('docs/public/images/guides/')
    else:
        needle = 'GuideSteps' if path.endswith('GuideSteps/index.tsx') else Path(path).stem
    return sorted(key for key, value in docs.items() if needle in value)


def uniqjoin(first, second):
    return '; '.join(dict.fromkeys(x.strip() for x in (first + '; ' + second).split('; ') if x.strip()))


merged = {}
source_row_count = 0
for source_name in SOURCE_NAMES:
    raw_rows = read_csv(ART / source_name)
    source_row_count += len(raw_rows)
    for raw in raw_rows:
        original = raw.get('Asset', raw.get('Asset file', ''))
        path = asset_path(original)
        feature_ids = ids(raw.get('Feature IDs', raw.get('Feature ID', '')))
        # Correct attribution in the merged view without rewriting source inputs.
        if Path(path).stem == 'ann-arrow-native-edited':
            feature_ids = ['ANN-019', 'ANN-028']
        purpose = raw.get('Teaching purpose', raw.get('Teaching purpose and step', ''))
        step = raw.get('Associated step', '')
        if not step:
            match = re.match(r'^(\d+)\.\s*(.*)', purpose)
            step = '步骤' + match[1] + '：' + match[2] if match else purpose
        source = raw.get('Source', '')
        method = raw.get('Production method', '')
        combined = raw.get('Source and production method', '')
        if combined:
            method = combined + ('；标注：' + raw['Caption'] if raw.get('Caption') else '')
            source = 'artifacts/research-annotations.md（产品源码与发行标签证据）'
            for marker in ['；手工', '；原创脚本']:
                if marker in combined and not combined.startswith(('手工', '原创')):
                    source = combined.split(marker, 1)[0] + '；artifacts/research-annotations.md'
                    break
            logs = re.findall(r'(?:runtime-[\w-]+\.json|generate-[\w-]+\.py)', combined)
            if logs:
                source += '；' + '；'.join('artifacts/' + x for x in logs)
            if 'MCP' in combined and not logs:
                source += '；artifacts/runtime-mcp-fixture.json'
            if 'arrowhead-' in combined:
                source += '；产品 snow_shot/src/presentation/components/icons/resources/arrowhead-*.svg'
        source = source or '分组研究登记：artifacts/' + source_name
        mode = re.search(r'mode=(\w+)', original)
        if mode:
            step = '组件模式 mode=' + mode[1] + '；' + step
        doc_paths = norm_doc(raw.get('Documentation path', raw.get('Page', '')))
        actual_refs = references(path)
        if mode:
            actual_refs = [x for x in actual_refs if ('trim-export' in x) == (mode[1] == 'trim')]
        doc_paths = sorted(set(doc_paths + actual_refs)) or doc_from_ids(feature_ids)
        status = raw.get('Status', raw.get('Asset status', '已制作；逐项验收另记'))
        row = dict(zip(COLS, [path, ';'.join(feature_ids), purpose, '; '.join(doc_paths), step,
                              source, method, '已制作（仅本资产范围）；' + status,
                              raw.get('Capture prerequisites and next action', '')]))
        key = (path, mode[1] if mode else '')
        if key in merged:
            previous = merged[key]
            for column in COLS:
                if column != 'Asset':
                    previous[column] = uniqjoin(previous[column], row[column])
            previous['Feature IDs'] = ';'.join(ids(previous['Feature IDs']))
        else:
            merged[key] = row

# English SVGs are localized copies of an existing instructional asset, not new demonstrations.
localized_count = 0
if LOCALIZATION.exists():
    localization_rows = read_csv(LOCALIZATION)
    for localized in localization_rows:
        assert set(localized) == {'Asset', 'Source', 'Production method'}, 'Unexpected localization CSV schema'
        path, source_path = asset_path(localized['Asset']), asset_path(localized['Source'])
        assert path.startswith('docs/public/images/guides/en/'), path
        original = merged.get((source_path, ''))
        if original is None:
            raise ValueError('Localized asset has no original teaching registry: ' + source_path)
        row = original.copy()
        row['Asset'] = path
        english_docs = references(path)
        if not english_docs:
            english_docs = [x.split('#')[0].replace('docs/zh/guides/', 'docs/en/guides/')
                            for x in original['Documentation path'].split('; ')
                            if x.startswith('docs/zh/guides/')]
            english_docs = [x for x in english_docs if (ROOT / x).is_file()]
        row['Documentation path'] = '; '.join(sorted(set(english_docs)))
        row['Source'] = ('英文图示本地化；原始资产：' + source_path + '；原始证据：' + original['Source']
                         + '；artifacts/assets-english-localization.csv；artifacts/guide-svg-en-*.json')
        row['Production method'] = localized['Production method']
        row['Status'] = '已制作英文文本本地化副本；原几何与操作教学范围不变；不是新增教学演示；验收另记'
        merged[(path, '')] = row
        localized_count += 1

shared = 'theme/components/GuideSteps/index.tsx'
shared_docs = references(shared)
shared_ids = ids(';'.join(row['Feature IDs'] for row in merged.values()
                          if set(row['Documentation path'].split('; ')) & set(shared_docs)))
merged[(shared, '')] = dict(zip(COLS, [shared, ';'.join(shared_ids),
    '共享分镜播放、暂停、逐步前后和放大查看；本组件不替代专属分镜', '; '.join(shared_docs),
    '所有 GuideSteps 调用；具体动作见每张分镜行',
    'theme/components/GuideSteps/index.tsx；各语言页 frames 数据；artifacts/guide-validation.md',
    '共享 React 播放控件；字幕与静态帧支持逐步查看；语言副本不重复计算教学任务',
    '已实现；浏览器实查范围见验证报告；不单独计作新的操作演示',
    '专属内容缺口仍按操作行保留，不因共享组件或本地化副本存在而完成']))
produced = list(merged.values())
actual = {p.relative_to(ROOT).as_posix() for p in ASSETS.rglob('*') if p.suffix in ('.svg', '.png', '.webp')}
registered = {row['Asset'] for row in produced}
omitted = sorted(actual - registered)
for path in omitted:
    refs = references(path)
    feature_ids = ids(';'.join(x['Feature ID'] for x in coverage.values()
                              if x.get('Documentation path and section', '').split('#')[0] in refs))
    produced.append(dict(zip(COLS, [path, ';'.join(feature_ids), '实有资源，原分组登记遗漏，待补教学目的',
        '; '.join(refs), '待补', '磁盘实有文件自动对账发现', '待补制作方式；不得猜测来源',
        '文件存在，登记待补，不视为已验收', '核对生成记录与引用，补完整来源/步骤后验收'])))

all_gaps = read_csv(ART / 'annotation-asset-gaps.csv')
gaps = [row for row in all_gaps if row['Status'].startswith('未完成')]
missing = []
for gap in gaps:
    fid = gap['Feature ID']
    doc = norm_doc(coverage.get(fid, {}).get('Documentation path and section', ''))
    missing.append(dict(zip(COLS, ['MISSING:' + fid, fid, gap['Specific asset gap'], '; '.join(doc),
        coverage.get(fid, {}).get('Specific feature or operation', gap['Specific asset gap']),
        'artifacts/annotation-asset-gaps.csv；对应 coverage-annotations.csv；'
        + ('artifacts/research-release-editor-crop.md' if fid.startswith('IMG-')
           else 'artifacts/research-annotations.md'),
        '尚未制作；按具体捕获或教学重建计划实施', gap['Status'],
        '当前缺口/条件：' + gap['Current blocker or limitation'] + '；下一步：' + gap['Actionable next capture']])))
missing_ids = {row['Feature ID'] for row in gaps}
for row in produced:
    pending = sorted(set(ids(row['Feature IDs'])) & missing_ids)
    if pending:
        row['Capture prerequisites and next action'] = uniqjoin(row['Capture prerequisites and next action'],
            '同页仍需专属资产：' + ','.join(pending) + '；见对应 MISSING 行；关联 ID 不表示全部操作已覆盖')
produced.sort(key=lambda row: (0 if row['Asset'].startswith('docs/public/') else 1,
                               row['Asset'], row['Associated step']))
all_rows = produced + missing
with (ART / 'guide-assets.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=COLS)
    writer.writeheader()
    writer.writerows(all_rows)
invalid = [row['Asset'] for row in produced if not (ROOT / row['Asset']).is_file()]
invalid_docs = [path for row in all_rows for path in row['Documentation path'].split('; ')
                if path and not (ROOT / path.split('#')[0]).is_file()]
original_svg = sum(path.endswith('.svg') and '/guides/en/' not in path for path in actual)
english_svg = sum(path.endswith('.svg') and '/guides/en/' in path for path in actual)
png_count = sum(path.endswith('.png') for path in actual)
webp_count = sum(path.endswith('.webp') for path in actual)
components = [row for row in produced if row['Asset'].endswith('.tsx')]
unique_components = len({row['Asset'] for row in components})


def table(rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', '<br>')
    return ('| ' + ' | '.join(COLS) + ' |\n|' + '|'.join(['---'] * len(COLS)) + '|\n'
            + '\n'.join('| ' + ' | '.join(cell(row.get(c, '')) for c in COLS) + ' |' for row in rows) + '\n')


md = f'''# Snow Shot 双语手册资产总登记

五份原始登记保持不变，合并时统一字段与迁移路径；英文图示从三字段本地化 CSV 追加，继承原图的 Feature IDs、教学目的与关联步骤，并关联英文教程。Feature IDs 仅表示关联主题，不能替代逐项验收。

当前图像：**{original_svg} 个原始 SVG + {english_svg} 个英文 SVG 副本 + {webp_count} 个共享 WebP + {png_count} 个共享 PNG**。SVG 本地化副本不作为新的教学示范翻倍计算。组件 **{len(components)} 个逻辑条目 / {unique_components} 个实际 TSX 文件**；capture 与 trim 各保留一个模式，共享组件在中英文页面复用。已制作登记 **{len(produced)} 行**，未制作专项资产 **{len(missing)} 行**（原 {len(all_gaps)} 项已补齐 {len(all_gaps)-len(gaps)} 项），共 **{len(all_rows)} 行**。

原始输入：{', '.join('`' + x + '`' for x in SOURCE_NAMES)}。本地化输入：`assets-english-localization.csv`，字段固定为 Asset、Source、Production method；Source 指向原始 SVG。英文翻译/几何副本、真实渲染图与原生界面截图的制作方式分别记录，均不会自动使产品操作验收通过。

## 已制作文件与组件

{table(produced)}
## 未制作的专项资产

{table(missing)}
## 对账结果

- 磁盘 SVG/PNG/WebP 未登记：{len(actual - {row['Asset'] for row in produced})}。
- 登记已制作文件不存在：{len(invalid)}。
- 文档目标文件不存在：{len(invalid_docs)}。
- 自动补入但来源/步骤仍待补的资源：{len(omitted)}。
- 已从原图完整继承来源与操作范围的英文副本：{localized_count}。
- 原始五份 CSV 未被合并脚本改写；原生箭头结果 ANN-019 / ANN-028 的归属仅在合并视图校正。
'''
(ART / 'guide-assets.md').write_text(md)
print(json.dumps({'source_rows': source_row_count, 'svg': original_svg + english_svg,
    'original_svg': original_svg, 'english_localized_svg': english_svg, 'png': png_count, 'webp': webp_count,
    'localized_registry_rows': localized_count, 'produced_rows': len(produced),
    'produced_unique_files': len({row['Asset'] for row in produced}),
    'component_mode_rows': len(components), 'component_unique_files': unique_components,
    'missing_rows': len(missing), 'total_rows': len(all_rows), 'originally_omitted': omitted,
    'missing_files': invalid, 'invalid_docs': invalid_docs}, ensure_ascii=False))
