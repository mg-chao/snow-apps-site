"""Package and deploy only the Rspress-owned part of the Snow Shot web root."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler
import uuid


OWNED = frozenset({
    "index.html", "404.html", "about.html", "download.html",
    "app-icon.ico", "app-icon.svg", "static", "images", "zh",
    "website-release.json",
})
REQUIRED = {"index.html", "download.html", "zh/index.html", "zh/download.html"}
RECEIPT = "website-release.json"
INSTALLER_SIZE_LIMIT = 1048576


class InstallerRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme != "https":
            raise ValueError("Installer redirects must stay on HTTPS")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def validate_release_installer(version):
    """Verify the exact installer asset used by both website languages."""
    validate_version(version)
    opener = build_opener(InstallerRedirectHandler())
    scripts = []
    for host in ("github.com", "gitee.com"):
        url = (f"https://{host}/mg-chao/snow-apps/releases/download/"
               f"v{version}_snow-shot/install-snow-shot-macos.sh")
        try:
            with opener.open(url, timeout=30) as response:
                script = response.read(INSTALLER_SIZE_LIMIT + 1)
        except (URLError, OSError, ValueError) as error:
            raise ValueError(f"Cannot download release installer: {url} ({error})") from error
        try:
            script.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"Invalid UTF-8 release installer: {url}") from error
        if (len(script) > INSTALLER_SIZE_LIMIT or not script.startswith(b"#!/bin/bash\n")
                or b"\r" in script):
            raise ValueError(f"Invalid Bash release installer: {url}")
        scripts.append(script)
    if scripts[0] != scripts[1]:
        raise ValueError(f"GitHub and Gitee release installers differ for {version}")
    return {"version": version, "sha256": hashlib.sha256(scripts[0]).hexdigest(),
            "bytes": len(scripts[0])}


class DownloadLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.update(value for name, value in attrs if name == "href")


def validate_download_page(html, version, locale):
    """Check the default Windows cards rendered in each public download page."""
    repository = "gitee.com" if locale == "zh" else "github.com"
    base = f"https://{repository}/mg-chao/snow-apps/releases/download/v{version}_snow-shot"
    assets = (
        f"snow-shot-{version}-windows-x64-online.exe",
        f"snow-shot-{version}-windows-x64-offline.exe",
        f"snow-shot-{version}-windows-x64-portable.zip",
        f"snow-shot-mini-{version}-windows-x64-online.exe",
        f"snow-shot-mini-{version}-windows-x64-portable.zip",
    )
    parser = DownloadLinks()
    parser.feed(html)
    missing = [asset for asset in assets if f"{base}/{asset}" not in parser.links]
    if missing:
        raise ValueError(f"Missing {locale} release download links: {', '.join(missing)}")


def validate_downloads(directory, version):
    for locale, name in (("en", "download.html"), ("zh", "zh/download.html")):
        validate_download_page((directory / name).read_text(encoding="utf-8"), version, locale)


def validate_version(version):
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
                        r"(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?", version):
        raise ValueError("Expected a release semantic version")


def identity(version, commit):
    validate_version(version)
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
    validate_downloads(build, version)
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
        validate_downloads(stage, version)
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
    check = commands.add_parser("check-downloads")
    check.add_argument("--version", required=True)
    check.add_argument("--locale", choices=("en", "zh"), required=True)
    installer = commands.add_parser("check-release-installer")
    installer.add_argument("--version", required=True)
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
    elif args.operation == "check-downloads":
        validate_download_page(sys.stdin.buffer.read().decode("utf-8"), args.version, args.locale)
        print(f"Verified {args.locale} Snow Shot and Snow Shot Mini downloads for {args.version}")
    elif args.operation == "check-release-installer":
        try:
            print(json.dumps(validate_release_installer(args.version)))
        except ValueError as error:
            parser.exit(1, f"{error}\n")
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
