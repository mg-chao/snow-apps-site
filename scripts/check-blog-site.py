"""Check rendered bilingual blog discovery, media, links and metadata after build."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'doc_build'
ORIGIN = 'https://snowshot.top'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.images = []
        self.links = []
        self.ids = set()
        self.cards = 0
        self.categories = 0
        self.language_links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'img':
            self.images.append(a)
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
            if 'snow-guide-language' in a.get('class', '').split():
                self.language_links.append(a['href'])
        if tag == 'article' and 'snow-blog-card' in a.get('class', '').split():
            self.cards += 1
        if tag == 'button' and a.get('aria-pressed') in ('true', 'false'):
            self.categories += 1


def destination(href, source):
    url = urlsplit(urljoin(ORIGIN + '/' + source, href))
    if url.netloc != 'snowshot.top' or url.scheme != 'https':
        return None, None
    name = unquote(url.path).lstrip('/')
    if name.endswith('/'):
        name += 'index.html'
    elif not Path(name).suffix:
        name += '.html'
    return BUILD / name, unquote(url.fragment)


def check():
    sources = {lang: sorted((ROOT / 'docs' / lang / 'blog').glob('*.mdx')) for lang in ('en', 'zh')}
    assert [p.name for p in sources['en']] == [p.name for p in sources['zh']], 'Blog locale counterparts differ'
    slugs = {p.stem for p in sources['en'] if p.stem != 'index'}
    assert len(slugs) >= 10, 'The first ten independent topics are incomplete'
    sitemap = (BUILD / 'sitemap.xml').read_text()
    search_files = list(BUILD.rglob('search_index.*.json'))
    assert search_files, 'Missing generated search index'
    search_routes = {page['routePath'] for p in search_files for page in json.loads(p.read_text())}
    rows = []
    for lang, files in sources.items():
        prefix = 'zh/' if lang == 'zh' else ''
        home = prefix + 'blog/index.html'
        listing_text = (BUILD / home).read_text()
        listing = Page(listing_text)
        assert listing.cards == len(slugs), f'{home}: articles absent from static HTML'
        assert listing.categories == 3, f'{home}: category controls missing'
        for source in files:
            name = prefix + 'blog/' + source.with_suffix('.html').name
            target = BUILD / name
            assert target.is_file(), f'Missing {name}'
            text = target.read_text()
            page = Page(text)
            assert ORIGIN + '/' + name in sitemap, f'{name}: absent from sitemap'
            alternate = '/' + (name.removeprefix('zh/') if lang == 'zh' else 'zh/' + name)
            assert page.language_links == [alternate], f'{name}: wrong language switch'
            for href in page.links:
                dest, anchor = destination(href, name)
                if dest is None:
                    continue
                assert dest.is_file(), f'{name}: broken link {href}'
                if anchor and dest.suffix == '.html':
                    assert anchor in Page(dest.read_text()).ids, f'{name}: broken anchor {href}'
            if source.stem == 'index':
                continue
            assert '/' + name in listing.links, f'{name}: absent from list links'
            assert '/' + name in search_routes, f'{name}: missing canonical search-index route'
            for field in ('title', 'description', 'date', 'category', 'productVersion', 'platforms', 'related'):
                assert re.search(r'^' + field + r':\s*\S', source.read_text(), re.M), f'{source}: missing {field}'
            images = [a for a in page.images if a.get('src', '').startswith('/images/')]
            assert len(images) >= 3, f'{name}: fewer than three instructional images'
            assert any(a['src'].endswith('.webp') for a in images), f'{name}: missing app capture or output'
            for a in images:
                assert len(a.get('alt', '').strip()) >= 8, f'{name}: missing descriptive alt'
                assert (BUILD / a['src'].lstrip('/')).is_file(), f'{name}: broken image {a["src"]}'
            assert text.count('snow-blog-related') > 0, f'{name}: missing related articles'
            assert '<p>import ' not in text, f'{name}: literal import'
            rows.append({'path': name, 'images': len(images), 'language': lang})
    print(json.dumps({'articles_checked': len(rows), 'topics': len(slugs), 'pages': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    check()
