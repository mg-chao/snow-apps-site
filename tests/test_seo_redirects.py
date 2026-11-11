"""Exercise the shipped Nginx rules in an isolated official Nginx container."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, build_opener
import uuid


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class RedirectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('docker'):
            raise unittest.SkipTest('Docker is required for real Nginx integration tests')
        cls.temp = tempfile.TemporaryDirectory(prefix='snow-seo-nginx-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name).resolve()
        cls.name = 'snow-seo-' + uuid.uuid4().hex[:12]
        cls.addClassCleanup(lambda: subprocess.run(['docker', 'rm', '-f', cls.name], capture_output=True))
        web = cls.root / 'html'
        for name in ('index.html', 'download.html', 'zh/download.html',
                     'guides/capture/scrolling.html', 'zh/guides/capture/scrolling.html',
                     'blog/ocr.html', 'zh/blog/ocr.html', 'api/example',
                     'images/example.svg', 'setup/installer.exe'):
            path = web / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Snow Shot fixture', encoding='utf-8')
        rules = Path(__file__).resolve().parents[1] / 'deploy/nginx-seo-redirects.conf'
        config = cls.root / 'default.conf'
        config.write_text('server { listen 80; server_name _; root /usr/share/nginx/html;\n'
                          'include /etc/nginx/seo.conf;\n'
                          'location / { try_files $uri $uri.html $uri/ =404; }\n}\n', encoding='utf-8')
        subprocess.run(['docker', 'run', '--detach', '--name', cls.name,
                        '-p', '127.0.0.1::80',
                        '--mount', f'type=bind,source={web},target=/usr/share/nginx/html,readonly',
                        '--mount', f'type=bind,source={config},target=/etc/nginx/conf.d/default.conf,readonly',
                        '--mount', f'type=bind,source={rules},target=/etc/nginx/seo.conf,readonly',
                        'nginx:stable-alpine'], check=True, capture_output=True)
        subprocess.run(['docker', 'exec', cls.name, 'nginx', '-t'], check=True, capture_output=True)
        info = json.loads(subprocess.check_output(['docker', 'inspect', cls.name], text=True))[0]
        port = info['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']
        cls.base = 'http://127.0.0.1:' + port
        cls.opener = build_opener(NoRedirect)
        for _ in range(30):
            try:
                cls.request('/index.html')
                break
            except URLError:
                time.sleep(0.1)
        else:
            raise RuntimeError('Test Nginx did not start')

    @classmethod
    def request(cls, path):
        try:
            response = cls.opener.open(cls.base + path, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.headers.get('Location'), response.read()

    def test_existing_document_aliases_redirect_once_and_preserve_parameters(self):
        for prefix in ('', '/zh'):
            for document in ('/guides/capture/scrolling', '/blog/ocr'):
                canonical = prefix + document + '.html'
                for suffix in ('', '/'):
                    with self.subTest(path=prefix + document + suffix):
                        status, location, _ = self.request(prefix + document + suffix + '?os=macos&arch=arm64')
                        self.assertEqual(status, 301)
                        self.assertEqual(location, 'https://snowshot.top' + canonical + '?os=macos&arch=arm64')
                        self.assertEqual(self.request(canonical)[0], 200)

    def test_missing_docs_stay_404_and_services_and_assets_are_untouched(self):
        for path in ('/guides/missing', '/zh/blog/missing/', '/blog/missing.html'):
            self.assertEqual(self.request(path)[0], 404, path)
        for path in ('/api/example', '/images/example.svg', '/setup/installer.exe'):
            self.assertEqual(self.request(path)[0], 200, path)

    def test_download_alias_retains_user_choices(self):
        for prefix in ('', '/zh'):
            status, location, _ = self.request(prefix + '/download?os=macos&arch=x64')
            self.assertEqual(status, 301)
            self.assertEqual(location, 'https://snowshot.top' + prefix + '/download.html?os=macos&arch=x64')


if __name__ == '__main__':
    unittest.main()
