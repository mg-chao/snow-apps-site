"""Render current source-analysis delivery while retaining historical runtime ledgers."""

from collections import Counter
import csv
import hashlib
import json
import re
import subprocess
import sys


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def render(root):
    art = root / 'artifacts'
    # Always refresh from the canonical rows and current signed evidence. A prior
    # green report must never survive a changed document/source/asset/manifest.
    subprocess.run([sys.executable, str(root / 'scripts/check-guide-coverage.py')],
                   cwd=root, check=True, capture_output=True, text=True)
    evaluation = json.loads((art / 'guide-code-validation-evaluation.json').read_text())
    rows = read_csv(art / 'guide-coverage.csv')
    policy = json.loads((art / 'guide-validation-policy.json').read_text())
    manifest = json.loads((art / 'guide-code-validation-inputs.json').read_text())
    site = json.loads((art / 'guide-site-check.json').read_text())
    website = json.loads((root / manifest['website_review']['path']).read_text())
    runtime = json.loads((art / 'guide-acceptance-evaluation.json').read_text())
    criteria = read_csv(art / 'guide-acceptance-evidence.csv')
    scopes = read_csv(art / 'guide-acceptance-scopes.csv')
    history = {name: hashlib.sha256((art / name).read_bytes()).hexdigest()
               for name in ('guide-acceptance-evidence.csv', 'guide-acceptance-scopes.csv')}
    inventory = []
    sequences = []
    embeds = 0
    modes = set()
    arrow_demo = False
    for locale in ('zh', 'en'):
        for page in sorted((root / f'docs/{locale}/guides').rglob('*')):
            if page.suffix not in ('.md', '.mdx'):
                continue
            path = page.relative_to(root).as_posix()
            text = page.read_text()
            title = re.search(r'^title:\s*(.+)$', text, re.M).group(1).strip('"\'')
            exists = subprocess.run(['git', 'cat-file', '-e', 'HEAD:' + path], cwd=root,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            old_md = path.removesuffix('x') if path.endswith('.mdx') else None
            migrated = not exists and old_md and subprocess.run(
                ['git', 'cat-file', '-e', 'HEAD:' + old_md], cwd=root,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            change = ('首页重写' if page.name == 'index.md' else
                      '格式迁移并扩写' if migrated else '扩写现有路径' if exists else '新建独立教程')
            inventory.append({'locale': locale, 'path': path, 'title': title, 'change': change})
            for block in re.findall(r'<GuideSteps\b[\s\S]*?/>', text):
                frames = re.findall(r"['\"]?src['\"]?\s*:\s*['\"]([^'\"]+)", block)
                assert frames, path
                sequences.append(tuple(frame.replace('/images/guides/en/', '/images/guides/') for frame in frames))
            embeds += len(re.findall(r'<(?:GuideSteps|GuideRecordingDemo|ArrowDemo)\b', text))
            modes.update(re.findall(r'<GuideRecordingDemo\s+mode=["\']([^"\']+)', text))
            arrow_demo = arrow_demo or bool(re.search(r'<ArrowDemo\b', text))
    assets = sorted(p for p in (root / 'docs/public/images/guides').rglob('*')
                    if p.suffix in ('.svg', '.png', '.webp'))
    complete = evaluation['pending_operations'] == 0 and not evaluation['global_gaps']
    report = {
        'status': 'complete_by_user_requested_source_analysis' if complete else 'partial_source_analysis',
        'validation_mode': 'source_analysis', 'authority': policy['instruction'],
        'confirmed_operations': evaluation['confirmed_operations'],
        'completed_operations': evaluation['complete_operations'],
        'incomplete_operations': evaluation['pending_operations'],
        'excluded_candidates': evaluation['excluded_candidates'],
        'pages': len(inventory), 'pages_by_locale': dict(Counter(x['locale'] for x in inventory)),
        'tutorials_per_locale': len([x for x in inventory if x['locale'] == 'zh']) - 1,
        'page_changes_against_git_head': dict(Counter(x['change'] for x in inventory)),
        'page_inventory': inventory,
        'images': len(assets), 'image_types': dict(Counter(x.suffix for x in assets)),
        'svg_per_locale': sum(p.suffix == '.svg' and p.parent.name != 'en' for p in assets),
        'distinct_controlled_demonstrations': len(set(sequences)) + len(modes) + int(arrow_demo),
        'demonstration_embeds': embeds,
        'demonstration_count_evidence': 'Current128 Markdown/MDX pages; normalize localized frame paths before deduplicating sequences, plus unique component modes.',
        'demonstration_count_limit': 'Distinct modes/sequences, not188 newly recorded native runs; current source bindings and512 layout observations retained.',
        'source_commit': evaluation['source_commit'], 'source_audits': evaluation['audits'],
        'code_evaluation': 'artifacts/guide-code-validation-evaluation.json',
        'asset_review': manifest['asset_review'], 'website_review': manifest['website_review'],
        'website': website['checks'], 'historical_native': {
            'scope_rows': len(scopes), 'criterion_rows': len(criteria),
            'strict_complete_operations': runtime['strict_complete'],
            'stored_pass_criteria': sum(x.get('Result') == 'pass' for x in criteria),
            'complete_platform_scopes': sum(len(x['accepted_scopes']) for x in runtime['items']),
            'new_native_passes': 0, 'ledger_sha256': history,
            'is_current_completion_gate': False,
        },
        'public_copy': 'Task-oriented bilingual tutorials; no applicability-version labels or research/acceptance-progress remarks.',
        'product_changes': False, 'published_or_deployed': False,
        'page_tree': 'artifacts/guide-page-tree.md',
    }
    (art / 'guide-delivery.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', '<br>')

    def table(headers, data):
        return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |']
                         + ['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in data])

    pending = [x for x in evaluation['items'] if not x['complete'] and not x['excluded']]
    with (art / 'guide-pending.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['Feature ID', 'Specific gap', 'Blocker', 'Next action'])
        writer.writeheader()
        for item in pending:
            writer.writerow({'Feature ID': item['feature_id'], 'Specific gap': '; '.join(item['gaps']),
                             'Blocker': '代码/内容/素材或网站证据待补', 'Next action': '修正具体缺口后重审当前文件'})
    coverage = '# Snow Shot 手册覆盖清单\n\n'
    coverage += f"按照用户要求以代码分析验证产品行为：确认操作 **{report['confirmed_operations']}** 项，完成 **{report['completed_operations']}** 项，未完成 **{report['incomplete_operations']}** 项。IMG-040 为未发布候选，不计入确认操作。\n\n"
    coverage += '每项验收核对普通 UI 入口、事件/命令、处理、可见结果、重要选项与限制，以及当前双语教程、教学素材和网站检查。固定源码证据不冒充实机运行。原生历史账本原样保留，已退出当前完成门槛。\n\n'
    coverage += '详见 [交付报告](guide-delivery.md)、[代码分析明细](guide-code-validation-evaluation.json)、[页面树](guide-page-tree.md)及 [素材清单](guide-assets.csv)。\n\n'
    coverage += table(list(rows[0]), [[row[key] for key in rows[0]] for row in rows]) + '\n'
    (art / 'guide-coverage.md').write_text(coverage)
    delivery = '# Snow Shot 中英文手册交付报告\n\n'
    delivery += ('手册已完成，产品行为按用户指定的代码分析方式验收。\n\n' if complete else '当前仍有具体未完成项，见待办清单。\n\n')
    delivery += f"- 确认操作：{report['confirmed_operations']}；完成：{report['completed_operations']}；未完成：{report['incomplete_operations']}。另有1项未发布候选 IMG-040，未写成可用功能。\n"
    delivery += f"- 页面：中文63篇独立教程及1首页，英文完整对等，共{len(inventory)}页；侧栏、目录、相关任务和语言切换已接入。\n"
    delivery += f"- 教学图片：{len(assets)}个文件，其中{report['svg_per_locale']}组中英文SVG各一份、{report['image_types'].get('.webp', 0)}张共享WebP；{report['distinct_controlled_demonstrations']}种受控分镜/演示，共{embeds}处嵌入。重建图示在页面标明教学示意。\n"
    delivery += '- 公开教程已移除版本适用说明和研究过程备注；保留完成任务必需的平台、版本类型、权限及服务条件。\n\n'
    delivery += '## 验证结果\n\n'
    delivery += table(['检查', '结果'], [[k, v] for k, v in website['checks'].items()]) + '\n\n'
    delivery += '代码审核分四组并行完成，并由其他审核者复核冻结文件；每项保存当前中英文页面摘要和固定源码行号。外部桶读取权限、设备输出等不由源码保证，教程按真实条件指导用户核对结果。\n\n'
    delivery += '历史原生验证数据保留独立归属，本轮新增实机通过数为0；当前完成结论依据用户要求的代码分析。没有修改产品行为、提交或部署网站。\n\n'
    delivery += '## 实际页面与处理方式\n\n以下“新建/扩写/迁移”以当前 Git HEAD 为比较基线；从产品旧指南拆解扩展的组织记录另见[页面树](guide-page-tree.md)。\n\n'
    delivery += table(['语言', '教程', '实际文件', '处理方式'], [[x['locale'], x['title'], '../' + x['path'], x['change']] for x in inventory]) + '\n\n'
    delivery += '## 待完成项\n\n' + ('无确认操作遗留缺口。\n' if not pending else table(['Feature ID', '具体缺口', '下一步'], [[x['feature_id'], '; '.join(x['gaps']), '修正后重审'] for x in pending]))
    delivery += '\n完整操作、证据链及素材归属见[覆盖清单](guide-coverage.md)、[代码审核](guide-code-validation-evaluation.json)和[素材清单](guide-assets.csv)。\n'
    (art / 'guide-delivery.md').write_text(delivery)
    (art / 'guide-validation.md').write_text('# 手册验证记录\n\n产品验证方式：代码分析；依据用户指令“不要实机验证了，从代码分析验证”。\n\n' + table(['检查', '结果'], [[k, v] for k, v in website['checks'].items()]) + '\n\n当前输入绑定、历史检查继承范围与局限见[网站检查证据](guide-source-website-review-20261110i.json)。各项代码链与独立复核摘要见[代码分析验收](guide-code-validation-evaluation.json)。\n')
    print(json.dumps({key: report[key] for key in ('status', 'confirmed_operations', 'completed_operations', 'incomplete_operations', 'pages', 'images')}, ensure_ascii=False))
