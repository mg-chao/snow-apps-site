"""Validate the actual generated HTML and discovery files before deployment."""

from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ORIGIN = 'https://snowshot.top'
REPOSITORY = 'https://github.com/mg-chao/snow-shot'


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.meta = {}
        self.scripts = []
        self.h1 = ''
        self.in_h1 = False
        self.in_json = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'link':
            self.links.append(values)
        if tag == 'meta':
            self.meta[values.get('name', values.get('property'))] = values.get('content')
        if tag == 'h1':
            self.in_h1 = True
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_json = True
            self.scripts.append('')

    def handle_data(self, data):
        if self.in_h1:
            self.h1 += data
        if self.in_json:
            self.scripts[-1] += data

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'script':
            self.in_json = False


def check(directory):
    pages = {path.relative_to(directory).as_posix(): Page(path.read_text(encoding='utf-8'))
             for path in directory.rglob('*.html')}
    expected = set()
    for name, page in pages.items():
        canonical = [link['href'] for link in page.links if link.get('rel') == 'canonical']
        if name == '404.html':
            assert page.meta.get('robots') == 'noindex' and not canonical, '404 must not be indexed'
            continue
        url = f'{ORIGIN}/{name}'
        expected.add(url)
        assert canonical == [url], f'{name}: expected exactly one self-canonical'
        assert page.meta.get('description'), f'{name}: missing description'
        assert page.meta.get('og:url') == url, f'{name}: incorrect social URL'
        english = name.removeprefix('zh/')
        assert english in pages and f'zh/{english}' in pages, f'{name}: missing language counterpart'
        alternates = {link.get('hreflang'): link.get('href') for link in page.links
                      if link.get('rel') == 'alternate'}
        assert alternates == {'en': f'{ORIGIN}/{english}',
                              'zh': f'{ORIGIN}/zh/{english}',
                              'x-default': f'{ORIGIN}/{english}'}, f'{name}: incorrect language links'
        if name in ('index.html', 'zh/index.html'):
            assert len(page.scripts) == 1, f'{name}: missing application schema'
            data = json.loads(page.scripts[0])
            assert data['sameAs'] == REPOSITORY and data['downloadUrl'] == f'{REPOSITORY}/releases/latest'
            assert data['url'] == url and data['offers']['price'] == '0'
            assert ('开源' in page.h1 and '截图' in page.h1) if name.startswith('zh/') else (
                'open-source' in page.h1 and 'screenshot' in page.h1)
    root = ET.fromstring((directory / 'sitemap.xml').read_text(encoding='utf-8'))
    urls = [element.text for element in root.findall('{*}url/{*}loc')]
    assert set(urls) == expected and len(urls) == len(expected), 'Sitemap must contain exactly the canonical pages'
    robots = (directory / 'robots.txt').read_text(encoding='utf-8')
    assert f'Sitemap: {ORIGIN}/sitemap.xml' in robots and 'Disallow: /' not in robots
    print(f'Verified {len(expected)} canonical pages, bilingual metadata, homepage schema and discovery files.')


if __name__ == '__main__':
    check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'doc_build')
