"""Release installer parity checks without networking or executing downloaded code."""

import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError


spec = importlib.util.spec_from_file_location(
    "website", Path(__file__).resolve().parents[1] / "scripts/deploy-website.py")
website = importlib.util.module_from_spec(spec)
spec.loader.exec_module(website)
VERSION = "1.2.3"
SCRIPT = b"#!/bin/bash\nset -Eeuo pipefail\nprintf '%s\\n' 'Snow Shot installer'\n"
URLS = [
    f"https://{host}/mg-chao/snow-apps/releases/download/"
    f"v{VERSION}_snow-shot/install-snow-shot-macos.sh"
    for host in ("github.com", "gitee.com")
]


class ReleaseInstallerTests(unittest.TestCase):
    def check(self, contents):
        opener = Mock()
        opener.open.side_effect = [
            content if isinstance(content, Exception) else io.BytesIO(content)
            for content in contents
        ]
        with patch.object(website, "build_opener", return_value=opener):
            result = website.validate_release_installer(VERSION)
        return result, opener

    def test_matching_release_scripts_are_verified_without_execution(self):
        result, opener = self.check([SCRIPT, SCRIPT])
        self.assertEqual(result, {
            "version": VERSION, "sha256": hashlib.sha256(SCRIPT).hexdigest(),
            "bytes": len(SCRIPT),
        })
        self.assertEqual([call.args[0] for call in opener.open.call_args_list], URLS)
        self.assertTrue(all(call.kwargs["timeout"] == 30
                            for call in opener.open.call_args_list))

    def test_different_channel_scripts_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "differ"):
            self.check([SCRIPT, SCRIPT + b"# stale mirror\n"])

    def test_missing_or_unreachable_installer_is_rejected_on_either_channel(self):
        for index, url in enumerate(URLS):
            for error in (HTTPError(url, 404, "Not Found", None, None),
                          URLError("unreachable"), TimeoutError("timeout")):
                with self.subTest(channel=url, error=type(error).__name__):
                    contents = [SCRIPT, SCRIPT]
                    contents[index] = error
                    with self.assertRaisesRegex(ValueError, "Cannot download.*installer"):
                        self.check(contents)

    def test_invalid_bash_assets_are_rejected_on_either_channel(self):
        for index in range(2):
            for invalid in (b"", b"<html>Not Found</html>",
                            SCRIPT.replace(b"\n", b"\r\n"),
                            b"\xef\xbb\xbf" + SCRIPT, SCRIPT + b"\xff\n"):
                with self.subTest(channel=URLS[index], invalid=invalid[:30]):
                    contents = [SCRIPT, SCRIPT]
                    contents[index] = invalid
                    with self.assertRaisesRegex(ValueError, "Invalid.*installer"):
                        self.check(contents)

    def test_oversized_assets_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid.*installer"):
            self.check([SCRIPT + b"x" * 1048576, SCRIPT])

    def test_invalid_versions_never_make_network_requests(self):
        for version in ("../1.2.3", "01.2.3", "1.2", "1.2.3?bad"):
            with self.subTest(version=version), patch.object(website, "build_opener") as opener:
                with self.assertRaisesRegex(ValueError, "semantic version"):
                    website.validate_release_installer(version)
                opener.assert_not_called()

    def test_redirects_cannot_downgrade_the_install_command_to_http(self):
        handler = website.InstallerRedirectHandler()
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            handler.redirect_request(Mock(), None, 302, "Found", {},
                                     "http://example.com/installer.sh")

    def test_cli_reports_the_verified_release_digest(self):
        opener = Mock()
        opener.open.side_effect = [io.BytesIO(SCRIPT), io.BytesIO(SCRIPT)]
        output = io.StringIO()
        with patch.object(website, "build_opener", return_value=opener), \
                patch.object(website.sys, "argv", ["deploy-website.py", "check-release-installer",
                                                  "--version", VERSION]), \
                redirect_stdout(output):
            website.main()
        self.assertEqual(json.loads(output.getvalue())["sha256"],
                         hashlib.sha256(SCRIPT).hexdigest())

    def test_cli_fails_with_an_actionable_download_diagnostic(self):
        opener = Mock()
        opener.open.side_effect = URLError("unreachable")
        output = io.StringIO()
        with patch.object(website, "build_opener", return_value=opener), \
                patch.object(website.sys, "argv", ["deploy-website.py", "check-release-installer",
                                                  "--version", VERSION]), \
                redirect_stderr(output), self.assertRaises(SystemExit) as failure:
            website.main()
        self.assertEqual(failure.exception.code, 1)
        self.assertIn(URLS[0], output.getvalue())
        self.assertIn("unreachable", output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())


if __name__ == "__main__":
    unittest.main()
