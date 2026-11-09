"""Explicit, reviewed acceptance evidence; never infer acceptance from a build."""
from pathlib import Path
from urllib.parse import urlparse
import csv
import hashlib

SCOPE_COLUMNS = [
    "Feature ID", "Scope ID", "Target version", "Platform", "Edition", "Architecture",
    "Documentation SHA256", "Scope basis", "Scope review status", "Reviewer", "Notes",
]
EVIDENCE_COLUMNS = [
    "Feature ID", "Scope ID", "Target version", "Criterion", "Result", "Evidence kind",
    "Build channel", "Evidence refs", "Review status", "Reviewer", "Notes",
]
CRITERIA = (
    "availability", "workflow", "result", "options-limitations", "assets", "content", "website",
)
KINDS = {
    "source", "release_availability", "native_ui", "user_visible_result", "backend_result",
    "asset_review", "content_review", "website_review", "scope_review",
}
REQUIRED_KIND = {
    "availability": "release_availability",
    "workflow": "native_ui",
    "result": "user_visible_result",
    "options-limitations": "native_ui",
    "assets": "asset_review",
    "content": "content_review",
    "website": "website_review",
}
RELEASE_CRITERIA = {"availability", "workflow", "result", "options-limitations"}


def unreleased(row):
    return row["Availability conclusion"].startswith("未发行")


def read_ledger(path, columns):
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError(f"{path.name}: expected exact schema {columns}")
        return [{key: (value or "").strip() for key, value in item.items()} for item in reader]


def refs_exist(root, refs):
    items = [item.strip() for item in refs.split(";") if item.strip()]
    if not items:
        return False
    for item in items:
        if urlparse(item).scheme in {"http", "https"}:
            # The named reviewer must have checked remote evidence; no implied web verification.
            continue
        path = item.partition("#")[0]
        if not (root / path).is_file():
            return False
    return True


def load_inputs(root, rows):
    by_id = {row["Feature ID"]: row for row in rows}
    scopes = read_ledger(root / "artifacts/guide-acceptance-scopes.csv", SCOPE_COLUMNS)
    evidence = read_ledger(root / "artifacts/guide-acceptance-evidence.csv", EVIDENCE_COLUMNS)
    keys = set()
    for scope in scopes:
        fid, sid = scope["Feature ID"], scope["Scope ID"]
        key = (fid, sid)
        if fid not in by_id or not sid or key in keys:
            raise ValueError(f"invalid or duplicate advertised scope: {key}")
        keys.add(key)
        if scope["Platform"] not in {"Windows", "macOS"} or scope["Edition"] not in {"Full", "Mini"}:
            raise ValueError(f"{key}: declare one actual platform and edition per scope")
        if not scope["Target version"] or not scope["Architecture"]:
            raise ValueError(f"{key}: version and architecture declaration required")
        if scope["Target version"] not in by_id[fid]["Product version and platform"]:
            raise ValueError(f"{key}: target version not present in current product coverage")
        if scope["Scope review status"] not in {"pending", "reviewed"}:
            raise ValueError(f"{key}: invalid scope review status")
        if scope["Scope review status"] == "reviewed":
            doc = by_id[fid]["Documentation path and section"].partition("#")[0]
            if (
                not scope["Reviewer"]
                or not scope["Notes"]
                or len(scope["Documentation SHA256"]) != 64
                or doc not in scope["Scope basis"]
                or not refs_exist(root, scope["Scope basis"])
            ):
                raise ValueError(f"{key}: reviewed scope needs reviewer, rationale, current tutorial and existing evidence")
    seen = set()
    for item in evidence:
        key = (item["Feature ID"], item["Scope ID"])
        criterion = item["Criterion"]
        identity = key + (criterion,)
        if key not in keys or criterion not in CRITERIA or identity in seen:
            raise ValueError(f"undeclared scope, criterion or duplicate evidence: {identity}")
        seen.add(identity)
        if item["Result"] not in {"pass", "fail", "pending", "not_applicable"}:
            raise ValueError(f"{identity}: invalid result")
        if item["Evidence kind"] not in KINDS:
            raise ValueError(f"{identity}: invalid evidence kind")
        if item["Build channel"] not in {"release", "development", "source", "website", "not_applicable"}:
            raise ValueError(f"{identity}: invalid build channel")
        if item["Review status"] not in {"pending", "reviewed"}:
            raise ValueError(f"{identity}: invalid review status")
        scope = next(scope for scope in scopes if (scope["Feature ID"], scope["Scope ID"]) == key)
        if item["Target version"] != scope["Target version"]:
            raise ValueError(f"{identity}: evidence version differs from declared target")
        if item["Result"] == "not_applicable" and criterion not in {"assets", "options-limitations"}:
            raise ValueError(f"{identity}: this criterion cannot be waived")
        if item["Review status"] == "reviewed":
            if not item["Reviewer"] or not item["Notes"] or not refs_exist(root, item["Evidence refs"]):
                raise ValueError(f"{identity}: reviewed evidence needs reviewer, notes and usable references")
    return scopes, evidence


def qualifying(item, criterion, scope, root):
    if not item or item["Review status"] != "reviewed":
        return False, "缺少已复核证据"
    if not refs_exist(root, item["Evidence refs"]):
        return False, "证据引用不存在"
    if item["Target version"] != scope["Target version"]:
        return False, "证据版本与作用域不符"
    if item["Result"] == "not_applicable":
        ok = criterion in {"assets", "options-limitations"} and item["Evidence kind"] == "scope_review" and bool(item["Notes"])
        return ok, "有据不适用" if ok else "不允许跳过此验收条件"
    if item["Result"] != "pass":
        return False, "未通过或待验证"
    if item["Evidence kind"] != REQUIRED_KIND[criterion]:
        return False, "现有证据类型仅作参考，未覆盖本验收条件"
    if criterion in RELEASE_CRITERIA and item["Build channel"] != "release":
        return False, "开发构建或源码证据不能替代目标发行构建"
    return True, "已复核通过"


def evaluate(root, row, scopes, evidence, asset_gap=False, website_ok=True):
    fid = row["Feature ID"]
    declared = [scope for scope in scopes if scope["Feature ID"] == fid]
    result = {
        "Feature ID": fid, "complete": False, "required_scopes": [], "accepted_scopes": [],
        "scopes": [], "reason": "",
    }
    if unreleased(row):
        result["reason"] = "未发行候选；不能作为目标发行版验收"
        return result
    if not declared:
        result["reason"] = "尚未显式复核教程的完整公开作用域，未按平台或版本自动推断"
        return result
    for scope in declared:
        sid = scope["Scope ID"]
        result["required_scopes"].append(sid)
        items = {
            item["Criterion"]: item for item in evidence
            if item["Feature ID"] == fid and item["Scope ID"] == sid
        }
        passed, missing, references = [], {}, []
        doc = root / row["Documentation path and section"].partition("#")[0]
        content_current = doc.is_file() and hashlib.sha256(doc.read_bytes()).hexdigest() == scope["Documentation SHA256"]
        for criterion in CRITERIA:
            item = items.get(criterion)
            ok, reason = qualifying(item, criterion, scope, root)
            if criterion == "assets" and asset_gap:
                ok, reason = False, "仍有明确登记的必需专属素材缺口"
            if criterion == "website" and not website_ok:
                ok, reason = False, "当前站内检查尚未通过"
            if scope["Scope review status"] != "reviewed":
                ok, reason = False, "教程公开作用域尚未复核"
            if not content_current:
                ok, reason = False, "教程正文与已复核摘要不符，需重新核对内容和作用域"
            if ok:
                passed.append(criterion)
                references.extend(item["Evidence refs"].split(";"))
            else:
                missing[criterion] = reason
        scope_result = {
            "Scope ID": sid, "Target version": scope["Target version"],
            "Platform": scope["Platform"], "Edition": scope["Edition"],
            "Architecture": scope["Architecture"], "passed_criteria": passed,
            "missing_criteria": missing, "complete": not missing,
            "evidence_refs": list(dict.fromkeys(references)),
            "reference_evidence": [
                {key: item[key] for key in ("Criterion", "Result", "Evidence kind", "Build channel", "Review status", "Evidence refs", "Notes")}
                for item in items.values()
            ],
        }
        result["scopes"].append(scope_result)
        if not missing:
            result["accepted_scopes"].append(sid)
    result["complete"] = len(result["accepted_scopes"]) == len(declared)
    result["reason"] = "全部已复核公开作用域通过七项条件" if result["complete"] else "仅部分或尚无公开作用域通过完整条件"
    return result


def status_text(result):
    if result["complete"]:
        return "已完成：显式证据已覆盖全部已复核公开作用域（" + "、".join(result["accepted_scopes"]) + "）的发行可用性、普通操作到结果、选项限制、素材、正文和网站"
    if not result["required_scopes"]:
        return "未完成：" + result["reason"]
    passed = "、".join(result["accepted_scopes"]) or "无"
    pending = "、".join(scope for scope in result["required_scopes"] if scope not in result["accepted_scopes"])
    return f"未完成：已验收作用域={passed}；待验收作用域={pending}；详见 guide-acceptance-evaluation.json"
