"""Summarize the final guide inventory and recorded validation without accepting operations."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import json
import re
from guide_code_validation import source_mode
from guide_source_report import render as render_source_report

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
REPORT_DATE = datetime.now(timezone(timedelta(hours=8))).date().isoformat()

if source_mode(ROOT):
    render_source_report(ROOT)
    raise SystemExit(0)


def csv_rows(name):
    with (ART / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def json_data(name):
    return json.loads((ART / name).read_text())


def optional_json_data(name):
    return json_data(name) if (ART / name).is_file() else None


def checked_browser_batch(name):
    data = json_data(name)
    assert not data.get("errors", []) and not data.get("consoleErrors", []), name
    assert all(frame["loaded"] for frame in data.get("frames", [])), name
    assert all(not item.get("overflow") and not item.get("badImages")
               and not item.get("literalImport") for item in data.get("layouts", [])), name
    summary = data.get("summary", {})
    if "layouts" in summary:
        assert summary["layouts"] == len(data.get("layouts", [])), name
    if "frames" in summary:
        assert summary["frames"] == len(data.get("frames", [])), name
    assert not summary.get("layoutErrors", 0) and not summary.get("frameErrors", 0), name
    return data


def snapshot_matches_current(reference):
    snapshot = json.loads((ROOT / reference).read_text())
    groups = [snapshot.get(name, {}) for name in ("pages", "support", "assets")] if "pages" in snapshot else [snapshot]
    return all((ROOT / path).is_file() and hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
               for group in groups for path, digest in group.items())


docs_by_locale = {
    locale: sorted(p for p in (ROOT / f"docs/{locale}/guides").rglob("*")
                   if p.suffix in (".md", ".mdx"))
    for locale in ("zh", "en")
}
docs = [page for pages in docs_by_locale.values() for page in pages]
page_counts = {locale: len(pages) for locale, pages in docs_by_locale.items()}
tutorial_counts = {locale: len(pages)-1 for locale, pages in docs_by_locale.items()}
zh_tasks = {p.relative_to(ROOT / "docs/zh/guides").with_suffix("").as_posix()
            for p in docs_by_locale["zh"]}
en_tasks = {p.relative_to(ROOT / "docs/en/guides").with_suffix("").as_posix()
            for p in docs_by_locale["en"]}
assert zh_tasks == en_tasks, {"missing_english": sorted(zh_tasks-en_tasks), "extra_english": sorted(en_tasks-zh_tasks)}
images = sorted(p for p in (ROOT / "docs/public/images/guides").rglob("*")
                if p.is_file() and p.suffix in (".svg", ".png", ".webp"))
svgs = [p for p in images if p.suffix == ".svg"]
source_svgs = [p for p in svgs if p.parent.name != "en"]
english_svgs = [p for p in svgs if p.parent.name == "en"]
assert {p.name for p in source_svgs} == {p.name for p in english_svgs}, "English SVG copies are incomplete"
pngs = [p for p in images if p.suffix == ".png"]
webps = [p for p in images if p.suffix == ".webp"]
bitmaps = pngs + webps
native_bitmap_stems = {
    "start-main-interface-macos", "img-editor-native-empty", "ann-arrow-native-edited",
    "ann-smart-erase-native-result",
    "ann-arrow-click-native-1", "ann-arrow-click-native-2", "ann-arrow-click-native-3",
    "ann-text-move-app-before", "ann-text-move-app-after",
    "img-editor-fit-view", "img-editor-actual-size",
    "rec-local-image-input", "rec-local-text-recognized", "rec-local-text-edited",
    "rec-local-txt-reopened",
    "set-shortcut-bindings", "set-shortcut-recording",
    "set-shortcut-confirm-candidate", "set-shortcut-cancel-reopened",
    "img-paste-split-file-icon", "img-paste-split-bitmap",
    "img-split-vertical-equal", "img-split-horizontal-equal", "img-split-grid-3x2",
}
native_bitmaps = [p for p in bitmaps if p.stem in native_bitmap_stems]
input_bitmap_stems = {
    "img-editor-original-input", "rec-practice-qr-text",
    "rec-practice-qr-url", "rec-practice-ean13",
}
input_bitmaps = [p for p in bitmaps if p.stem in input_bitmap_stems]
practice_input_bitmaps = [p for p in input_bitmaps if p.stem.startswith('rec-practice-')]
result_bitmaps = [p for p in bitmaps if p not in native_bitmaps and p not in input_bitmaps]
steps = []
recording_modes = set()
arrow_demo = False
embed_count = 0
embeds_by_locale = {"zh": 0, "en": 0}
for page in docs:
    content = page.read_text()
    locale = page.relative_to(ROOT / "docs").parts[0]
    page_embeds_before = embed_count
    for block in re.findall(r"<GuideSteps\b[\s\S]*?/>", content):
        frames = tuple(re.findall(r"['\"]?src['\"]?\s*:\s*['\"]([^'\"]+)", block))
        assert frames, page
        steps.append(tuple(frame.replace("/images/guides/en/", "/images/guides/") for frame in frames))
        embed_count += 1
    arrow_count = len(re.findall(r"<ArrowDemo\b", content))
    arrow_demo = arrow_demo or bool(arrow_count)
    embed_count += arrow_count
    for mode in re.findall(r'<GuideRecordingDemo\s+mode=[\'"]([^\'"]+)', content):
        recording_modes.add(mode)
        embed_count += 1
    embeds_by_locale[locale] += embed_count - page_embeds_before
demo_count = len(set(steps)) + len(recording_modes) + int(arrow_demo)
coverage = csv_rows("guide-coverage.csv")
released = [r for r in coverage if r["Feature ID"] != "IMG-040"]
accepted = [r for r in released if r["Acceptance status"].startswith(("已完成", "验收通过", "完成："))]
acceptance_evaluation = json_data("guide-acceptance-evaluation.json")
accepted_scopes = [
    {"Feature ID": item["Feature ID"], "Scope ID": scope}
    for item in acceptance_evaluation["items"] for scope in item["accepted_scopes"]
]
ledger_scopes = csv_rows("guide-acceptance-scopes.csv")
ledger_evidence = csv_rows("guide-acceptance-evidence.csv")
ledger_scope_keys = {(item["Feature ID"], item["Scope ID"])
                     for item in ledger_scopes}
evaluated_scope_keys = {(item["Feature ID"], scope["Scope ID"])
                        for item in acceptance_evaluation["items"] for scope in item["scopes"]}
assert ledger_scope_keys == evaluated_scope_keys, "Acceptance output is stale: run check-guide-coverage.py first"
set005_scope_accepted = {"Feature ID": "SET-005", "Scope ID": "macos-arm64-full"} in accepted_scopes
shortcut_scope_detail = (
    "SET-005 的 macos-arm64-full 已由显式证据通过全部七项条件；其他六公开 scope 仍 pending"
    if set005_scope_accepted else
    "SET-005 的取消选项已有新增普通操作记录；当前显式评价尚未列为完整 scope，待输入/摘要复核，其他六公开 scope 仍 pending"
)
gaps = [r for r in csv_rows("annotation-asset-gaps.csv") if r["Status"].startswith("未完成")]
if gaps:
    asset_boundary = f"专属教学素材缺口清单仍有 {len(gaps)} 项待补齐"
    asset_gap_detail = (
        f"当前 {len(gaps)} 个明确素材缺口为 {', '.join(r['Feature ID'] for r in gaps)}。"
        "各项须按对应教学目的补充准确重建或实际结果，并如实标注制作方式；素材补齐后仍需分别完成操作验收。"
    )
else:
    asset_boundary = "专属教学素材缺口清单当前为 0 项"
    asset_gap_detail = (
        "当前清单内的专属教学素材已补齐，未完成素材缺口为 0 项。"
        "其中包含明确标注的源码教学重建、后台实际渲染与原生界面截图；"
        "这不表示所有用户操作、真实错误重试、发行包或跨平台验证已经通过。"
    )
release_editor = json_data("runtime-release-native-image-editor.json")
release_outputs = json_data("runtime-release-image-output-check.json")
assert release_outputs["editor_vs_pin"]["RGBA_equal"]
assert release_outputs["official-editor-final.png"]["sha256"] == release_outputs["official-pinned-result.png"]["sha256"]
release_ocr = json_data("runtime-release-native-ocr.json")
assert release_ocr["saved_text"]["text"] == "Start\nGoal"
smart_erase = json_data("runtime-smart-erase-result-check.json")
auto_filter = json_data("runtime-auto-filter-document-summary.json")
site = json_data("guide-site-check.json")
anchors = json_data("coverage-anchor-check.json")
current_native = optional_json_data("guide-runtime-preflight-current.json") or {}
current_native_detail = (
    "原生主窗口已恢复可读，已通过普通动作行和文件选择器载入自有图片；"
    "浮动裁剪/保存工具栏未出现在当前自动化截图与控件树中，正在等待入口选择协助；未新增操作通过。"
    if current_native.get("manual_entry_assistance_pending") else
    "当前普通界面预检仍报告锁屏，尚不能继续该批操作。"
    if current_native.get("state") == "locked" else
    "当前普通界面状态与操作结果见最新预检记录；不从可读取界面推断操作已通过。"
)
browser = json_data("qa-browser-all-tutorials.json")
final_qa = json_data("qa-browser-final-assets.json")
release_qa = json_data("qa-browser-release-ui-assets.json")
zoom_qa = json_data("qa-browser-editor-zoom.json")
assert all(frame["loaded"] for frame in zoom_qa["playerChecks"])
assert all(not check["overflow"] for check in zoom_qa["layoutChecks"])
ocr_qa = json_data("qa-browser-local-ocr.json")
parallel_qa = json_data("qa-browser-parallel-review.json")
workflow_qa = json_data("qa-browser-workflow-followup-20261110.json")
search_guard_qa = json_data("qa-search-keyboard-guard-20261110.json")
focused_zoom_qa = json_data("qa-focused-step-zoom-20261110.json")
depth_qa_name = "qa-browser-depth-review-20261110.json"
depth_qa = checked_browser_batch(depth_qa_name)
depth_integration = json_data("depth-review-integration-20261110.json")
depth_files = [item for group in depth_integration["groups"] for item in group["files"]]
assert depth_integration["files_total"] == len(depth_files)
assert all(group["status"] == "applied" for group in depth_integration["groups"])
formula_qa = json_data("qa-formula-edit-review-20261110.json")
assert not formula_qa["findings"] and all(item["visually_viewed"] for item in formula_qa["assets"])
formula_asset_count = len(formula_qa["assets"])
split_direction_count = sum(path.name == "img-split-directions.svg" for path in svgs)
split_native = json_data("runtime-release-native-split-20261110.json")
split_pixels = json_data("runtime-split-output-pixel-check-20261110.json")
split_assets = json_data("qa-native-split-conversion-20261110.json")
assert split_pixels["all_expected_pixels_preserved"]
assert all(item["RGBA_equal_to_source_crop"] for item in split_pixels["files"])
assert all(item["decoded_RGBA_equal"] for item in split_assets["conversions"])
shortcut_options = json_data("runtime-shortcut-cancel-options-20261110.json")
assert not shortcut_options["finalObserved"]["newBindingSaved"]
final_delta_name = "qa-browser-depth-final-delta-20261110.json"
final_delta_qa = checked_browser_batch(final_delta_name) if (ART / final_delta_name).is_file() else None
if final_delta_qa:
    assert final_delta_qa.get("sourceSnapshot"), "Final delta QA must name its source snapshot"
final_delta_current = bool(final_delta_qa and snapshot_matches_current(final_delta_qa["sourceSnapshot"]))
final_delta_detail = (
    f"此前独立增量按其当时快照核对 {len(final_delta_qa.get('layouts', []))} 个布局、"
    f"{len(final_delta_qa.get('frames', []))} 帧；见 [{final_delta_name}]({final_delta_name})"
    if final_delta_qa else
    "后续剪贴板与设置教学增量尚待独立的二次构建/浏览器记录；不将深审批次的历史 QA 扩展到新改动"
)
next_batch_name = next((name for name in (
    "completion-scope-batch-summary-20261110d.json",
    "input-state-batch-summary-20261110c.json",
    "next-depth-batch-summary-20261110b.json",
) if (ART / name).is_file()), "next-depth-batch-summary-20261110b.json")
next_batch = optional_json_data(next_batch_name)
next_qa = checked_browser_batch(next_batch["browser_qa"]) if next_batch else None
if next_qa:
    assert snapshot_matches_current(next_qa["sourceSnapshot"]), "Current review QA snapshot is stale"
    assert not next_batch["native_passes_added"], "Report must explicitly review any new native acceptance"
next_batch_detail = (
    f"{next_batch.get('label', '截图、识别、翻译与贴图深审')}按独立快照整合 {next_batch['integrated_file_changes']} 次文件变更，"
    + (f"补审 {next_batch['existing_operations_scope_reviewed']} 项已有操作的完整公开平台范围、"
       f"声明 {next_batch['new_declared_scopes']} 个待验收范围；"
       if next_batch.get('existing_operations_scope_reviewed') else
       f"新增 {len(next_batch['new_operation_ids'])} 条查重后的操作；")
    + f"新增 {next_batch['new_asset_files']} 个实际素材文件；"
    f"{len(next_qa['layouts'])} 个布局与 {len(next_qa['frames'])} 帧已逐项检查，0错误。"
    f"公开文案与图示不含无关版本或制作进度备注；操作示意与真实截图保持区分。"
    f"本批没有新增原生操作验收。见 [{next_batch_name}]({next_batch_name}) / "
    f"[{next_batch['browser_qa']}]({next_batch['browser_qa']})"
    if next_batch else "最新增量仍待最终构建及浏览器验证。"
)
next_integration = next_batch.get("integration", "next-depth-integration-20261110b.json") if next_batch else "next-depth-integration-20261110b.json"
format_evidence = next_batch.get("format_evidence", "validation-format-next-depth-20261110b.json") if next_batch else "validation-format-next-depth-20261110b.json"
current_layout_name = "qa-browser-current-layout-coverage-20261110d.json"
current_layout_qa = checked_browser_batch(current_layout_name) if (ART / current_layout_name).is_file() else None
if current_layout_qa:
    assert snapshot_matches_current(current_layout_qa["sourceSnapshot"]), "Current all-page layout evidence is stale"
current_layout_detail = (
    f"{current_layout_qa['summary']['pages']} 页、{len(current_layout_qa['layouts'])} 组桌面/手机明暗布局；"
    "按文件 SHA 保留未变页面的既有实测记录，变更页另作增量复核，0 错误；历史记录保留来源。"
    if current_layout_qa else "尚无覆盖当前全部页面的统一布局证据。"
)
split_paste_name = "runtime-release-native-split-paste-20261110.json"
split_paste_pixels_name = "runtime-split-paste-output-pixel-check-20261110.json"
split_paste = optional_json_data(split_paste_name)
split_paste_pixels = optional_json_data(split_paste_pixels_name)
assert bool(split_paste) == bool(split_paste_pixels), "Keep split-paste operation and pixel evidence paired"
if split_paste_pixels:
    assert split_paste_pixels["horizontal_concatenation_RGBA_equal"]
split_paste_detail = (
    f"IMG-050 本次 Finder 文件列表复制得到 1024×1024 文件图标，file-URL 路径没有通过；"
    f"改用 Preview 复制实际 {split_paste_pixels['source_size'][0]}×{split_paste_pixels['source_size'][1]} 像素后，"
    f"空窗粘贴与替换确认成功，取消替换保留图像及 count3。导出 {len(split_paste_pixels['files'])} 片并横向拼回后 RGBA 完全一致；"
    f"该成功仅归实际位图路径，不证明文件 URL、多文件、Smart 优化或其他平台。见 [{split_paste_name}]({split_paste_name}) / "
    f"[{split_paste_pixels_name}]({split_paste_pixels_name})。"
    if split_paste_pixels else "本批没有新增剪贴板位图粘贴的独立运行记录。"
)
assert len(workflow_qa["frames"]) == 60 and all(frame["loaded"] for frame in workflow_qa["frames"])
assert workflow_qa["summary"]["layoutErrorsAfterRetry"] == 0
assert len(workflow_qa["layouts"]) == 68
assert len(workflow_qa["finalBuildConfirmation"]["shortcutFrames"]) == 8
assert not search_guard_qa["errors"] and not focused_zoom_qa["errors"]
assert len(focused_zoom_qa["checks"]) == 4 and all(
    check["loaded"] and not check["overlay"] and check["scrollTop"] == 0
    for check in focused_zoom_qa["checks"]
)
assert focused_zoom_qa["originalLinkCheck"]["images"][0]["loaded"]
assert len(parallel_qa["frames"]) == 38 and all(frame["loaded"] for frame in parallel_qa["frames"])
assert len(parallel_qa["layouts"]) == 48 and all(not item["overflow"] and not item["badImages"] for item in parallel_qa["layouts"])
assert len(parallel_qa["focusChecks"]) == 14 and all(item["scrollTop"] == 0 and item["overflow"] == "clip" for item in parallel_qa["focusChecks"])
build_status = json_data("validation-build-status.json")
standard_build_passed = build_status["standard_exit_code"] == 0
if standard_build_passed:
    assert snapshot_matches_current(build_status["source_snapshot"]), "Build source snapshot is stale"
if standard_build_passed:
    confirmation = parallel_qa["standardBuildConfirmation"]
    assert confirmation["standardBuildPassed"] and confirmation["defaultConfig"]
    assert len(confirmation["checks"]) == 4 and all(not item["overflow"] and not item["badImages"] for item in confirmation["checks"])
build_detail = "退出 0；正式输出生成" if standard_build_passed else "未通过；并行博客的两处链接和两张图尚未产出，原失败日志保留"
checks_detail = "相关共享组件 format、lint、build 通过；MD/MDX 不在 Biome 格式化支持范围" if standard_build_passed else "相关组件 format、lint 通过；标准 build 未通过；诊断构建另记"
assert len(ocr_qa["frames"]) == 8 and all(frame["loaded"] for frame in ocr_qa["frames"])
assert all(frame["scrollTop"] == 0 for frame in ocr_qa["frames"] if frame["focus"])
assert all(not check["overflow"] and not check["badImages"] for check in ocr_qa["layouts"])
final_players = [p for page in final_qa["desktop"] for p in page["players"]]
final_frames = [frame for player in final_players for frame in player["frames"]]
assert all(frame["loaded"] for frame in final_frames)
ops = csv_rows("guide-operational-checks.csv")
depth_added_ids = (json_data("image-new-operations-integration-20261110.json")["new_ids"]
                   + json_data("settings-new-operations-integration-20261110.json")["new_ids"])
assert len(depth_added_ids) == len(set(depth_added_ids))
assert set(depth_added_ids) <= {row["Feature ID"] for row in coverage}
depth_asset_registries = [
    "assets-formula-edit.csv", "assets-image-processing-depth-review-20261110.csv",
    "assets-native-split-20261110.csv", "assets-original-preview-20261110.csv",
    "assets-paste-teaching-20261110.csv", "assets-settings-operations-20261110.csv",
    "assets-canvas-navigation-20261110.csv",
]
depth_registered_assets = {row["Asset"] for name in depth_asset_registries for row in csv_rows(name)}
release_partial_ids = [r["Feature ID"] for r in ops
                       if "正式发行原生UI：" in r["Verification result"]
                       or "正式发行普通UI" in r["Verification result"]
                       or "runtime-release-native-shortcut-cancel.json" in r["Verification result"]]
tests = (ART / "validation-tests.log").read_text()
pass_count = int(re.search(r"(\d+) pass", tests).group(1))
fail_count = int(re.search(r"(\d+) fail", tests).group(1))
lint_log = (ART / "validation-lint.log").read_text()
lint_warning_match = re.search(r"Found (\d+) warnings?", lint_log)
lint_warning_count = int(lint_warning_match.group(1)) if lint_warning_match else 0
lint_detail = f"退出 0；{lint_warning_count} 条警告，另有 Biome 配置弃用提示"
if "exceeds the configured maximum" in lint_log:
    lint_detail += "；包含生成验收 JSON 超过 1 MiB 的扫描跳过提示，该 JSON 另由 Python 解析与 schema 校验"
assert not site["errors"] and not anchors["errors"] and fail_count == 0
assert site["pages"] == len(docs), "Site check is stale: rebuild and check all current bilingual pages first"
assert site["svg_files"] == len(svgs) and site["webp_files"] == len(webps) and site["png_files"] == len(pngs), "Asset scanner is stale"
assert site.get("pages_by_locale") == page_counts, "Site check lacks current per-locale page evidence"
assert site["standalone_tutorials"] == sum(tutorial_counts.values()), "Tutorial count does not match current source"
mobile_by_locale = {locale: sum(record.get("path", "").startswith("/zh/") == (locale == "zh")
                                for record in browser) for locale in ("zh", "en")}
page_inventory = []
for locale, pages in docs_by_locale.items():
    for page in pages:
        title = re.search(r"^title:\s*(.+)$", page.read_text(), re.M).group(1).strip("\"'")
        page_inventory.append({"locale": locale, "title": title,
                               "path": page.relative_to(ROOT).as_posix(),
                               "kind": "hub" if page.stem == "index" else "tutorial"})
metrics = {
    "date": REPORT_DATE, "status": "partial",
    "new_tutorials": sum(tutorial_counts.values()), "rewritten_hubs": len(docs_by_locale),
    "pages": len(docs), "pages_by_locale": page_counts,
    "tutorials_by_locale": tutorial_counts, "matched_task_pages_per_locale": len(zh_tasks),
    "page_inventory": page_inventory,
    "coverage_rows": len(coverage), "released_check_rows": len(released),
    "strictly_accepted_released_rows": len(accepted),
    "released_rows_pending_strict_acceptance": len(released)-len(accepted),
    "strictly_accepted_platform_scopes": accepted_scopes,
    "declared_scope_rows": len(ledger_scopes),
    "source_scope_rows_reviewed": sum(row["Scope review status"] == "reviewed" for row in ledger_scopes),
    "source_scope_rows_pending_review": sum(row["Scope review status"] == "pending" for row in ledger_scopes),
    "criterion_rows": len(ledger_evidence),
    "stored_pass_criteria": sum(row["Result"] == "pass" for row in ledger_evidence),
    "unreleased_candidate_ids": ["IMG-040"],
    "svg_images": len(svgs), "source_instructional_svg_images": len(source_svgs),
    "english_localized_svg_images": len(english_svgs), "shared_png_images": len(pngs),
    "png_images": len(pngs),
    "shared_webp_images": len(webps), "webp_images": len(webps),
    "image_bytes": sum(p.stat().st_size for p in images if p.is_file()),
    "distinct_controlled_demonstrations": demo_count,
    "demonstration_embeds": embed_count, "demonstration_embeds_by_locale": embeds_by_locale,
    "specific_asset_gaps": [r["Feature ID"] for r in gaps],
    "partial_runtime_evidence_ids": [r["Feature ID"] for r in ops],
    "release_native_partial_ids": release_partial_ids,
    "official_release_identity": release_editor["identity_evidence"],
    "official_native_ocr_evidence": "artifacts/runtime-release-native-ocr.json",
    "native_screenshot_bitmaps": len(native_bitmaps),
    "application_result_bitmaps": len(result_bitmaps),
    "input_bitmaps": len(input_bitmaps),
    "practice_input_bitmaps": len(practice_input_bitmaps),
    "mobile_pages_inspected": len(browser), "mobile_inspections_by_locale": mobile_by_locale, "related_tests_passed": pass_count,
    "related_tests_failed": fail_count, "site_check": site,
    "build_status": build_status,
    "parallel_review_browser": "artifacts/qa-browser-parallel-review.json",
    "workflow_followup_browser": "artifacts/qa-browser-workflow-followup-20261110.json",
    "shortcut_native_cancellation": "artifacts/runtime-release-native-shortcut-cancel.json",
    "search_keyboard_fix_browser": "artifacts/qa-search-keyboard-guard-20261110.json",
    "focused_step_zoom_fix_browser": "artifacts/qa-focused-step-zoom-20261110.json",
    "depth_review_integration": "artifacts/depth-review-integration-20261110.json",
    "depth_integrated_files": len(depth_files),
    "depth_batch_browser": "artifacts/" + depth_qa_name,
    "depth_batch_browser_phase": "Historical validated batch; later changes require final_delta_browser",
    "depth_batch_browser_summary": depth_qa["summary"],
    "depth_batch_source_snapshot": depth_qa["sourceSnapshot"],
    "depth_new_operation_ids": depth_added_ids,
    "depth_reviewed_asset_files": len(depth_registered_assets),
    "depth_asset_registries": depth_asset_registries,
    "depth_batch_snapshot_matches_current_source": snapshot_matches_current(depth_qa["sourceSnapshot"]),
    "formula_editing_illustrations": formula_asset_count,
    "split_direction_illustrations": split_direction_count,
    "native_split_screenshot_bitmaps": len(split_assets["conversions"]),
    "native_split_export_PNG_evidence": len(split_pixels["files"]),
    "native_split_operation": "artifacts/runtime-release-native-split-20261110.json",
    "native_split_pixel_check": "artifacts/runtime-split-output-pixel-check-20261110.json",
    "shortcut_native_options": "artifacts/runtime-shortcut-cancel-options-20261110.json",
    "shortcut_cancel_mac_full_scope_accepted": set005_scope_accepted,
    "split_paste_native_evidence": "artifacts/" + split_paste_name if split_paste else None,
    "split_paste_pixel_check": "artifacts/" + split_paste_pixels_name if split_paste_pixels else None,
    "split_paste_file_URL_branch": split_paste_pixels["file_URL_clipboard_branch"] if split_paste_pixels else None,
    "final_delta_browser": "artifacts/" + final_delta_name if final_delta_qa else None,
    "final_delta_browser_status": ("recorded for its exact current snapshot" if final_delta_current
                                   else "historical snapshot only" if final_delta_qa else "pending"),
    "final_delta_browser_summary": final_delta_qa.get("summary", {}) if final_delta_qa else None,
    "latest_depth_batch": next_batch,
    "latest_depth_batch_browser_summary": next_qa.get("summary", {}) if next_qa else None,
    "current_all_page_layout_evidence": "artifacts/" + current_layout_name if current_layout_qa else None,
    "current_all_page_layout_summary": current_layout_qa.get("summary", {}) if current_layout_qa else None,
    "current_native_preflight": current_native,
}
(ART / "guide-delivery.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2)+"\n")

validation = f"""# 中英文手册验证记录

日期：{REPORT_DATE}，macOS arm64，Rspress 2.0.22，Bun 1.4.2。产品研究与运行副本的区别见 [研究记录](guide-research.md)。以下网站检查通过不代表产品操作已逐项验收。

| 检查 | 实际结果 | 证据 |
| --- | --- | --- |
| `bun run format -- package.json rspress.config.ts tests/search-keyboard.test.mjs theme/components/GuideSteps theme/components/GuideRecordingDemo.tsx` | 退出 0，检查 6 个相关文件、无修正；MD/MDX 不在 Biome 支持范围 | [本批 format]({format_evidence}) / [旧文档调用](validation-format.log) |
| `bun run lint` | {lint_detail} | [lint 日志](validation-lint.log) |
| `bun run build` | {build_detail} | [build 日志](validation-build.log) |
| 早期手册诊断构建 | 退出 0；当时只排除精确的 3 个博客引用（4 个物理缺目标），其他链接与图检查保留；不替代标准构建 | [诊断日志](validation-guide-diagnostic-build.log) / [本地配置](rspress-guide-diagnostic.config.ts) |
| `bun test tests/feature-demo.test.mjs tests/search-keyboard.test.mjs tests/locale-redirect.test.mjs tests/seo.test.mjs` | {pass_count} 通过，{fail_count} 失败；仅运行相关的四个测试文件，含真实依赖键盘处理器 | [测试日志](validation-tests.log) |
| 页面、侧栏、链接与资源 | {site['pages']} 页、{site['unique_assets_checked']} 个唯一资源、{site['unique_anchor_targets_checked']} 个锚点目标；0 错误 | [站点检查](guide-site-check.json) |
| 操作与章节映射 | {anchors['rows']} 个唯一 ID；0 缺失文件/章节锚点 | [覆盖映射](coverage-anchor-check.json) |
| SVG | {len(source_svgs)} 个原始图示 + {len(english_svgs)} 个英文文本副本，均为有效 XML | 站点检查与 [素材登记](guide-assets.csv) |
| 深审历史批次 | {len(depth_files)} 文件窄合入；{depth_qa["summary"]["layouts"]} 布局、{depth_qa["summary"]["frames"]} 帧0错误；含公式{formula_asset_count} SVG、方向{split_direction_count}图与{len(split_assets["conversions"])}张原生分割截图 | [批次网页QA](qa-browser-depth-review-20261110.json) / [静态复核](depth-batch-static-review-20261110.md) |
| 最终独立增量 | {final_delta_detail} | [当前构建](validation-build-status.json) |
| 最新并行深审增量 | {next_batch_detail} | [最新整合]({next_integration}) |
| 当前全部页面布局 | {current_layout_detail} | [当前布局证据]({current_layout_name}) |
| 当前原生界面状态 | {current_native_detail} | [当前预检](guide-runtime-preflight-current.json) |

已有 node:test 测试通过 Bun 的测试运行器执行，仅运行相关测试。没有修改产品代码，没有运行产品完整测试套件。

## 浏览器实际检查

- 正式预览：[中文手册](http://127.0.0.1:4174/zh/guides/index.html) · [English manual](http://127.0.0.1:4174/guides/index.html)。旧的 4173 开发预览已停止；保留 4174 供本地查看。
- 手机 390×844：实际记录中文 {mobile_by_locale["zh"]} 页、英文 {mobile_by_locale["en"]} 页；对应记录中的页面标题正常、图片无加载失败、没有 JSX/import 原样泄露，也没有整页横向溢出。详见 [逐页记录](qa-browser-all-tutorials.json)。
- 早期桌面 1440×1000：首页与箭头页在浅色/深色下目视检查。该历史批次另检查手机表格演示，并在当时恢复默认视口和浅色主题；本轮 1280×720 桌面检查另见后续记录。
- 先前英文补充检查：63 篇独立教程在手机浅色布局逐页通过；当时的 52 个步骤播放器共 159 帧经 Next/Reset 实际点击全部加载，6 个代表性英文页在手机深色下无整页溢出或坏图。英文搜索跳到箭头段落，中英文切换保持同一教程；手机目录可展开并进入颜色卡片教程。见 [英文逐页检查](qa-browser-english-tutorials.json)、[英文分镜](qa-browser-english-players.json)、[双语集成](qa-browser-bilingual-integration.json) 和 [英文字体与图示复核](qa-guide-english-svg-review.md)。
- 本次新增真实步骤与结果：重启正式预览后，文字移动的两帧播放器在两语页面实际点击 Next/Reset；输入/编辑结果两图均加载。{len(release_qa['mobileChecks'])} 条 390×844 浅色/深色检查无坏图或整页溢出，覆盖两语文字、编辑和箭头页；另核对桌面结果图、放大图片新窗口、同页语言切换及英文控件名称。见 [本次浏览器记录](qa-browser-release-ui-assets.json)。
- 观看缩放补充：Fit/100% 两帧在中文和英文各点击 Next/Reset，{len(zoom_qa['playerChecks'])} 条帧记录均实际加载；390×844 两语明暗布局及100%长说明无整页溢出，完整截图提供放大入口。见 [观看缩放浏览器记录](qa-browser-editor-zoom.json) 与 [原图无损转换核对](runtime-release-editor-view-assets.json)。
- 本地 OCR 教学：中英文各 4 帧经 Next/Reset 实际切换，共 {len(ocr_qa['frames'])} 条帧记录全部加载；手机两语明暗及桌面明暗检查无坏图/整页溢出，放大区域可读。修正 `overflow:hidden` 被自动滚动造成白屏，当前聚焦容器 `overflow:clip`、scrollTop=0；保留完整原图链接。另复核旧原生截图与 SVG 播放器的默认显示及 Next/Reset。新任务能经搜索跳到正确 `.html#识别已有图片并保存文字`，语言切换仍同任务。见 [本地 OCR 浏览器记录](qa-browser-local-ocr.json)。
- 并行审稿：标注 19 对、录屏与设置 9 对复核了两语结构与步骤，修正标注文字提交、修改已有对象前的工具选择、录屏动作行、配置导出确认、鼠标绑定及悬浮条说明；另补 Mini 图像编辑器隐藏识别按钮的入口。源码结论与公开文案审核不提升 Mini、裁剪或其他未操作的 UI 验收。
- 本轮手册诊断输出：24 个更新页面的手机明暗共 48 条布局记录无坏图/整页溢出；editor 两语 30 帧及 OCR 两语 8 帧经按钮切换/重置正常。新裁剪 14 帧放大左侧数值对照区，保留完整原图链接，容器 `overflow:clip`、scrollTop=0；同任务语言切换已查。详见 [并行审稿浏览器记录](qa-browser-parallel-review.json) 和 [14 张图示独立复核](qa-editor-crop-illustrations-review.md)。这不代表尚未补齐的博客资源已经通过。
- 随后博客缺目标落盘，并修复日期辅助函数漏导入；标准构建重新通过。重启预览后，对两语 editor/text 共 4 页复核标题、5/1 组播放器、2 个裁剪放大区、语言目标、坏图与溢出，均符合当前页面；早期诊断批次仍保留原构建身份，不改写成全部在标准输出重跑。原失败日志保存在 [构建状态](validation-build-status.json) 所列历史路径。
- 2026-11-10 三路审核合入 30 个文档修订、24 张裁剪 SVG 和 4 张快捷键原生截图。新的正式输出中，editor 两语 52 帧、快捷键两语 8 帧全部实际切换并重置，原图入口一致；34 页手机明暗共 68 条检查及两条主题时序复核没有坏图或整页溢出，另核英文精确选区/备份两页及 8 条桌面布局。两处 caption 与英文精度修正后的最终构建又复核两语快捷键 8 帧和四个页面。详见 [本轮网页记录](qa-browser-workflow-followup-20261110.json)。这些是当前批次检查；历史逐页检查仍保留原时间身份。
- 本轮发现并修复 Rspress SearchPanel 在搜索关闭/无结果时按 Enter 读取 undefined.link 的错误：维护 Bun 依赖补丁，仅增加 focused 和有效 suggestion 两项检查。7 项回归运行真实依赖处理器；未修复原文件的负向检查有 4 项失败。浏览器实际复核空搜索、无匹配、有效结果、关闭后回车、Command+K 与 Esc，控制台无新错误。另修复局部截图与全站 medium-zoom 的偏移冲突，四条两语原生/SVG 点击记录保持画面可见，完整 1800×1280 原图另页正常加载。见 [键盘复查](qa-search-keyboard-guard-20261110.json) 与 [局部图放大复查](qa-focused-step-zoom-20261110.json)。手机换行链接的包围盒中心落在空白处，自动中心点击未跳转；其键盘 Enter 与桌面点击已核对，不能将此自动定位现象归因为上述键盘异常。
- 深审历史批次：三路 source review 窄合入 {len(depth_files)} 文件，另增公式 {formula_asset_count} SVG、分割方向 {split_direction_count} 图和 {len(split_assets['conversions'])} 张原生分割截图；{depth_qa['summary']['layouts']} 个布局、{depth_qa['summary']['frames']} 帧均无错误，并检查公式同页语言切换/搜索与完整原图。证据只覆盖 [该批源快照](depth-build-inputs-20261110.json)，不借给后续 clipboard/settings 改动。见 [depth QA](qa-browser-depth-review-20261110.json)。
- {final_delta_detail}。
- {next_batch_detail}。
- 共享步骤播放器：检查上一步、下一步、重置和播放至末帧；箭头另检查类型、双端和路径，录屏两模式检查下一步/重置。见 [步骤演示](qa-browser-demo-checks.json)、[录屏演示](qa-browser-recording-checks.json) 与补充批次 [最终素材检查](qa-browser-final-assets.json)。
- 最终新增批次：{len(final_qa['desktop'])} 个更新页面、{len(final_players)} 组新播放器的 {len(final_frames)} 帧均通过普通按钮逐帧检查并加载；同批 {len(final_qa['mobileDark'])} 页在手机深色模式下无图片加载失败或整页溢出。专属图示另经过 [独立源码与渲染复核](qa-annotation-asset-review.md)，三处几何/标签问题已修正。
- 已有手机浏览器记录覆盖侧栏展开、颜色卡片页和导航展开。当前静态检查另核对中英文同任务页面的语言切换目标；不将早期中文浏览器记录扩大为所有英文页面已实查。
- 搜索“距离”得到 `.html` 正式地址；点击后及刷新后均保持正确教程，见 [搜索复核](qa-browser-search.json)。搜索摘要不含组件 JSX。
- 原首页 URL 与六个既有锚点保留，侧栏、页内目录、上一篇/下一篇及相关链接由构建检查覆盖。
- 减少动态效果：静态检查 prefers-reduced-motion 样式；演示默认不自动播放，分镜离散切换。没有声称已更改系统偏好完成全平台辅助功能认证。

## 产品实际操作的界限

普通原生 UI 与后台运行证据分别记录正式发行包和开发构建身份，不合并替代：

- 官方 macOS arm64 Full 已匹配 DMG SHA256、只读挂载并核对嵌入 revision，在独立数据目录启动。通过主窗口动作行→添加单张本地图像→箭头/矩形/文字创建→端点与矩形控制柄→文字移动→撤销/重做/选中删除→系统保存→固定到屏幕→贴图保存→重开结果，完成一条实际普通 UI 链。此批涉及 {len(release_partial_ids)} 个 ID 的局部成功或未完成尝试，均保留分支边界。输出 507×199 PNG，编辑器最终结果与贴图结果的 SHA256、RGBA 均一致。见 [正式包普通操作](runtime-release-native-image-editor.json)、[输出核对](runtime-release-image-output-check.json) 和 [逐项验收增量](acceptance-release-ui-review.md)。
- 同一正式包本地 OCR：从图片编辑器 Command+D 得到可编辑 Start/Target；人工将 Target 改为 Goal，Command+Z 与 Command+Shift+Z 撤销/重做；局部与全文复制到自有 TextEdit 文稿均匹配。TXT 保存取消保留结果；再次保存得到 {release_ocr['saved_text']['bytes']} 字节 UTF-8 文本，在 TextEdit 普通 Open 重开后仍为 Start/Goal 两行。实际通过标题栏鼠标移焦后 Command+S 保存，未点击浮动 Save 按钮；不将此路径冒充正文按钮操作已完成。截图宿主的原图显示、格式/标点/重置、图像输出与跨平台仍待测。见 [本地 OCR 原生记录](runtime-release-native-ocr.json)、[来源链](research-release-editor-ocr-ui.md)、[新增两项操作与局部验收](acceptance-release-ocr-ui-review.md)。
- 快捷键取消：原有⌃1 → Tab草稿 → 行末勾 → 外层Cancel保留原值；随后新增等待时Cancel、Esc/Enter候选后Cancel或标题关闭、删除/添加草稿后取消，主列表及重开均保留原配置，未保存新绑定。两候选进程实际二进制SHA与映射inode匹配正式包，短revision澄清另存。{shortcut_scope_detail}，不提升SET-004或“备用键已保存”。早期锁屏中断后已继续完成上述普通操作，历史中断单独保留。见 [最初步骤](runtime-release-native-shortcut-cancel.json)、[取消选项补测](runtime-shortcut-cancel-options-20261110.json)、[身份澄清](runtime-shortcut-options-revision-clarification-20261110.json) 与 [独立复核](acceptance-shortcut-options-review-20261110.json)。
- 正式包原生分割：同一300×200输入实际选择Vertical/Horizontal Equal2与Grid2行3列、overlap0。{len(split_pixels['files'])} 个导出PNG分别与对应source crop完全相等：左右两片150×200、上下两片300×100、6格100×100且按行排列；未成功的AX-only尝试单列排除，不冒充Equal。图像、输出、保存取消与窗口关闭有实际记录，Smart/Precise/非零重叠/手动线/PDF/其他平台不继承。见 [原生操作](runtime-release-native-split-20261110.json)、[像素核对](runtime-split-output-pixel-check-20261110.json) 和 [独立范围复核](acceptance-native-split-review-20261110.json)。
- {split_paste_detail}
- 保存窗口类型可通过普通设置在系统/Snow Shot 之间选择；本次选 Snow Shot 后发起保存只显示“正在导出…”，未出现可见表单或取得文件。已关闭无修改窗口并恢复系统方式。这是未完成尝试，不推断所有平台均失败。见 [设置选择与恢复](runtime-release-save-dialog-choice.json)。
- 继续验证时，原隔离进程已退出，通过原 launcher 重启。绑定窗口能显示已有图片与 OCR 文字，但完整桌面截图显示多个 Snow Shot 窗口重叠，物理前景和绑定表面的对应关系不足；本次不提升任何键鼠操作、Save 按钮或裁剪通过。内部截图不作为公开素材。见 [继续验证记录](runtime-release-native-continuation-20261109.json)。

- 原有普通操作：主窗口/截图进入退出、箭头拖动创建、V 点选/曲线中点、逐点创建、Command+Z/Command+Y、Backspace。见 [原生箭头记录](runtime-native-arrow-checks.json)。
- 智能擦除：类型与矩形范围通过 MCP 设置，在可见画布中完成补全；随后通过普通 Command+S、“保存截图”对话框和“保存”按钮输出 {smart_erase['size'][0]}×{smart_erase['size'][1]} PNG，并重新打开检查。虚构简单背景中右侧文字被移除、旁边蓝条保留；目标范围外改变 {smart_erase['changed_pixels_outside_target']} 个像素。此证据覆盖可见处理与原生保存，没有验证普通菜单选择类型或鼠标创建范围。见 [处理状态](runtime-visible-filter-checks.json) 与 [保存结果核对](runtime-smart-erase-result-check.json)。
- 早期开发构建普通图像打开记录仍保留：搜索定位动作行、点击空编辑器、添加单张图片成功。后续编辑与输出由上述正式包独立验证；拖入、多文件和文件管理器已有选择仍未验证。见 [早期普通入口记录](runtime-native-image-editor.json)。
- ANN-065 自动滤镜：后台文档自动检测任务完成，返回 {auto_filter['job']['result']['regions']} 个检测区域总数，随后按文本、框内文本两类填充 85% 马赛克并导出 {auto_filter['output_size'][0]}×{auto_filter['output_size'][1]} 图片，实际改变 {auto_filter['changed_pixels']} 个像素。总数不表示文本区域数量，输出还出现头像形状误分类；此证据未验证普通“填充区域”菜单选择、鼠标命中或实际错误重试。见 [后台任务与输出核对](runtime-auto-filter-document-summary.json) 和 [完整请求记录](runtime-auto-filter-document-checks.json)。
- 其他后台 MCP 证据：独立背景绘图、矩形区域、渲染对照，以及本地 OCR/校正/文本导出。具体覆盖见 [逐 ID 验证](guide-operational-checks.csv) 和研究笔记。

普通入口、后台参数补丁、可见宿主处理和原生保存分别核验，没有把一种证据扩展为其他控件已经操作。正式发行包记录仅归于实际 macOS arm64 Full，不扩展到 Windows、Mini、Intel Mac、外部服务、声音/摄像头或其他工具的全部操作。当前严格验收完成 {len(accepted)} 项，发布操作仍有 {len(released)-len(accepted)} 项待逐项闭环，具体下一步均在 [guide-pending.csv](guide-pending.csv)。

## 两次覆盖审计

产品→文档：对当前已登记的 {len(coverage)} 条核查记录，检查工具条、分组、菜单、编辑状态、结果窗口、全局动作和全部 11 类设置；静态页面/章节映射无缺失。当前入口状态见 [入口审计](guide-entrypoint-audit.md)，逐条证据链见 [覆盖报告](guide-coverage.md)。

文档→证据：反查快捷键、中文标签、修饰键、选中状态、参数含义、输出与版本条件，修正 Mini OCR 入口、Mac 默认按键、表格合并拆分、模板插入和主分支未发行行为等。源码和正文已交叉复核；实际用户流程、发行包和平台验证仍明确未完成。没有将页面数量、素材数量或构建结果替代此项验收。
"""
(ART / "guide-validation.md").write_text(validation)

delivery = f"""# Snow Shot 中英文手册交付记录（部分完成）

已在原站接入中文 {tutorial_counts["zh"]} 篇与英文 {tutorial_counts["en"]} 篇对等独立教程，两语各有 1 个任务导航首页，共 {len(docs)} 页。教程正文、站内路由、分组侧栏、目录、前后篇、相关链接、搜索和同任务语言切换已接通。{asset_boundary}；产品逐项实操及发行版本、平台验证尚未闭环，因此不能把整套手册标为完成。

本地查看：[中文手册预览](http://127.0.0.1:4174/zh/guides/index.html) · [English manual](http://127.0.0.1:4174/guides/index.html)。页面实际名称、路径以及新建/拆分扩写的处理方式见 [完整页面树](guide-page-tree.md)；所有教程正文均可站内阅读，不再依赖四组 GitHub 跳转。产品仓库原指南保持不变；英文教程按相同任务路径独立阅读，页面树逐项列出两语标题与实际文件。

## 计数及完成边界

| 项目 | 当前事实 |
| --- | --- |
| 正文与网站接入 | 中文 {tutorial_counts["zh"]} 教程 + 1 首页；英文 {tutorial_counts["en"]} 教程 + 1 首页；共 {len(docs)} 页，实际路径见页面树 |
| 目标发行源码的操作/参数/设置核查记录 | {len(released)} 条；包含跨教程重复核对，不代表 {len(released)} 个独立产品功能或已逐项实测可用 |
| 严格最终验收 | 已完成 {len(accepted)} 条，未完成 {len(released)-len(accepted)} 条；正文完成不等于操作验收 |
| 已完成全部条件的平台作用域 | {len(accepted_scopes)} 个；{', '.join(item['Feature ID']+' / '+item['Scope ID'] for item in accepted_scopes) or '暂无'}；仅归于该平台/版本类型/架构，不能替代整行所有公开范围 |
| 源码范围声明复核 | {len(ledger_scopes)} 条声明，{sum(row['Scope review status'] == 'reviewed' for row in ledger_scopes)} 已复核，{sum(row['Scope review status'] == 'pending' for row in ledger_scopes)} 仍待复核；声明复核不增加七项验收条件的 pass |
| 未发行候选 | IMG-040，编辑器粘贴；不进入目标 1.5.2 教程；其他主分支排除项见研究记录 |
| 已产出图像 | {len(source_svgs)} 原始 SVG + {len(english_svgs)} 英文本地化副本 + {len(webps)} 共享 WebP + {len(pngs)} 共享 PNG；共 {sum(p.stat().st_size for p in images if p.is_file())/1024/1024:.2f} MiB |
| 已产出步骤与交互演示 | {demo_count} 套不同序列/模式，共 {embed_count} 处嵌入；中英文副本与快速入门重复使用序列均不重复计数 |
| 相关测试 | {pass_count} 通过，{fail_count} 失败；{checks_detail} |

位图中 {len(result_bitmaps)} 张是 Snow Shot 的真实导出/渲染结果，{len(native_bitmaps)} 张是原生界面/步骤截图，{len(input_bitmaps)} 张是对照或练习输入，其中 {len(practice_input_bitmaps)} 张为独立生成的二维码/条码练习图，不是 Snow Shot 识别输出；SVG 与 React 演示为操作示意。英文 SVG 为相同内容的语言副本，不使教学演示数量翻倍；文字长度需要时使用已复核的英文布局调整。每个文件的 Feature ID、用途、关联步骤、来源、制作方式和状态见 [完整素材登记](guide-assets.md) / [CSV](guide-assets.csv)。

## 尚未完成的工作

{current_native_detail} 旧锁屏与已完成的运行记录分别保留，当前条件见 [原生预检](guide-runtime-preflight-current.json)。

每一个未完成 ID 都列在 [逐项待办](guide-pending.csv)，包括具体操作、UI 入口、现有证据、缺口、当前条件和下一步。完整 14 字段明细见 [覆盖报告](guide-coverage.md) / [CSV](guide-coverage.csv)。{asset_gap_detail}

跨平台发行包验证、各工具普通 UI 完整闭环、外部模型/翻译/S3、录屏设备与成片、系统集成/清理恢复仍需逐项操作。官方 macOS arm64 Full 已启动并完成上述本地图像编辑、系统保存与贴图输出链；不能由此提升其他平台、菜单或高级参数。早期开发构建和后台证据按原身份保留。身份与隔离见 [发行包记录](release-isolation-source.md)，实际步骤见 [正式包 UI 记录](runtime-release-native-image-editor.json)。未测试项是待执行工作，不自动称作外部阻塞。

本次另补本地图片识别→可编辑文字→局部/全文复制→TXT 保存/重开。新发现的 OCR-061/062 单独登记，原截图识别核查行保留。4 帧真实截图的原文件未裁切，公共组件仅按已登记区域放大显示，并保留完整原图入口；具体运行与未测的 Save 按钮路径见 [本地 OCR 记录](runtime-release-native-ocr.json)。

更早的并行审核扩写30个文档文件，补24张裁剪SVG与4张真实快捷键截图。裁剪教学素材三项缺口均以准确标注的图示补齐，原生裁剪操作仍未通过；快捷键取消的实际结果及剩余选项/平台范围另记 [SET-005 最终审核](acceptance-set005-final-review-20261110.json)。所有公开指南已复查并移除无关版本适用/制作过程备注，保留安装和故障处理所需条件；64 对页面及导航对等。详见 [公开文案审查](audit-public-guide-notes-20261110.md) 与 [双语审查](audit-guide-bilingual-parity-20261110.md)。

本次三路深审另窄合入 {len(depth_files)} 文件，补正录屏、设置、拼接/分割/PDF/画布教学；公式编辑 {formula_asset_count} SVG、分割方向 {split_direction_count} 图、{len(split_assets['conversions'])} 张原生分割截图分别有来源与制作登记。{len(split_pixels['files'])} 个历史分割导出PNG是运行像素证据，不混入公共图像计数。{shortcut_scope_detail}；整体已完成行仍按全部公开scope的显式输入判断。见 [深审整合](depth-review-integration-20261110.json)、[该批网页检查](qa-browser-depth-review-20261110.json)。{final_delta_detail}。

{split_paste_detail}

{next_batch_detail}。

后续查重新增 {len(depth_added_ids)} 条独立操作（{', '.join(depth_added_ids)}），保留输入分支及宿主范围，未把父任务或同入口的两种输入重复计数。相关原图预览、画布导航、剪贴板和设置事务图示已完成并单列来源；本轮 {len(depth_registered_assets)} 份新增/专属资产登记经源码、逐图或转换审查及最终网站复核。图示不替代原生操作。公开文案与两语任务对等另见 [本轮审查](audit-public-guide-depth-delta-20261110.md)。

{current_layout_detail} 具体记录见 [当前全部页面布局]({current_layout_name})。当前网站验证、浏览器检查、两次证据审计及具体限制见 [验证报告](guide-validation.md)；版本、参考目录和源码链见 [研究记录](guide-research.md)。本次未提交、发布或部署网站，未修改产品行为。
"""
(ART / "guide-delivery.md").write_text(delivery)
print(json.dumps(metrics, ensure_ascii=False, indent=2))
