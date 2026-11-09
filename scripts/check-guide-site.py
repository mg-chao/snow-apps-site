"""Audit generated guide routes, sidebar links, anchors, assets and locale targets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'doc_build'
DOCS = [ROOT / 'docs/zh/guides', ROOT / 'docs/en/guides']

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = set()
        self.links = []
        self.assets = []
        self.headings = {}
        self.heading = None
        self.heading_id = None
        self.words = []
        self.alternates = []
        self.sidebar_links = set()
        self.in_sidebar = 0
        self.stack = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag == 'aside':
            self.stack.append(self.in_sidebar)
            self.in_sidebar = 1 if 'sidebar' in a.get('class', '') else self.in_sidebar
        if tag == 'a' and a.get('href'):
            self.links.append((a['href'], a))
            if self.in_sidebar: self.sidebar_links.add(a['href'])
        if tag == 'link' and a.get('rel') == 'alternate': self.alternates.append(a)
        if tag in ('img', 'source', 'video', 'script') and a.get('src'): self.assets.append(a['src'])
        if tag == 'link' and a.get('rel') == 'stylesheet': self.assets.append(a['href'])
        if re.fullmatch('h[1-6]', tag):
            self.heading, self.heading_id, self.words = tag, a.get('id'), []
    def handle_data(self, text):
        if self.heading: self.words.append(text)
    def handle_endtag(self, tag):
        if tag == 'aside' and self.stack: self.in_sidebar = self.stack.pop()
        if tag == self.heading:
            if self.heading_id: self.headings[''.join(self.words).strip().lstrip('#').strip()] = self.heading_id
            self.heading = None

cache = {}
def page(file):
    if file not in cache: cache[file] = Page(file.read_text())
    return cache[file]

def resolve(href, source):
    url = urlsplit(urljoin('https://snowshot.top/' + source.relative_to(BUILD).as_posix(), href))
    if url.netloc != 'snowshot.top' or url.scheme not in ('http', 'https'): return None, None
    target = BUILD / unquote(url.path).lstrip('/')
    if url.path.endswith('/'): target /= 'index.html'
    elif not target.suffix: target = target.with_suffix('.html')
    return target, unquote(url.fragment)

errors = []
files = sorted(p for directory in DOCS for p in directory.rglob('*') if p.suffix in ('.md', '.mdx'))
htmls = []
assets = set()
anchors = set()
for source in files:
    locale = 'en' if source.is_relative_to(ROOT / 'docs/en') else 'zh'
    relative = source.relative_to(ROOT / ('docs/en' if locale == 'en' else 'docs')).with_suffix('.html')
    target = BUILD / relative
    if not target.exists(): errors.append(f'Missing page: {target.relative_to(ROOT)}'); continue
    htmls.append(target)
    data = page(target)
    text = source.read_text()
    for field in ('title', 'description'):
        if not re.search(r'^'+field+r':\s*\S', text, re.M): errors.append(f'Missing {field}: {source.relative_to(ROOT)}')
    if not data.headings: errors.append(f'No headings: {source.relative_to(ROOT)}')
    if '<p>import {' in target.read_text(): errors.append(f'Literal component import: {source.relative_to(ROOT)}')
    if 'import { GuideSteps }' in text and 'snow-guide-steps' not in target.read_text():
        errors.append(f'Unrendered step demonstration: {source.relative_to(ROOT)}')
    for href, attrs in data.links:
        dest, anchor = resolve(href, target)
        if dest is None: continue
        if not dest.exists(): errors.append(f'Broken link {href} in {source.relative_to(ROOT)}'); continue
        if anchor and dest.suffix == '.html':
            anchors.add((dest, anchor))
            if anchor not in page(dest).ids: errors.append(f'Broken anchor {href} in {source.relative_to(ROOT)}')
    for src in data.assets:
        dest, _ = resolve(src, target)
        if dest is None: continue
        assets.add(dest)
        if not dest.exists(): errors.append(f'Missing asset {src} in {source.relative_to(ROOT)}')
    if source.name != 'index.md':
        expected = '/'+relative.as_posix()
        if expected not in data.sidebar_links: errors.append(f'Tutorial not in sidebar: {expected}')
    expected_language = '/' + (relative.as_posix().removeprefix('zh/') if locale == 'zh' else 'zh/' + relative.as_posix())
    language_links = [href for href, attrs in data.links if 'snow-guide-language' in attrs.get('class', '').split()]
    if language_links != [expected_language]: errors.append(f'Wrong corresponding language link: {relative}')
    counterpart, _ = resolve(expected_language, target)
    if not counterpart.is_file(): errors.append(f'Missing language counterpart: {expected_language}')
    alternates = {a.get('hreflang'): a.get('href') for a in data.alternates}
    english = '/' + relative.as_posix().removeprefix('zh/')
    for lang, path in [('en', english), ('zh', '/zh' + english)]:
        if alternates.get(lang) != 'https://snowshot.top' + path:
            errors.append(f'Wrong {lang} hreflang: {relative}')

# Check every frame, not just the first frame rendered by SSR.
for source in files:
    for src in set(re.findall(r'/images/guides/[A-Za-z0-9_./-]+\.(?:svg|png|webp)', source.read_text())):
        asset = BUILD / src.lstrip('/')
        assets.add(asset)
        if not asset.exists(): errors.append(f'Missing frame {src} in {source.relative_to(ROOT)}')
svgs = list((ROOT / 'docs/public/images/guides').rglob('*.svg'))
for svg in svgs:
    try: ET.parse(svg)
    except ET.ParseError as exc: errors.append(f'Invalid SVG {svg.name}: {exc}')
pngs = list((ROOT / 'docs/public/images/guides').rglob('*.png'))
for png in pngs:
    header = png.read_bytes()[:24]
    if (len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n'
            or header[12:16] != b'IHDR'
            or int.from_bytes(header[16:20], 'big') == 0
            or int.from_bytes(header[20:24], 'big') == 0):
        errors.append(f'Invalid PNG or mismatched file extension: {png.name}')
webps = list((ROOT / 'docs/public/images/guides').rglob('*.webp'))
for webp in webps:
    data = webp.read_bytes()
    if (len(data) < 25 or data[:4] != b'RIFF' or data[8:12] != b'WEBP'
            or int.from_bytes(data[4:8], 'little') != len(data) - 8
            or data[12:16] not in (b'VP8 ', b'VP8L', b'VP8X')):
        errors.append(f'Invalid WebP or mismatched file extension: {webp.name}')

for index in (BUILD / 'static').glob('search_index.*.json'):
    for item in json.loads(index.read_text()):
        path = item.get('routePath', '')
        if not re.match(r'^/(?:zh/)?guides(?:/|$)', path): continue
        if re.search(r'<(?:GuideSteps|GuideRecordingDemo|ArrowDemo)\b', item.get('content','')):
            errors.append(f'JSX leaked into search: {path}')

legacy = page(BUILD / 'zh/guides/index.html').ids
for anchor in ['snow-shot-截图与文本识别使用指南','安装并完成第一张截图','截取滚动长截图','使用离线文本识别提取文字','将资料贴到屏幕或录制操作演示','识别官方入口']:
    if anchor not in legacy: errors.append(f'Missing legacy guide anchor: {anchor}')

summary = {'pages':len(htmls),'standalone_tutorials':len(htmls)-len(DOCS),'pages_by_locale':{lang:sum(p.is_relative_to(ROOT/f'docs/{lang}') for p in files) for lang in ('zh','en')},'unique_assets_checked':len(assets),'svg_files':len(svgs),'png_files':len(pngs),'webp_files':len(webps),'unique_anchor_targets_checked':len(anchors),'errors':sorted(set(errors))}
(ROOT/'artifacts/guide-site-check.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
