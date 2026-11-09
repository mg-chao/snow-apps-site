"""Render the final audit and per-ID pending work from the authoritative CSVs.

Run check-guide-coverage.py first after changing source coverage or asset gaps.
This script only writes artifacts/guide-coverage.md and artifacts/guide-pending.csv.
"""
from pathlib import Path
from collections import Counter
import csv
import json
import re
from guide_acceptance import unreleased

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"


def read_csv(name):
    with (ART / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def read_json(name):
    return json.loads((ART / name).read_text(encoding="utf-8"))


rows = read_csv("guide-coverage.csv")
assert len({row["Feature ID"] for row in rows}) == len(rows)
columns = list(rows[0])
assert len(columns) == 14
gaps = {
    row["Feature ID"]: row
    for row in read_csv("annotation-asset-gaps.csv")
    if row.get("Status", "").startswith("未完成")
}
ops = {row["Feature ID"]: row["Verification result"] for row in read_csv("guide-operational-checks.csv")}
site = read_json("guide-site-check.json")
anchors = read_json("coverage-anchor-check.json")
browser = read_json("qa-browser-all-tutorials.json")
evaluation_file = ART / "guide-acceptance-evaluation.json"
evaluations = {
    item["Feature ID"]: item
    for item in (json.loads(evaluation_file.read_text())["items"] if evaluation_file.exists() else [])
}
static_issues = {}
for issue in anchors["errors"]:
    fid = issue.partition(":")[0]
    static_issues.setdefault(fid, []).append(issue)
released = [row for row in rows if not unreleased(row)]
candidate = [row for row in rows if unreleased(row)]
candidate_ids = {row["Feature ID"] for row in candidate}
accepted = [
    row for row in released
    if row["Acceptance status"].startswith(("已完成", "验收通过", "完成："))
]
development_native = [key for key, value in ops.items() if "构建原生UI：" in value]
release_native = [key for key, value in ops.items() if "正式发行原生UI：" in value]
native = sorted(set(development_native) | set(release_native))
backend = [key for key, value in ops.items() if "后台MCP" in value]
abnormal = [
    row["Feature ID"] for row in released
    if row["Feature ID"] not in ops
    and any(term in row["Operational verification status"] for term in ("未得到完成效果", "逐字换行"))
]


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>").replace("\r", "")


def table(headers, values):
    return "\n".join(
        ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
        + ["| " + " | ".join(cell(value) for value in row) + " |" for row in values]
    )


def doc_link(target):
    path, _, fragment = target.partition("#")
    label = path.removeprefix("docs/zh/guides/")
    if fragment:
        label += "#" + fragment
    return f"[{label}](../{target})"


def task_context(row):
    target = row["Documentation path and section"]
    operation = row["Specific feature or operation"]
    if any(term in operation for term in ("Windows", "UIA", "MSAA", "管理员", "右键菜单")):
        return (
            "当前验证宿主为 macOS arm64；该 Windows 分支尚无对应发行包运行记录，源码条件已标注。",
            "在 Windows 匹配发行包的隔离测试环境执行；使用虚构窗口或文件，核对系统入口、权限提示及实际结果。",
        )
    if "/output/cloud-upload" in target:
        return (
            "尚无本项 S3 测试目标、临时凭据及端到端结果记录；未测试不等于外部阻塞。",
            "准备自有测试桶和临时凭据，按本节配置并上传虚构图像；分别核对 HTTP 结果、剪贴板链接与读取权限，清理测试对象。",
        )
    if "/translation/" in target or any(
        part in target for part in ("/recognition/table", "/recognition/formula", "/recognition/image-conversion")
    ):
        return (
            "尚未记录本项所选服务/模型、组件与网络配置的实际请求和结果；不将未测试标为外部阻塞。",
            "先记录本节实际服务/模型与组件状态，以虚构文字、表格或公式输入执行；核对等待/失败/重试、编辑及复制/保存结果。",
        )
    if "/recognition/" in target:
        return (
            "仅有局部开发构建后台 OCR 证据；本项普通结果窗口、发布包及适用版本尚未逐项验证。",
            "准备本节对应的虚构识别样本，从截图工具或结果窗口执行；对照原文/编码及编辑后的复制、导出结果。",
        )
    if "/recording/audio-camera" in target:
        return (
            "本项尚未完成设备、音源/摄像头权限、预览及成片回放检查；已有教学演示不算实录。",
            "在匹配发行包检查设备与权限，录制不含隐私的 MP4 短片；回放核对本项声音、音轨或摄像头布局。",
        )
    if "/recording/" in target:
        return (
            "本项尚无普通录屏界面至输出文件的运行记录；浏览器演示检查只验证手册组件。",
            "录制虚构短操作，按本项状态/参数执行；核对时间轴或按钮状态、输出文件、回放和必要错误恢复。",
        )
    if "/pinning/live-window" in target:
        return (
            "尚未运行本项实时源窗口状态与恢复操作；当前源代码支持结论不代替平台捕获验证。",
            "以普通虚构窗口为来源固定到屏幕，按本节最小化/恢复/关闭或转图像；核对状态提示与更新结果。",
        )
    if "/pinning/" in target:
        return (
            "尚无本项普通贴图窗口操作及适用平台发行包验证记录。",
            "用虚构图片/文本/动图创建隔离贴图，执行本项菜单或手势；核对窗口、文字、裁剪/变换、分组或导出结果并关闭测试窗口。",
        )
    if "/image-editing/" in target:
        return (
            "本项尚未按自然文件入口与匹配发行包完成编辑至输出闭环；基础分镜不能证明所有参数已操作。",
            "用有方向与尺寸标记的虚构图片，从本节自然入口执行；保留初始、关键操作和最终输出，核对尺寸、布局及保存结果。",
        )
    if "/annotations/" in target:
        return (
            "本项缺普通用户入口的逐项运行证据；局部箭头 UI 与后台渲染结果不自动覆盖本工具的全部模式。",
            "在隔离虚构画布激活本工具，执行本项创建或修改；核对工具状态、控制点、样式作用对象以及复制/PNG 输出。",
        )
    if "/output/history" in target or "/settings/storage-backup" in target:
        return (
            "本项尚未以隔离历史/配置验证，未对用户现有记录执行删除、导入或迁移。",
            "建立隔离测试记录或配置副本后执行本项；核对确认范围、取消路径、持久化/恢复或生成文件，保留测试前后状态。",
        )
    if "/output/" in target:
        return (
            "本项尚未从普通输出入口核对目标应用/文件/系统打印或分享结果。",
            "使用虚构图片执行本项输出；在独立目标文件或接收应用确认内容、尺寸、格式与取消行为，不覆盖用户文件。",
        )
    if "/getting-started/install" in target:
        return (
            "发布清单与打包/更新源码已核；本项安装或更新未在对应系统的干净环境完成。",
            "在相应系统/架构的隔离环境取得匹配发布包，执行本项；记录安装渠道、启动路径、版本与设置结果，保留恢复点。",
        )
    if "/getting-started/permissions" in target:
        return (
            "开发构建 MCP 报告相关权限已授予，但授权/重启流程和本项普通 UI 动作尚未逐项核对。",
            "在可恢复的 macOS 测试配置中查看本项系统权限和实际应用路径；按提示授权/重启并完成对应截图、输入或声音动作。",
        )
    if "/settings/" in target:
        return (
            "本项设置字段与处理链已核，但尚未记录普通界面更改、效果及重启后的持久状态。",
            "备份隔离测试配置，在本项入口更改一个选项；执行对应用户任务核对效果，按需重启并恢复原值。",
        )
    return (
        "本项尚无普通用户入口的逐项运行记录；macOS 开发构建已可访问，不再以早期连接超时作为阻碍。",
        "在匹配发行包以不含隐私的虚构素材执行本项；保留输入、操作、可观察状态和取得的结果，按版本/平台列补齐适用环境。",
    )


pending = []
for row in rows:
    fid = row["Feature ID"]
    if row in accepted:
        continue
    operation = row["Specific feature or operation"]
    entry = row["Actual UI entry point"]
    evidence = row["Operational verification status"]
    constraint, next_step = task_context(row)
    gap = f"尚缺从普通用户入口完成「{operation}」的目标发行包/适用平台验收；源码与正文完成不能替代。"
    if fid in release_native:
        gap = f"已有 macOS arm64 Full 正式发行包普通 UI 的局部核验记录（成功与未完成步骤见当前证据），仍缺「{operation}」的完整公开作用域核验。"
        constraint = "已核对官方 DMG 与二进制身份，在独立数据目录运行；仅将实际执行的分支记为局部证据，不扩展至其他参数、平台或版本类型。"
        next_step = "对照 release UI 记录和 acceptance ledger，只补未执行的分支与其他适用平台；保留成功的本地编辑、系统保存和贴图输出证据。"
    elif fid in native:
        gap = f"已有 macOS 开发构建原生 UI 的局部核验记录（结果见当前证据），仍缺「{operation}」的完整公开作用域核验。"
        constraint = "实际运行副本为 macOS 1.5.2 开发构建，尚未证明二进制等同发布标签；已有的原生操作不需要当成从未发生。"
    elif fid in backend:
        gap = f"已有后台 MCP 局部处理记录（结果见当前证据），仍缺「{operation}」的普通用户入口和完整公开作用域核验。"
        constraint += " 后台 MCP 的输入/输出与普通 UI 的进入、焦点和控件操作分别记录。"
    elif fid in abnormal:
        gap = f"本项后台尝试未得到合格完成结果；「{operation}」的原生操作和有效结果仍待核对。"
        constraint = evidence + "；这不能推断原生界面一定同样失败，也不能视为成功。"
        next_step = "在原生 UI 对虚构素材执行并等待完成，核对是否仍异常；成功后留存合格结果，仍异常则记录实际条件/提示并修订限制说明，不修改产品行为来迁就文档。"
    asset_gap = gaps.get(fid)
    asset_text = asset_gap["Specific asset gap"] if asset_gap else "没有当前明确登记的专属素材缺口；仍需按本项逐一核对素材与实际行为，不能自动判定全部高级参数素材已验收。"
    if asset_gap:
        gap += " 专属素材未完成：" + asset_gap["Specific asset gap"] + "。"
        constraint += " 素材当前情况：" + asset_gap["Current blocker or limitation"] + "。"
        next_step += " 素材补齐动作：" + asset_gap["Actionable next capture"] + "。"
    decision = evaluations.get(fid)
    if decision and decision["required_scopes"]:
        accepted_scopes = "、".join(decision["accepted_scopes"]) or "无"
        missing = [
            scope["Scope ID"] + "：" + "、".join(scope["missing_criteria"])
            for scope in decision["scopes"] if scope["missing_criteria"]
        ]
        gap += " 已完整验收作用域：" + accepted_scopes + "；剩余：" + "；".join(missing) + "。"
        next_step += " 仅补齐尚缺作用域及条件，保留已通过证据；按 guide-acceptance-schema.md 更新显式记录。"
    elif decision and fid not in candidate_ids:
        constraint += " 完整公开作用域尚未显式复核，不能按当前宿主自行缩小范围。"
        next_step += " 依据正文平台/版本条件声明并复核完整适用作用域，再登记七项条件的证据。"
    if fid in static_issues:
        gap += " 当前站内静态检查：" + "；".join(static_issues[fid]) + "。"
        next_step += " 修正对应路径/章节或更新构建后重新运行静态检查，不将旧扫描当作当前通过。"
    if fid in candidate_ids:
        gap = "图像编辑器剪贴板粘贴未进入目标发布标签；尚无对应发行教程、专属素材与发行包验证。"
        constraint = "main 的 b687a9288 已实现，但 v1.5.2_snow-shot/f02f50e 不含；开发树仍标 1.5.2 不能作为已发布证据。"
        next_step = "等待包含该提交的正式发行版，先核对发布提交和实际入口，再补独立图像编辑器粘贴步骤、入口/结果素材及各适用平台操作验证。"
        asset_text = "未制作；等待该能力正式发行，不为目标 1.5.2 虚构入口素材。"
    pending.append({
        "Feature ID": fid,
        "Category": row["Category"],
        "Specific feature or operation": operation,
        "Actual UI entry point": entry,
        "Product version and platform": row["Product version and platform"],
        "Documentation path and section": row["Documentation path and section"],
        "Current evidence": evidence,
        "Specific gap": gap,
        "Current constraint": constraint,
        "Next action": f"对应入口「{entry}」，执行「{operation}」。{next_step}",
        "Specific asset gap": asset_text,
        "Acceptance status": "不适用于目标发行版；等待后续发行" if fid in candidate_ids else "未完成；待逐项严格验收",
    })

with (ART / "guide-pending.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(pending[0]))
    writer.writeheader()
    writer.writerows(pending)

parts = [
    "# Snow Shot 操作级覆盖与最终验收记录",
    "",
    "研究日期：2026-11-09（Asia/Shanghai）。本报告由 scripts/generate-guide-coverage-report.py 根据最终明细生成；先运行 scripts/check-guide-coverage.py 合并分表及当前未完成素材项，再重新生成本报告。",
    "",
    f"当前为**{'目标发行操作已严格验收' if len(accepted) == len(released) else '部分完成'}**：记录 {len(rows)} 个稳定 Feature ID，其中 {len(released)} 项为目标发布标签已有实现链的操作，另有 {len(candidate)} 项未发行候选。{len(released)} 项正文已编写；严格验收完成 {len(accepted)} 项、未完成 {len(released)-len(accepted)} 项。网站当前检查与缺口分别列下，候选不计入已发布功能分母。",
    "",
    f"**计数口径：{len(released)} 是操作、参数、设置和核对清单的行数，不是 {len(released)} 个互不重复的产品功能。** 入门教程与具体工具教程会分别核对同一能力，存在跨教程重复检查；这里没有把它们合并成去重后的产品功能数。Feature ID 用于续接具体检查工作，不用于宣传功能数量。",
    "",
    "完整 14 字段机器可读明细见 [guide-coverage.csv](guide-coverage.csv)，下方逐 ID 全量表保留同样 14 字段。每个未完成 ID 的具体缺口、当前条件和下一步见 [guide-pending.csv](guide-pending.csv)。未测试代表尚需执行的工作，不自动等于受到外部阻塞。",
    "",
    "## 分开统计来源、正文、运行、素材与验收",
    "",
    table(["检查层", "当前事实", "不据此推断"], [
        ["源码与发行可用性", f"{len(released)} 项已对照 v1.5.2_snow-shot/f02f50e 的 UI→事件/处理→结果链；IMG-040 仅主分支有", "发布源码包含不等于所有发行二进制和平台已经实操"],
        ["正文与网站接入", f"{len(released)} 项正文已编写、源码和中文标签交叉复核；{site['standalone_tutorials']} 篇独立教程和首页已接入", "页面存在、文字校对或 build 成功不等于教程操作验收"],
        ["正式发行原生入口", f"{len(release_native)} 个 ID 记录局部原生核验：{', '.join(release_native)}；包含成功操作和未完成的自有保存窗口尝试，逐行区分", "仅归于官方 macOS arm64 Full 二进制的实际步骤；不扩展至 Windows、Mini、Intel Mac 或未执行的分支"],
        ["开发构建原生入口", f"{len(development_native)} 个 ID 记录局部原生核验：{', '.join(development_native)}；另观察主窗口和截图进入/退出", "早期开发构建证据仍按原身份保留，不能改标为正式发行证据"],
        ["后台处理", f"{len(backend)} 个 ID 记录局部后台 MCP 核验：{', '.join(backend)}；具体结果保留在逐行记录", "MCP 不是普通 UI 入口；不能替代点击、焦点、菜单、设备权限的核对"],
        ["异常样本", f"{len(abnormal)} 项后台未得合格结果：{', '.join(abnormal)}", "未发布内部 QA 样本；不据此断定原生 UI 一定失败"],
        ["其他逐项运行", f"{len(released)-len(ops)-len(abnormal)} 项发布操作没有单独的部分成功/异常运行记录", "不是声称这些功能不存在或不可操作"],
        ["教学素材", f"最近站内检查存在并可引用的资源 {site['unique_assets_checked']} 项，其中 SVG {site['svg_files']}；当前另有 {len(gaps)} 项具体专属素材缺口", "资源数量、基础三帧或重建图不能替代所有交互与高级参数教学"],
        ["严格验收", f"发布操作 {len(accepted)} 完成、{len(released)-len(accepted)} 未完成；IMG-040 单列候选", "不因预算、文件数、构建或局部样本而宣布整套手册完成"],
    ]),
    "",
    f"原生与后台运行记录按 ID 合并共 {len(set(native) | set(backend))} 项；两类可以重叠（当前交集：{', '.join(sorted(set(native) & set(backend))) or '无'}），不能直接相加。局部记录不会自行授予完整发行作用域验收。",
    "",
    f"显式验收由 [guide-acceptance-schema.md](guide-acceptance-schema.md)、两个 acceptance 输入 CSV 和 [guide-acceptance-evaluation.json](guide-acceptance-evaluation.json) 管理。当前有 {sum(len(item['accepted_scopes']) for item in evaluations.values())} 个作用域通过全部条件；每个平台/版本类型的部分证据和待补条件分别保留，不因重跑脚本强制清零已验证作用域，也不从源码/构建自动提升为完成。",
    "",
    "开发构建与官方发行包分别记录：早期开发 bundle 的提交身份仍未证明等同发布标签。后续已启动 SHA256 匹配官方 DMG 的 macOS arm64 Full，嵌入 revision 为 f02f50e5c6b1、可执行文件 SHA256 为 93ad73ad4a53dd1d7456a0f253d094df04832af21a1b36d42973940ace82b959，采用独立 app data。其原生编辑→系统保存→固定→再保存→重开核对见 runtime-release-native-image-editor.json；自有保存窗口未完成的尝试见 runtime-release-save-dialog-choice.json。没有修改产品行为或授予屏幕权限。",
    "",
    "## 操作范围",
    "",
]
prefixes = ["START", "CAP", "CAPSET", "ANN", "IMG", "OCR", "TR", "PIN", "REC", "OUT", "SET"]
summary = []
for prefix in prefixes:
    subset = [row for row in rows if row["Feature ID"].split("-")[0] == prefix]
    candidates = sum(row["Feature ID"] in candidate_ids for row in subset)
    summary.append([
        prefix, len(subset), len(subset)-candidates, candidates,
        sum(row in accepted for row in subset),
        len(subset)-candidates-sum(row in accepted for row in subset),
        sum(row["Feature ID"] in gaps for row in subset),
    ])
parts += [table(["ID 组", "全部 ID", "发布操作", "未发行候选", "严格完成", "发布操作未完成", "专属素材明确缺口"], summary), ""]

parts += [
    "## 入口审计：产品到文档",
    "",
    "下列“源码已查”指入口、事件/命令、处理与可见结果的交叉检查；原生 UI/后台运行分别列出。源码位于 /Users/chao/workspaces/snow-apps；表中界面文件省略 snow_shot/src/presentation/ 前缀，applicationcontroller.cpp 位于 snow_shot/src/app/，绘图引擎位于 snow_draw_engine_qt/。不把翻译字符串或类型声明单独当作实现证据。",
    "",
]
entry_rows = [
    ["主界面、页面导航、全局动作", "已查 mainwindow.cpp、components/contentcardwidget.cpp、settings/settingscatalog.cpp:5044,5353；动作接 applicationcontroller.cpp", "已观察实际开发构建主窗口、默认 ⌃1 和截图入口；未逐动作运行", "START、SET；getting-started/、settings/"],
    ["系统托盘菜单与点击动作", "已查 services/systemtraycontroller.cpp；settingscatalog.cpp:921-1026,2225；菜单动作接应用控制器", "未逐项打开/触发托盘动作", "SET；settings/toolbars-tray.mdx"],
    ["桌面悬浮工具栏", "已查 toolbar/floatingtoolbarcontroller.cpp；settingscatalog.cpp:760-795；布局和动作分发", "未逐动作、透明度或拖放实操", "SET；settings/toolbars-tray.mdx"],
    ["截图主工具栏与完成/取消", "已查 tools/screenshottoolpalette.cpp、overlay/screenshotoverlayinputhandler.cpp、services/screenshotcontroller.cpp", "已进入/取消截图并选择箭头；没有覆盖全部输出动作", "CAP、OUT、ANN；capture/、output/、annotations/"],
    ["工具分组、隐藏/更多和布局", "已查 screenshottoolpalette.cpp:564-595,6332,6669；components/settingscustomwidget.cpp:987-1330；toolbar layout", "局部选择箭头；全部组与隐藏/叠放的普通操作待核", "ANN、OCR、SET；工具各页与toolbars-tray"],
    ["截图及贴图上下文菜单", "已查 overlay 输入动作和 pinned/screenshotpinnedwindow.cpp:3410-4014；输出/分组/加载/动画处理", "菜单及平台分支未逐项操作", "CAP、PIN、OUT"],
    ["选区尺寸、比例、区域组合与样式", "已查 selection/screenshotselectiontoolbarwidget.cpp、screenshotselectionresizeworkflow.cpp；overlay inputhandler.cpp:1018-1260,1500-1555；selectionmodel", "后台替换/增加矩形区域并导出成功；数值/比例/多区域普通 UI 未逐项核验", "CAP、CAPSET；capture/各页"],
    ["标注子类型与属性面板", "已查 tools/screenshottoolpalettestylecontrols.cpp、core/screenshotcanvastoolstyles.cpp；引擎 creation/input/renderer", "开发构建箭头与曲线控制点局部成功；正式包快捷键激活箭头/形状/文字并生成对象，未操作子类型/样式菜单；后台箭杆/滤镜对照成功", "ANN；annotations/各独立工具页"],
    ["元素编辑、图层顺序与模板", "已查 screenshottoolpalette.cpp:8770-9167、toolbar/screenshottoolbarwindow.cpp:370-378 与引擎选择/重排", "正式包V选择、箭头端点、矩形缩放旋转、文字移动、撤销/重做及确认选中后Delete成功；旧开发构建曲线中点/Backspace按原身份保留；图层/模板及其余分支待测", "ANN；elements、templates及各工具"],
    ["独立图片编辑、拼图、分割、PDF、画布", "已查 imageediting/imageeditingwindow.cpp:305,851、collage/collageeditorwidget.cpp:2038、imagesplit/*、collage PDF 和 globalcanvas/globalcanvascontroller.cpp", "正式包空编辑器添加单图、创建标注、系统保存、固定并重新打开成功；拖入/多图及拼图/分割/PDF/画布仍待逐项；开发版粘贴 IMG-040 单列不适用", "IMG；image-editing/"],
    ["文本识别入口与结果窗口", "已查 ocr/screenshotrecognitionsessioncontroller.cpp:3033、screenshotrecognitionwindow.cpp、screenshotocrtexttransform.cpp", "后台虚构图本地 OCR、文字校正与文本导出成功；普通 UI 未测", "OCR；recognition/text、models"],
    ["表格、条码、公式、图像转换", "已查 screenshottoolpalette.cpp:6669-6734、ocr/screenshottableeditor.cpp:576-745、table conversion、recognition file export", "普通入口、模型请求、结果编辑与导出未逐项实操", "OCR；recognition/工具页"],
    ["截图/文本/划词翻译与服务配置", "已查 components/screenshottranslationsettingsdialog.cpp、translationpagewidget.cpp 与控制器/提供商；settingscatalog.cpp:3553-3645", "尚无本项服务端到端运行记录；不能把未测试称为外部阻塞", "TR；translation/"],
    ["贴图窗口、文本、管理与分组", "已查 pinned/screenshotpinnedwindow.cpp、screenshotpinnedtextannotation.cpp、components/pinnedwindowmanagementpagewidget.cpp", "普通贴图变换/文本/组管理待逐项实操", "PIN；pinning/"],
    ["动图与实时窗口贴图", "已查 screenshotpinnedwindow.cpp:3410-3485,3701-3740；pinned/screenshotpinnedlive.cpp:293-304,512 与平台 source", "需虚构动图/普通源窗口完成暂停、逐帧和源状态验证；尚未运行", "PIN；animation、live-window"],
    ["录屏区域、工具栏、音源/摄像头/输入效果", "已查 recording/screenrecordingcontroller.cpp:630-760、screenshottoolpalette.cpp:8035-8115,10430-11060、webcam/audio/effects", "浏览器教学演示可运行；实际屏幕、设备和成片链未逐项录制", "REC；recording/"],
    ["录屏时间轴、渲染、导出和恢复", "已查 recording/recordingtrimtoolbar.cpp:20,92、recordingtrimsession.cpp:51-76,303、recordingrenderdialog.cpp:98-125", "网站时间轴分步/重置已检查；产品裁剪/变速/导出待实操", "REC；recording/trim-export.mdx"],
    ["保存、打印、AirDrop、云上传、历史", "已查 services/screenshotsaveasfiledialog.cpp、screenshotimagefileservice.cpp、screenshotprintservice.cpp、screenshotairdropservice.cpp、screenshotclouduploadservice.cpp:128-262、components/screenshothistorypagewidget.cpp", "正式包编辑器/贴图系统保存目录、命名、PNG输出成功；自有窗口选择后导出未完成；S3/打印/AirDrop/历史自然入口仍待逐项", "OUT；output/"],
]
parts += [table(["入口", "源码审计及位置", "实际运行核对", "文档映射"], entry_rows), ""]
parts += [
    "## 设置分类逐类审计",
    "",
    "完整设置页注册与导航在 snow_shot/src/presentation/settings/settingscatalog.cpp:5044,5353。以下恰为 11 类设置；主窗口独立的全局快捷键、全局鼠标、截图历史、固定到屏幕管理和完整版翻译另在入口表审计。原生主窗口看到了导航，不等于每个设置控件已经更改并验证。",
    "",
]
settings = [
    ["常规", "settingscatalog.cpp:4092；语言、启动/更新、管理员/右键集成、优先级/QoS/内存；settingsbackend.cpp 与平台服务", "发布链已查；主窗口/平台默认按键已观察，安装更新/系统设置改变未逐项运行", "START、SET；install、network-integration"],
    ["外观", "settingscatalog.cpp:4143；theme/font/toolbar size/skinItems → ThemeManager/MainWindowSkinController", "源码/中文标签已查；主题、字体、三表面皮肤参数普通 UI 待测", "SET；settings/appearance.md"],
    ["截图", "settingscatalog.cpp:4250；交互、截图界面、操作工具栏、标注偏好、捕获内容、Windows高级捕获 → overlay/toolbar", "源码逐选项已查；普通截图/箭头局部观察，其余 CAPSET/SET/ANN 操作待核", "CAPSET、CAP、ANN、SET；basics、precise-selection、toolbars-tray"],
    ["固定到屏幕", "settingscatalog.cpp:4378；交互、窗口界面、文本样式、操作工具栏 → pinned window/geometry/text", "源码逐选项已查；普通窗口参数和结果未逐项实操", "PIN、SET；pinning/与toolbars-tray"],
    ["屏幕录制", "settingscatalog.cpp:4460；视频/音频、动图、编码、录制内容、工具栏、交互 → RecordingSettings/controller/runtime", "源码逐选项已查；设备、录制与导出未逐项运行", "REC、SET；recording/与toolbars-tray"],
    ["文本识别与翻译（Mini 为文本识别）", "settingscatalog.cpp:4590；识别输出、文本背景、翻译、模型与性能 → recognition/translation controllers", "后台本地 OCR/校正/导出局部成功；普通结果 UI 与其他选项待核", "OCR、TR；recognition/与translation/"],
    ["应用快捷键", "settingscatalog.cpp:4677；截图/标注/固定/录屏/识别/Windows菜单 → local shortcut managers", "源码逐动作已查；V 等局部实际使用不代表全部绑定已核验", "SET及各工具；settings/shortcuts.mdx"],
    ["托盘与悬浮工具栏", "settingscatalog.cpp:4787；托盘图标/点击/菜单与浮动开关/不透明度/布局 → systemtraycontroller/floatingtoolbarcontroller", "源码及平台分支已查；普通托盘/悬浮操作待逐项运行", "SET；settings/toolbars-tray.mdx"],
    ["导出与存储", "settingscatalog.cpp:4844；图像/视频输出、历史/贴图保留、配置/日志/目录/清理 → save/storage/archive services", "源码逐项已查；真实文件/剪贴板/存储持久化与清理未逐项运行", "OUT、REC、SET；output/、trim-export、storage-backup"],
    ["网络与连接", "settingscatalog.cpp:4939；自定义AI/翻译/服务器、代理、MCP → providers/network/server", "MCP状态已读、后台客户端可用；代理/第三方配置字段和网络请求未逐项验证", "TR、SET、OUT；services、network-integration、cloud-upload"],
    ["应用权限（仅 macOS）", "settingscatalog.cpp:5029；屏幕与系统音频录制/辅助功能/输入监控/麦克风 → services/apppermissionservice.cpp/permissionguidecontroller.cpp", "MCP状态报告四项已授予；普通系统跳转、授权/重启及各功能结果待核", "START、REC；getting-started/permissions.md"],
]
parts += [table(["设置分类", "源码分区与处理链", "源码/运行分别记录", "正文映射"], settings), ""]

parts += [
    "## 当前专属素材缺口",
    "",
    f"仅将 annotation-asset-gaps.csv 中 Status 以“未完成”开头的记录计为当前明确缺口，共 {len(gaps)} 项；已补齐的教学重建不会再覆盖成未完成。教学重建允许用于讲解，但仍不能冒充真实应用操作或发行包验证。",
    "",
    table(["Feature ID", "具体缺口", "当前情况", "可执行的补齐动作"], [
        [fid, row["Specific asset gap"], row["Current blocker or limitation"], row["Actionable next capture"]]
        for fid, row in gaps.items()
    ]) if gaps else "当前专属素材缺口表没有仍标“未完成”的记录；这不代表所有普通 UI/平台/高级参数素材已经通过严格验收。",
    "",
    ("IMG-040 另为未发行候选：等待包含 b687a9288 的正式版本后，重新核对入口并补正文、素材和运行；没有为目标 1.5.2 编造该步骤。"
     if "IMG-040" in candidate_ids else "当前未发行候选以逐 ID 可用性记录为准；只有实际发行事实更新后才按新作用域验收。"),
    "",
    "## 网站检查与反向证据审计",
    "",
    f"- 最近静态检查：{site['pages']} 页（含首页），{site['standalone_tutorials']} 篇独立教程；{site['unique_assets_checked']} 个唯一资源，{site['unique_anchor_targets_checked']} 个锚点目标，错误 {len(site['errors'])}，见 [guide-site-check.json](guide-site-check.json)。",
    f"- 覆盖表反查：{anchors['rows']} 行、{anchors['unique_ids']} 个唯一 ID；教程路径/章节检查错误 {len(anchors['errors'])}，见 [coverage-anchor-check.json](coverage-anchor-check.json)。候选映射研究笔记而非虚构公开页面。",
    f"- 浏览器快照覆盖 {len({item['path'] for item in browser})} 篇教程的 390px 移动视口，记录的缺图、字面 import 和横向溢出异常为 {sum(bool(item.get('badImages')) or item.get('literalImport', False) or item.get('scrollWidth', 0) > item.get('width', 99999) for item in browser)}；见 [qa-browser-all-tutorials.json](qa-browser-all-tutorials.json)。箭头、表格、首页等明暗/桌面检查与演示控件结果见 QA 图及 demo/recording checks。",
    "- 文档到证据：对默认按键、中文按钮、选区 Shift/Q、对象选择状态、模板插入、表格输出与版本条件反查，修正后保留源码索引；产品未因文档修改行为。所有真实图片/重建图的来源与用途在 assets-*.csv 中分别登记。",
    "- 未将浏览器中的教学演示点击，计入产品鼠标手势验证；未将后台 OCR、绘图或 PNG 结果，计入普通菜单和输入态验证。严格验收仍按逐 ID 完成用户入口、选项/限制、结果、素材与网站检查。",
    "",
    "## 实际页面及处理方式",
    "",
    f"原中文指南首页 docs/zh/guides/index.md 已重写为任务导航并保留路由；新增 {site['standalone_tutorials']} 篇站内教程。原来四组 GitHub 跳转已拆成独立任务；产品仓库原指南保留。下表仅表示正文已编写与网站已接入，不是各页面内全部操作已严格验收。",
    "",
]
page_paths = sorted({row["Documentation path and section"].partition("#")[0] for row in released})
pages = []
for path in page_paths:
    text = (ROOT / path).read_text(encoding="utf-8")
    match = re.search(r"^title:\s*(.+)$", text, re.M)
    title = match.group(1).strip("'\"") if match else Path(path).stem
    ids = [row["Feature ID"] for row in released if row["Documentation path and section"].partition("#")[0] == path]
    done = sum(row["Feature ID"] in ids for row in accepted)
    pages.append([title, f"[{path}](../{path})", "新建；独立任务，源码与本地化复核", len(ids), f"正文已编写；严格验收 {done}/{len(ids)}，静态错误按逐项记录"])
parts += [table(["独立教程", "实际文件", "处理方式", "映射操作行", "状态"], pages), ""]
parts += [
    "## 全量操作表（14 字段）",
    "",
    "下表逐 ID 展示全部操作；字段和 [guide-coverage.csv](guide-coverage.csv) 对应。正文栏将早期“待页面检查”的陈述合并为当前静态检查结果；运行、素材和验收仍独立保留。每行的未完成动作可按同一 ID 在 guide-pending.csv 查到。编号有历史保留空缺，不因空缺而补造功能。",
    "",
]
for prefix in prefixes:
    subset = [row for row in rows if row["Feature ID"].split("-")[0] == prefix]
    parts += [f"### {prefix}", ""]
    values = []
    for row in subset:
        copy = row.copy()
        copy["Feature ID"] = f'<a id="{row["Feature ID"]}"></a>{row["Feature ID"]}'
        copy["Documentation path and section"] = doc_link(row["Documentation path and section"])
        if row["Feature ID"] not in candidate_ids:
            copy["Content status"] = (
                "正文已编写；源码/本地化复核；当前静态检查有对应错误"
                if row["Feature ID"] in static_issues
                else "正文已编写；源码/本地化复核；路径/章节/资源静态检查通过；实际验收状态独立记录"
            )
        if "根代理正在记录" in copy["Operational verification status"]:
            copy["Operational verification status"] = "未逐项实机验证；已记录的局部实际UI覆盖见 guide-operational-checks.csv"
        if row["Feature ID"] in gaps:
            copy["Asset status"] = "基础素材已制；专属素材未完成：" + gaps[row["Feature ID"]]["Specific asset gap"]
        values.append([copy[column] for column in columns])
    parts += [table(columns, values), ""]
(ART / "guide-coverage.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
print(json.dumps({
    "rows": len(rows),
    "released": len(released),
    "candidate": len(candidate),
    "strict_complete": len(accepted),
    "strict_incomplete": len(released)-len(accepted),
    "pending_rows": len(pending),
    "current_specialized_asset_gaps": len(gaps),
    "native_partial_ids": native,
    "release_native_partial_ids": release_native,
    "development_native_partial_ids": development_native,
    "backend_partial_ids": backend,
    "abnormal_result_ids": abnormal,
}, ensure_ascii=False))
