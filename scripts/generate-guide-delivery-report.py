"""Summarize the final guide inventory and recorded validation without accepting operations."""
from pathlib import Path
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"


def csv_rows(name):
    with (ART / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def json_data(name):
    return json.loads((ART / name).read_text())


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
native_bitmaps = [p for p in bitmaps if "native" in p.name or p.stem == "start-main-interface-macos"]
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
native_editor = json_data("runtime-native-image-editor.json")
smart_erase = json_data("runtime-smart-erase-result-check.json")
auto_filter = json_data("runtime-auto-filter-document-summary.json")
site = json_data("guide-site-check.json")
anchors = json_data("coverage-anchor-check.json")
browser = json_data("qa-browser-all-tutorials.json")
final_qa = json_data("qa-browser-final-assets.json")
final_players = [p for page in final_qa["desktop"] for p in page["players"]]
final_frames = [frame for player in final_players for frame in player["frames"]]
assert all(frame["loaded"] for frame in final_frames)
ops = csv_rows("guide-operational-checks.csv")
tests = (ART / "validation-tests.log").read_text()
pass_count = int(re.search(r"(\d+) pass", tests).group(1))
fail_count = int(re.search(r"(\d+) fail", tests).group(1))
assert not site["errors"] and not anchors["errors"] and fail_count == 0
assert site["pages"] == len(docs), "Site check is stale: rebuild and check all current bilingual pages first"
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
    "date": "2026-11-09", "status": "partial",
    "new_tutorials": sum(tutorial_counts.values()), "rewritten_hubs": len(docs_by_locale),
    "pages": len(docs), "pages_by_locale": page_counts,
    "tutorials_by_locale": tutorial_counts, "matched_task_pages_per_locale": len(zh_tasks),
    "page_inventory": page_inventory,
    "coverage_rows": len(coverage), "released_check_rows": len(released),
    "strictly_accepted_released_rows": len(accepted),
    "released_rows_pending_strict_acceptance": len(released)-len(accepted),
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
    "mobile_pages_inspected": len(browser), "mobile_inspections_by_locale": mobile_by_locale, "related_tests_passed": pass_count,
    "related_tests_failed": fail_count, "site_check": site,
}
(ART / "guide-delivery.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2)+"\n")

validation = f"""# 中英文手册验证记录

日期：2026-11-09，macOS arm64，Rspress 2.0.22，Bun 1.4.2。产品研究与运行副本的区别见 [研究记录](guide-research.md)。以下网站检查通过不代表产品操作已逐项验收。

| 检查 | 实际结果 | 证据 |
| --- | --- | --- |
| `bun run format` | 退出 0 | [format 日志](validation-format.log) |
| `bun run lint` | 退出 0；5 条既有 theme/index.css 警告，另有 Biome 配置弃用提示 | [lint 日志](validation-lint.log) |
| `bun run build` | 退出 0；正式输出生成 | [build 日志](validation-build.log) |
| `bun test tests/seo.test.mjs tests/locale-redirect.test.mjs` | {pass_count} 通过，{fail_count} 失败；仅运行相关测试 | [测试日志](validation-tests.log) |
| 页面、侧栏、链接与资源 | {site['pages']} 页、{site['unique_assets_checked']} 个唯一资源、{site['unique_anchor_targets_checked']} 个锚点目标；0 错误 | [站点检查](guide-site-check.json) |
| 操作与章节映射 | {anchors['rows']} 个唯一 ID；0 缺失文件/章节锚点 | [覆盖映射](coverage-anchor-check.json) |
| SVG | {len(source_svgs)} 个原始图示 + {len(english_svgs)} 个英文文本副本，均为有效 XML | 站点检查与 [素材登记](guide-assets.csv) |

当前环境没有独立 Node 可执行程序，因此已有 node:test 测试通过 Bun 的测试运行器执行。没有修改产品代码，没有运行产品完整测试套件。

## 浏览器实际检查

- 正式预览：[中文手册](http://127.0.0.1:4174/zh/guides/index.html) · [English manual](http://127.0.0.1:4174/guides/index.html)。旧的 4173 开发预览已停止；保留 4174 供本地查看。
- 手机 390×844：实际记录中文 {mobile_by_locale["zh"]} 页、英文 {mobile_by_locale["en"]} 页；对应记录中的页面标题正常、图片无加载失败、没有 JSX/import 原样泄露，也没有整页横向溢出。详见 [逐页记录](qa-browser-all-tutorials.json)。
- 桌面 1440×1000：首页与箭头页在浅色/深色下目视检查。手机表格演示在明暗主题下检查，图示提供独立放大入口。最终浏览器视口已恢复默认，主题回到浅色。
- 英文补充检查：63 篇独立教程在手机浅色布局逐页通过；52 个步骤播放器共 159 帧经 Next/Reset 实际点击全部加载，6 个代表性英文页在手机深色下无整页溢出或坏图。英文搜索跳到箭头段落，中英文切换保持同一教程；手机目录可展开并进入颜色卡片教程。见 [英文逐页检查](qa-browser-english-tutorials.json)、[英文分镜](qa-browser-english-players.json)、[双语集成](qa-browser-bilingual-integration.json) 和 [英文字体与图示复核](qa-guide-english-svg-review.md)。
- 共享步骤播放器：检查上一步、下一步、重置和播放至末帧；箭头另检查类型、双端和路径，录屏两模式检查下一步/重置。见 [步骤演示](qa-browser-demo-checks.json)、[录屏演示](qa-browser-recording-checks.json) 与补充批次 [最终素材检查](qa-browser-final-assets.json)。
- 最终新增批次：{len(final_qa['desktop'])} 个更新页面、{len(final_players)} 组新播放器的 {len(final_frames)} 帧均通过普通按钮逐帧检查并加载；同批 {len(final_qa['mobileDark'])} 页在手机深色模式下无图片加载失败或整页溢出。专属图示另经过 [独立源码与渲染复核](qa-annotation-asset-review.md)，三处几何/标签问题已修正。
- 已有手机浏览器记录覆盖侧栏展开、颜色卡片页和导航展开。当前静态检查另核对中英文同任务页面的语言切换目标；不将早期中文浏览器记录扩大为所有英文页面已实查。
- 搜索“距离”得到 `.html` 正式地址；点击后及刷新后均保持正确教程，见 [搜索复核](qa-browser-search.json)。搜索摘要不含组件 JSX。
- 原首页 URL 与六个既有锚点保留，侧栏、页内目录、上一篇/下一篇及相关链接由构建检查覆盖。
- 减少动态效果：静态检查 prefers-reduced-motion 样式；演示默认不自动播放，分镜离散切换。没有声称已更改系统偏好完成全平台辅助功能认证。

## 产品实际操作的界限

普通原生 UI 与后台运行证据来自正在运行的 macOS 1.5.2 开发构建，按实际步骤分别记录：

- 原有普通操作：主窗口/截图进入退出、箭头拖动创建、V 点选/曲线中点、逐点创建、Command+Z/Command+Y、Backspace。见 [原生箭头记录](runtime-native-arrow-checks.json)。
- 智能擦除：类型与矩形范围通过 MCP 设置，在可见画布中完成补全；随后通过普通 Command+S、“保存截图”对话框和“保存”按钮输出 {smart_erase['size'][0]}×{smart_erase['size'][1]} PNG，并重新打开检查。虚构简单背景中右侧文字被移除、旁边蓝条保留；目标范围外改变 {smart_erase['changed_pixels_outside_target']} 个像素。此证据覆盖可见处理与原生保存，没有验证普通菜单选择类型或鼠标创建范围。见 [处理状态](runtime-visible-filter-checks.json) 与 [保存结果核对](runtime-smart-erase-result-check.json)。
- 普通图像打开：主窗口“搜索功能”选择“编辑选中的图像”结果后只定位动作行；再点击动作行打开空编辑窗口，点击“添加图像”，通过原生文件对话框选取单张虚构图片并打开，1000×680 内容显示成功；未编辑窗口也已正常关闭。拖入、多文件、文件管理器已有选择、该编辑窗口的编辑与输出仍未验证。见 [普通入口记录](runtime-native-image-editor.json)。
- ANN-065 自动滤镜：后台文档自动检测任务完成，返回 {auto_filter['job']['result']['regions']} 个检测区域总数，随后按文本、框内文本两类填充 85% 马赛克并导出 {auto_filter['output_size'][0]}×{auto_filter['output_size'][1]} 图片，实际改变 {auto_filter['changed_pixels']} 个像素。总数不表示文本区域数量，输出还出现头像形状误分类；此证据未验证普通“填充区域”菜单选择、鼠标命中或实际错误重试。见 [后台任务与输出核对](runtime-auto-filter-document-summary.json) 和 [完整请求记录](runtime-auto-filter-document-checks.json)。
- 其他后台 MCP 证据：独立背景绘图、矩形区域、渲染对照，以及本地 OCR/校正/文本导出。具体覆盖见 [逐 ID 验证](guide-operational-checks.csv) 和研究笔记。

普通入口、后台参数补丁、可见宿主处理和原生保存分别核验，没有把一种证据扩展为其他控件已经操作。也没有将本轮结果扩展到 Windows、正式发行二进制、外部服务、声音/摄像头或其他工具的全部操作。当前严格验收完成 {len(accepted)} 项，发布操作仍有 {len(released)-len(accepted)} 项待逐项闭环，具体下一步均在 [guide-pending.csv](guide-pending.csv)。

## 两次覆盖审计

产品→文档：逐条核查工具条、分组、菜单、编辑状态、结果窗口、全局动作和全部 11 类设置；页面/章节映射无缺失。审计表及证据链见 [覆盖报告](guide-coverage.md)。

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
| 确认可用的操作/参数/设置核查记录 | {len(released)} 条；包含跨教程重复核对，不代表 {len(released)} 个独立产品功能 |
| 严格最终验收 | 已完成 {len(accepted)} 条，未完成 {len(released)-len(accepted)} 条；正文完成不等于操作验收 |
| 未发行候选 | IMG-040，编辑器粘贴；不进入目标 1.5.2 教程；其他主分支排除项见研究记录 |
| 已产出图像 | {len(source_svgs)} 原始 SVG + {len(english_svgs)} 英文本地化副本 + {len(webps)} 共享 WebP + {len(pngs)} 共享 PNG；共 {sum(p.stat().st_size for p in images if p.is_file())/1024/1024:.2f} MiB |
| 已产出步骤与交互演示 | {demo_count} 套不同序列/模式，共 {embed_count} 处嵌入；中英文副本与快速入门重复使用序列均不重复计数 |
| 相关测试 | {pass_count} 通过，{fail_count} 失败；format/lint/build 通过 |

位图中 {len(bitmaps)-len(native_bitmaps)} 张是 Snow Shot 的真实导出/渲染结果，{len(native_bitmaps)} 张是原生界面/步骤截图；SVG 与 React 演示为操作示意；英文 SVG 保留原图几何并翻译文字，属于同一教学内容的语言副本，不使教学演示数量翻倍。每个文件的 Feature ID、用途、关联步骤、来源、制作方式和状态见 [完整素材登记](guide-assets.md) / [CSV](guide-assets.csv)。

## 尚未完成的工作

每一个未完成 ID 都列在 [逐项待办](guide-pending.csv)，包括具体操作、UI 入口、现有证据、缺口、当前条件和下一步。完整 14 字段明细见 [覆盖报告](guide-coverage.md) / [CSV](guide-coverage.csv)。{asset_gap_detail}

跨平台发行包验证、普通 UI 完整闭环、外部模型/翻译/S3、录屏设备与成片、系统集成/清理恢复仍需逐项操作。已有运行证据来自 macOS 开发构建；官方发行 DMG 另已下载、匹配官方 SHA256、只读挂载并核对版本与诊断 revision，但尚未启动。身份和安全隔离准备见 [发行包记录](release-isolation-source.md)，不能据此升级运行验收。未测试项是待执行工作，不自动称作外部阻塞。

当前网站验证、浏览器检查、两次证据审计及具体限制见 [验证报告](guide-validation.md)；版本、参考目录和源码链见 [研究记录](guide-research.md)。本次未提交、发布或部署网站，未修改产品行为。
"""
(ART / "guide-delivery.md").write_text(delivery)
print(json.dumps(metrics, ensure_ascii=False, indent=2))
