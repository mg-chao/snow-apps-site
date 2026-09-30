"""Package and deploy only the Rspress-owned part of the Snow Shot web root."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile
import uuid


OWNED = frozenset({
    "index.html", "404.html", "about.html", "download.html",
    "app-icon.ico", "app-icon.svg", "static", "images", "zh",
    "website-release.json",
})
REQUIRED = {"index.html", "download.html", "zh/index.html", "zh/download.html"}
RECEIPT = "website-release.json"


def identity(version, commit):
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
                        r"(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?", version):
        raise ValueError("Expected a release semantic version")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Expected a website Git commit")


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def safe_path(name):
    path = PurePosixPath(name)
    if (path.is_absolute() or "\\" in name or not path.parts
            or any(part in {".", ".."} for part in name.split("/"))
            or path.parts[0] not in OWNED):
        raise ValueError(f"Not a website-owned path: {name}")
    return path


def inventory(directory):
    files = {}
    for path in sorted(directory.rglob("*")):
        name = path.relative_to(directory).as_posix()
        safe_path(name)
        if path.is_symlink() or path.is_mount():
            raise ValueError(f"Links and mounts are not allowed: {name}")
        if path.is_file() and name != RECEIPT:
            files[name] = {"size": path.stat().st_size, "sha256": digest(path)}
        elif not path.is_dir() and name != RECEIPT:
            raise ValueError(f"Not a regular file: {name}")
    if not REQUIRED.issubset(files) or not any(p.startswith("static/") for p in files):
        raise ValueError("Incomplete Rspress build")
    if any(files[name]["size"] == 0 for name in REQUIRED):
        raise ValueError("Empty website page")
    return files


def pack(build, archive, version, commit):
    identity(version, commit)
    files = inventory(build)
    receipt = {"schema": 1, "version": version, "commit": commit, "files": files}
    # The receipt is generated after the push and is not a source change.
    (build / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    with tarfile.open(archive, "w:gz") as bundle:
        for path in sorted(build.rglob("*")):
            bundle.add(path, arcname=path.relative_to(build).as_posix(), recursive=False)
    return receipt


def unpack(archive, stage):
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            path = safe_path(member.name)
            if member.name in seen or not (member.isfile() or member.isdir()):
                raise ValueError(f"Duplicate or nonregular archive entry: {member.name}")
            seen.add(member.name)
            destination = stage.joinpath(*path.parts)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, destination.open("xb") as target:
                    shutil.copyfileobj(source, target)
                destination.chmod(0o644)


def validate_root(root):
    if not root.is_absolute() or root.resolve() != root or not root.is_dir():
        raise ValueError("Web root must be an existing absolute directory without links")
    if root == Path(root.anchor) or not (root / "index.html").is_file():
        raise ValueError("Expected an existing Snow Shot website")
    if "Snow Shot" not in (root / "index.html").read_text(encoding="utf-8"):
        raise ValueError("Web root is not the Snow Shot website")
    for name in OWNED:
        target = root / name
        paths = [target, *target.rglob("*")] if target.is_dir() else [target]
        for path in paths:
            if path.is_symlink() or path.is_mount():
                raise ValueError(f"Refusing website path with a link or mount: {path}")


def deploy(root, archive, version, commit, sha256):
    identity(version, commit)
    validate_root(root)
    if digest(archive) != sha256:
        raise ValueError("Uploaded website archive checksum mismatch")
    backup_parent = root.parent / "snow-shot-website-backups"
    if backup_parent.is_symlink() or backup_parent.is_mount():
        raise ValueError("Backup directory must not be a link or mount")
    backup_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".snow-shot-website-stage-", dir=root.parent) as tmp:
        stage = Path(tmp)
        unpack(archive, stage)
        receipt = json.loads((stage / RECEIPT).read_text(encoding="utf-8"))
        if (receipt.get("schema") != 1 or receipt.get("version") != version
                or receipt.get("commit") != commit or receipt.get("files") != inventory(stage)):
            raise ValueError("Website receipt or file checksum mismatch")
        # Assets arrive before pages; the receipt is the final completion marker.
        names = sorted(p.name for p in stage.iterdir() if p.name != RECEIPT)
        names.sort(key=lambda name: (name not in {"static", "images"}, name))
        names.append(RECEIPT)
        backup = backup_parent / f"{version}-{commit[:12]}-{uuid.uuid4().hex}"
        backup.mkdir()
        moved = []
        installed = []
        try:
            for name in names:
                target = root / name
                if target.exists():
                    os.replace(target, backup / name)
                    moved.append(name)
                os.replace(stage / name, target)
                installed.append(name)
        except BaseException:
            for name in reversed(installed):
                os.replace(root / name, stage / name)
            for name in reversed(moved):
                os.replace(backup / name, root / name)
            raise
    return {"version": version, "commit": commit, "backup": str(backup), "replaced": names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation in ("pack", "deploy"):
        command = commands.add_parser(operation)
        command.add_argument("--archive", type=Path, required=True)
        command.add_argument("--version", required=True)
        command.add_argument("--commit", required=True)
        if operation == "pack":
            command.add_argument("--build", type=Path, required=True)
        else:
            command.add_argument("--web-root", type=Path, required=True)
            command.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if args.operation == "pack":
        result = pack(args.build, args.archive, args.version, args.commit)
        print(json.dumps({"version": result["version"], "commit": result["commit"],
                          "sha256": digest(args.archive)}))
    else:
        # Serialize deployments. The lock lives outside the shared public web root.
        import fcntl
        validate_root(args.web_root)
        lock_path = args.web_root.parent / ".snow-shot-website.lock"
        with lock_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            print(json.dumps(deploy(args.web_root, args.archive, args.version,
                                    args.commit, args.sha256)))


if __name__ == "__main__":
    main()
