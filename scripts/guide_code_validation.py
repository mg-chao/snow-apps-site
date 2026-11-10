"""Evaluate explicitly reviewed source chains without changing runtime evidence."""

import hashlib
import json
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_mode(root):
    policy = root / 'artifacts/guide-validation-policy.json'
    return policy.is_file() and json.loads(policy.read_text()).get('mode') == 'source_analysis'


def item_gaps(root, row, item, source_hashes):
    """Fail closed on missing, stale, unsupported, or unreviewed per-operation proof."""
    gaps = list(item.get('gaps', []))
    if item.get('code_result') != 'source_pass':
        gaps.append('代码链尚未通过审核')
    zh = row['Documentation path and section'].partition('#')[0]
    for locale, expected in (('zh', zh), ('en', zh.replace('/zh/', '/en/'))):
        path = item.get(locale + '_path', '')
        if path != expected or not (root / path).is_file():
            gaps.append(locale + ' 教程路径缺失或不匹配')
        elif digest(root / path) != item.get(locale + '_sha256'):
            gaps.append(locale + ' 教程已变更，需重新审核')
    for key in ('entry', 'event', 'processing', 'result', 'options_and_limits'):
        value = item.get('chain', {}).get(key)
        if not isinstance(value, str) or not value.strip():
            gaps.append('缺少代码链：' + key)
    references = item.get('source_refs', [])
    if not references:
        gaps.append('缺少固定源码引用')
    references = sorted(set(references + item.get('gate_refs', [])))
    for reference in references:
        match = re.fullmatch(r'(.+)#L(\d+)(?:-L?(\d+))?', reference)
        if not match:
            gaps.append('源码引用没有有效行号：' + reference)
            continue
        path = root / match[1]
        if not path.is_file() or match[1] not in source_hashes:
            gaps.append('源码快照未绑定：' + match[1])
            continue
        if digest(path) != source_hashes[match[1]]:
            gaps.append('源码快照已变更：' + match[1])
            continue
        first, last = int(match[2]), int(match[3] or match[2])
        if not 1 <= first <= last <= len(path.read_text().splitlines()):
            gaps.append('源码行号超出快照：' + reference)
    return sorted(set(gaps))


def evaluate_all(root, rows, anchor_issues, asset_gaps):
    art = root / 'artifacts'
    manifest_path = art / 'guide-code-validation-inputs.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    global_gaps = []
    if manifest.get('source_commit') != 'f02f50e5c6b132335247079398944b6fc9f7e6d6':
        global_gaps.append('固定研究源码提交不匹配')
    items = {}
    audit_bindings = []
    for audit in manifest.get('audits', []):
        path = root / audit['path']
        if not path.is_file() or digest(path) != audit['sha256']:
            global_gaps.append('代码审核文件缺失或已变更：' + audit['path'])
            continue
        data = json.loads(path.read_text())
        audit_items = data.get('items', [])
        peer = audit.get('peer_review', {})
        peer_path = root / peer.get('path', '')
        if not peer_path.is_file() or digest(peer_path) != peer.get('sha256'):
            global_gaps.append('独立复核文件缺失或已变更：' + audit['path'])
        else:
            review = json.loads(peer_path.read_text())
            if review.get('proposal_sha256') != audit['sha256'] or review.get('result') != 'pass' or review.get('gaps'):
                global_gaps.append('独立复核尚未通过：' + audit['path'])
            expected_ids = {item['feature_id'] for item in audit_items}
            if set(review.get('feature_ids', [])) != expected_ids:
                global_gaps.append('独立复核未覆盖本组全部操作：' + audit['path'])
        for item in audit_items:
            fid = item['feature_id']
            if fid in items:
                global_gaps.append('重复代码审核：' + fid)
            items[fid] = item
        audit_bindings.append({'path': audit['path'], 'sha256': audit['sha256'], 'rows': len(audit_items)})
    if set(items) != {row['Feature ID'] for row in rows}:
        global_gaps.append('代码审核未与完整覆盖清单对齐')

    checked = {}
    for key in ('asset_review', 'website_review', 'source_verification'):
        binding = manifest.get(key, {})
        path = root / binding.get('path', '')
        if not path.is_file() or digest(path) != binding.get('sha256'):
            global_gaps.append(key + ' 缺失或已变更')
        else:
            checked[key] = json.loads(path.read_text())
    assets = {x['feature_id']: x for x in checked.get('asset_review', {}).get('items', [])}
    source_check = checked.get('source_verification', {})
    if source_check.get('result') != 'pass' or source_check.get('errors'):
        global_gaps.append('固定源码快照校验未通过')
    if source_check.get('source_hashes') != manifest.get('source_hashes'):
        global_gaps.append('源码校验未覆盖全部当前引用')
    website = checked.get('website_review', {})
    if website.get('result') != 'pass' or website.get('gaps'):
        global_gaps.append('当前网站检查未通过')
    for group in website.get('current_inputs', {}).values():
        for path, expected in group.items():
            if not (root / path).is_file() or digest(root / path) != expected:
                global_gaps.append('网站检查输入已变更：' + path)
    if not website.get('current_inputs'):
        global_gaps.append('网站检查未绑定当前页面、素材与渲染输入')

    results = []
    for row in rows:
        fid = row['Feature ID']
        item = items.get(fid, {})
        excluded = fid == 'IMG-040'
        if excluded:
            gaps = [] if item.get('code_result') == 'excluded' and item.get('reason') else ['未发布候选缺少排除理由']
        else:
            gaps = global_gaps + item_gaps(root, row, item, manifest.get('source_hashes', {}))
            gaps += [issue for issue in anchor_issues if issue.startswith(fid + ':')]
            asset = assets.get(fid, {})
            if asset.get('result') != 'complete' or not asset.get('rationale'):
                gaps.append('教学素材适用性尚未审核')
            for path, expected in asset.get('asset_hashes', {}).items():
                if not (root / path).is_file() or digest(root / path) != expected:
                    gaps.append('教学素材已变更：' + path)
            if not asset.get('asset_hashes'):
                gaps.append('缺少现有教学素材绑定')
            if fid in asset_gaps:
                gaps.append('存在未完成的专属教学素材')
        complete = not excluded and not gaps
        row['Acceptance status'] = ('不纳入：未发布候选；见内部研究记录' if excluded and not gaps else
                                    '已完成：代码分析验证、双语教程、教学素材与网站检查通过' if complete else
                                    '未完成：' + '；'.join(sorted(set(gaps))))
        if complete:
            row['Operational verification status'] = '代码分析验证通过；普通UI入口→事件/命令→处理→可见结果已核对；未新增实机通过记录'
        elif not excluded:
            row['Operational verification status'] = '代码分析验证未完成；见本项验收缺口；历史原生记录保留在独立账本'
        results.append({'feature_id': fid, 'complete': complete, 'excluded': excluded,
                        'validation_mode': 'source_analysis', 'gaps': sorted(set(gaps)),
                        'source_review': item})
    report = {'schema_version': 1, 'validation_mode': 'source_analysis',
              'authority': 'artifacts/guide-validation-policy.json',
              'source_commit': manifest.get('source_commit'), 'audits': audit_bindings,
              'input_manifest_sha256': digest(manifest_path) if manifest_path.is_file() else None,
              'confirmed_operations': sum(not x['excluded'] for x in results),
              'complete_operations': sum(x['complete'] for x in results),
              'pending_operations': sum(not x['excluded'] and not x['complete'] for x in results),
              'excluded_candidates': [x['feature_id'] for x in results if x['excluded']],
              'global_gaps': sorted(set(global_gaps)), 'new_native_passes': 0, 'items': results}
    (art / 'guide-code-validation-evaluation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report
