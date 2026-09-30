import importlib.util
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "website", Path(__file__).resolve().parents[1] / "scripts/deploy-website.py")
website = importlib.util.module_from_spec(spec)
spec.loader.exec_module(website)
VERSION = "1.1.8"
COMMIT = "a" * 40


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="snow-website-tests-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.build = self.base / "build"
        self.root = self.base / "html"
        self.build.mkdir()
        self.root.mkdir()
        for name in website.REQUIRED | {"static/js/app.js", "images/en/app.png"}:
            target = self.build / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"Snow Shot {VERSION}: {name}", encoding="utf-8")
        (self.root / "index.html").write_text("Snow Shot old homepage", encoding="utf-8")
        (self.root / "static").mkdir()
        (self.root / "static/obsolete.js").write_text("old asset", encoding="utf-8")
        self.protected = {}
        for name in ("setup/installer.exe", "npm/package.js", "plugins/plugin.dll",
                     "ocr/model.onnx", "api/data.json", ".well-known/acme/token",
                     "latest-version.json", "latest-version.txt", "operator.txt"):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(f"preserve {name}".encode())
            self.protected[name] = target.read_bytes()
        self.archive = self.base / "website.tar.gz"

    def package(self):
        website.pack(self.build, self.archive, VERSION, COMMIT)
        return website.digest(self.archive)

    def publish(self, checksum=None):
        return website.deploy(self.root, self.archive, VERSION, COMMIT,
                              checksum or website.digest(self.archive))

    def assert_preserved(self):
        for name, content in self.protected.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)

    def test_deployment_preserves_nonwebsite_paths_and_backs_up_old_site(self):
        checksum = self.package()
        result = self.publish(checksum)
        self.assert_preserved()
        self.assertFalse((self.root / "static/obsolete.js").exists())
        backup = Path(result["backup"])
        self.assertEqual((backup / "static/obsolete.js").read_text(), "old asset")
        self.assertEqual((backup / "index.html").read_text(), "Snow Shot old homepage")
        receipt = json.loads((self.root / website.RECEIPT).read_text())
        self.assertEqual(receipt["version"], VERSION)
        self.assertEqual(receipt["commit"], COMMIT)
        for name, entry in receipt["files"].items():
            self.assertEqual(entry["sha256"], website.digest(self.root / name))

    def test_repeated_deployment_retains_previous_website(self):
        self.package()
        first = self.publish()
        second = self.publish()
        self.assertNotEqual(first["backup"], second["backup"])
        self.assertTrue((Path(second["backup"]) / website.RECEIPT).is_file())
        self.assert_preserved()

    def test_rejects_archive_corruption_before_replacement(self):
        self.package()
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.publish("0" * 64)
        self.assertEqual((self.root / "index.html").read_text(), "Snow Shot old homepage")
        self.assert_preserved()

    def test_rejects_mismatched_receipt_before_replacement(self):
        self.package()
        with self.assertRaisesRegex(ValueError, "receipt"):
            website.deploy(self.root, self.archive, "1.1.9", COMMIT, website.digest(self.archive))
        self.assert_preserved()

    def test_rejects_changed_file_even_with_valid_archive_checksum(self):
        self.package()
        (self.build / "download.html").write_text("changed", encoding="utf-8")
        with tarfile.open(self.archive, "w:gz") as bundle:
            for target in self.build.rglob("*"):
                bundle.add(target, arcname=target.relative_to(self.build).as_posix(), recursive=False)
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.publish()
        self.assert_preserved()

    def test_rejects_unsafe_archive_entries(self):
        for name, entry_type in (("../outside", tarfile.REGTYPE),
                                 ("/index.html", tarfile.REGTYPE),
                                 ("setup/installer.exe", tarfile.REGTYPE),
                                 ("static/link", tarfile.SYMTYPE),
                                 ("static/hardlink", tarfile.LNKTYPE)):
            with self.subTest(name=name):
                with tarfile.open(self.archive, "w:gz") as bundle:
                    member = tarfile.TarInfo(name)
                    member.type = entry_type
                    member.linkname = "../outside"
                    bundle.addfile(member, io.BytesIO(b""))
                with self.assertRaises(ValueError):
                    self.publish()
                self.assert_preserved()

    def test_rejects_protected_build_paths(self):
        (self.build / "latest-version.json").write_text("do not overwrite", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "owned"):
            self.package()

    def test_rejects_incomplete_build(self):
        (self.build / "zh/download.html").unlink()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.package()

    def test_rejects_symlink_destination(self):
        self.package()
        (self.root / "images").mkdir()
        # Windows may not grant symlink privileges; exercise the same guard through lstat.
        original = Path.is_symlink
        with patch.object(Path, "is_symlink", lambda path: path == self.root / "images" or original(path)):
            with self.assertRaisesRegex(ValueError, "link"):
                self.publish()
        self.assert_preserved()

    def test_rolls_back_replacement_failure(self):
        self.package()
        replace = os.replace

        def fail_homepage(source, target):
            if Path(source).parent.name.startswith(".snow-shot-website-stage-") and Path(target) == self.root / "index.html":
                raise OSError("injected replacement failure")
            return replace(source, target)

        with patch.object(website.os, "replace", side_effect=fail_homepage):
            with self.assertRaisesRegex(OSError, "injected"):
                self.publish()
        self.assertEqual((self.root / "index.html").read_text(), "Snow Shot old homepage")
        self.assertTrue((self.root / "static/obsolete.js").is_file())
        self.assertFalse((self.root / "download.html").exists())
        self.assert_preserved()


if __name__ == "__main__":
    unittest.main()
