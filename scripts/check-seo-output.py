"""Validate the actual generated HTML and discovery files before deployment."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ORIGIN = 'https://snowshot.top'
REPOSITORY = 'https://github.com/mg-chao/snow-shot'


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.meta = {}
        self.scripts = []
        self.h1 = ''
        self.h1_count = 0
        self.title = ''
        self.in_title = False
        self.anchors = []
        self.breadcrumbs = []
        self.in_breadcrumbs = False
        self.crumb_tag = None
        self.in_h1 = False
        self.in_json = False
        self.top_count = 0
        self.site_headers = 0
        self.site_footers = 0
        self.header_links = []
        self.footer_links = []
        self.language_switches = []
        self.images = []
        self.times = []
        self.in_site_header = False
        self.in_site_footer = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        classes = values.get('class', '').split()
        if tag == 'img':
            self.images.append(values)
        if tag == 'time':
            self.times.append(values.get('datetime'))
        if values.get('id') == 'top':
            self.top_count += 1
        if tag == 'header' and 'snow-site-header' in classes:
            self.site_headers += 1
            self.in_site_header = True
        if tag == 'footer' and 'snow-global-footer' in classes:
            self.site_footers += 1
            self.in_site_footer = True
        if tag == 'a' and self.in_site_header:
            self.header_links.append(values.get('href'))
            if 'snow-site-language' in classes:
                self.language_switches.append(values)
        if tag == 'a' and self.in_site_footer:
            self.footer_links.append(values.get('href'))
        if tag == 'link':
            self.links.append(values)
        if tag == 'meta':
            self.meta[values.get('name', values.get('property'))] = values.get('content')
        if tag == 'h1':
            self.in_h1 = True
            self.h1_count += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'a' and values.get('href'):
            self.anchors.append(values['href'])
        if tag == 'nav' and 'snow-breadcrumbs' in values.get('class', '').split():
            self.in_breadcrumbs = True
        if self.in_breadcrumbs and (tag == 'a' or values.get('aria-current') == 'page'):
            self.breadcrumbs.append({'href': values.get('href'), 'label': ''})
            self.crumb_tag = tag
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_json = True
            self.scripts.append('')

    def handle_data(self, data):
        if self.in_h1:
            self.h1 += data
        if self.in_json:
            self.scripts[-1] += data
        if self.in_title:
            self.title += data
        if self.crumb_tag:
            self.breadcrumbs[-1]['label'] += data

    def handle_endtag(self, tag):
        if tag == 'header':
            self.in_site_header = False
        if tag == 'footer':
            self.in_site_footer = False
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'script':
            self.in_json = False
        if tag == 'title':
            self.in_title = False
        if tag == self.crumb_tag:
            self.crumb_tag = None
        if tag == 'nav':
            self.in_breadcrumbs = False


def linked_page(href, source):
    url = urlsplit(urljoin(f'{ORIGIN}/{source}', href))
    if url.scheme != 'https' or url.netloc != 'snowshot.top':
        return None
    name = url.path.lstrip('/')
    if not name or name.endswith('/'):
        name += 'index.html'
    elif not Path(name).suffix:
        name += '.html'
    return name if name.endswith('.html') else None


def check_llms(directory, canonical_urls):
    locale_links = []
    for prefix, alternate in (('', '/zh/llms.txt'), ('zh/', '/llms.txt')):
        name = f'{prefix}llms.txt'
        lines = (directory / name).read_text(encoding='utf-8').splitlines()
        assert lines[0] == '# Snow Shot' and lines[2].startswith('> '), f'{name}: missing title or summary'
        assert '## Optional' in lines, f'{name}: missing Optional section'
        links = set()
        for line in lines:
            if not line.startswith('- '):
                continue
            match = re.fullmatch(r'- \[[^\]]+\]\((https://[^\s)]+)\): \S.*', line)
            assert match, f'{name}: invalid link entry {line}'
            url = match[1]
            assert url not in links, f'{name}: duplicate link {url}'
            links.add(url)
            if not url.startswith(f'{ORIGIN}/'):
                continue
            path = urlsplit(url).path
            assert not re.fullmatch(r'/(?:zh/)?pricing(?:\.html|\.md|/)?', path), f'{name}: unexpected link {url}'
            target = directory / path.lstrip('/')
            assert target.is_file() and target.stat().st_size, f'{name}: missing target {url}'
            if path == alternate:
                continue
            assert path.startswith('/zh/') == bool(prefix), f'{name}: wrong language for {url}'
            if path.endswith('.md'):
                assert url.removesuffix('.md') + '.html' in canonical_urls, f'{name}: no canonical page for {url}'
            elif path.endswith('.html'):
                assert url in canonical_urls, f'{name}: noncanonical page {url}'
        required = {f'{ORIGIN}/{prefix}{target}' for target in (
            'download.html', 'guides/index.md', 'guides/getting-started/install.md', 'llms-full.txt')}
        assert required | {ORIGIN + alternate} <= links, f'{name}: missing a key resource or alternate language'
        locale_links.append({url.removeprefix(f'{ORIGIN}/{prefix}')
                             for url in links - {ORIGIN + alternate}})
    assert locale_links[0] == locale_links[1], 'llms.txt indexes must link to equivalent resources'


def check(directory):
    pages = {path.relative_to(directory).as_posix(): Page(path.read_text(encoding='utf-8'))
             for path in directory.rglob('*.html')}
    expected = set()
    for name, page in pages.items():
        canonical = [link['href'] for link in page.links if link.get('rel') == 'canonical']
        if name.removeprefix('zh/') == '404.html':
            assert page.meta.get('robots') == 'noindex' and not canonical, '404 must not be indexed'
            continue
        url = f'{ORIGIN}/{name}'
        expected.add(url)
        assert canonical == [url], f'{name}: expected exactly one self-canonical'
        assert page.meta.get('description'), f'{name}: missing description'
        assert page.title.strip(), f'{name}: missing page title'
        assert page.h1_count == 1, f'{name}: expected one main heading, got {page.h1_count}'
        assert page.meta.get('og:url') == url, f'{name}: incorrect social URL'
        english = name.removeprefix('zh/')
        assert english in pages and f'zh/{english}' in pages, f'{name}: missing language counterpart'
        prefix = '/zh' if name.startswith('zh/') else ''
        assert page.site_headers == page.site_footers == page.top_count == 1, f'{name}: expected one shared header, footer and top anchor'
        target_language = 'en' if prefix else 'zh'
        target_href = f'/{english}' if prefix else f'/zh/{english}'
        assert len(page.language_switches) == 1, f'{name}: expected one visible language switch'
        switch = page.language_switches[0]
        assert switch.get('href') == target_href and switch.get('hreflang') == target_language, f'{name}: language switch must keep the current page'
        for target in ('guides/index.html', 'download.html', 'blog/index.html', 'changelog.html', 'about.html'):
            assert page.header_links.count(f'{prefix}/{target}') == 2, f'{name}: desktop and mobile navigation differ for {target}'
        locale_home = f'{prefix}/index.html'.lstrip('/')
        assert page.footer_links == pages[locale_home].footer_links, f'{name}: footer differs from the locale homepage'
        alternates = {link.get('hreflang'): link.get('href') for link in page.links
                      if link.get('rel') == 'alternate'}
        assert alternates == {'en': f'{ORIGIN}/{english}',
                              'zh': f'{ORIGIN}/zh/{english}',
                              'x-default': f'{ORIGIN}/{english}'}, f'{name}: incorrect language links'
        if english.startswith('blog/') and english != 'blog/index.html':
            data = json.loads(page.scripts[0])
            items = data['itemListElement']
            blog_home = 'zh/blog/index.html' if name.startswith('zh/') else 'blog/index.html'
            assert len(items) == 3 and items[1]['item'] == f'{ORIGIN}/{blog_home}', f'{name}: blog parent missing'
        if name in ('index.html', 'zh/index.html'):
            schemas = {data['@type']: data for data in map(json.loads, page.scripts)}
            assert len(page.scripts) == 2 and set(schemas) == {'SoftwareApplication', 'WebSite'}, f'{name}: missing homepage schemas'
            data = schemas['SoftwareApplication']
            assert data['sameAs'] == REPOSITORY and data['downloadUrl'] == f'{REPOSITORY}/releases/latest'
            assert data['url'] == url and data['offers']['price'] == '0'
            website = schemas['WebSite']
            assert website['url'] == f'{ORIGIN}/' and website['name'] == 'Snow Shot'
            assert website['alternateName'] == 'SnowShot'
            assert ('开源' in page.h1 and '截图' in page.h1) if name.startswith('zh/') else (
                'open-source' in page.h1 and 'screenshot' in page.h1)
            assert not page.breadcrumbs, f'{name}: homepage should not have breadcrumbs'
        else:
            is_article = english.startswith('blog/') and english != 'blog/index.html'
            assert len(page.scripts) == (2 if is_article else 1), f'{name}: incorrect schema count'
            data = json.loads(page.scripts[0])
            assert data['@type'] == 'BreadcrumbList', f'{name}: missing breadcrumb schema'
            items = data['itemListElement']
            assert len(items) == len(page.breadcrumbs) >= 2, f'{name}: missing visible breadcrumbs'
            for position, (item, visible) in enumerate(zip(items, page.breadcrumbs), 1):
                assert item['position'] == position and item['name'] == visible['label'], f'{name}: breadcrumb differs from visible navigation'
                assert item['item'] == (urljoin(url, visible['href']) if visible['href'] else url), f'{name}: incorrect breadcrumb URL'
            assert items[-1]['item'] == url and page.breadcrumbs[-1]['href'] is None, f'{name}: incorrect current breadcrumb'
            guide_home = 'zh/guides/index.html' if name.startswith('zh/') else 'guides/index.html'
            if '/guides/' in f'/{name}' and name != guide_home:
                assert len(items) == 3 and items[1]['item'] == f'{ORIGIN}/{guide_home}', f'{name}: guide must have its manual as a parent'
            if is_article:
                article = json.loads(page.scripts[1])
                assert article['@type'] == 'BlogPosting' and article['mainEntityOfPage'] == url
                assert article['headline'] == page.h1.lstrip('#').strip(), f'{name}: article title differs from H1'
                assert article['author']['name'] == 'Snow Apps' and article['author']['url'] in page.anchors
                assert article['datePublished'] in page.times, f'{name}: publication date must be visible'
                assert article.get('dateModified'), f'{name}: missing modification date'
                assert datetime.fromisoformat(article['dateModified'].replace('Z', '+00:00')).date() >= datetime.fromisoformat(article['datePublished']).date()
                assert article['image'] == page.meta['og:image']
                images = [img for img in page.images if img.get('src', '').startswith('/images/')]
                assert article['image'] == ORIGIN + images[0]['src'], f'{name}: use an article illustration'
                for index, img in enumerate(images):
                    assert int(img.get('width', '0')) > 0 and int(img.get('height', '0')) > 0, f'{name}: missing image dimensions'
                    assert img.get('loading') == ('eager' if index == 0 else 'lazy'), f'{name}: incorrect image loading'
    # Audit rendered links, so client-only navigation cannot hide orphaned pages.
    graph = {}
    for name, page in pages.items():
        if f'{ORIGIN}/{name}' not in expected:
            continue
        graph[name] = set()
        for href in page.anchors:
            target = linked_page(href, name)
            if target is None:
                continue
            assert target in pages, f'{name}: broken internal link {href}'
            graph[name].add(target)
    for prefix in ('', 'zh/'):
        home = f'{prefix}index.html'
        for target in ('download.html', 'guides/index.html', 'guides/getting-started/install.html',
                       'guides/settings/shortcuts.html', 'blog/index.html', 'changelog.html', 'about.html'):
            assert f'{prefix}{target}' in graph[home], f'{home}: missing direct link to {target}'
        visited, pending = set(), [home]
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(graph.get(current, set()) - visited)
        locale_pages = {name for name in graph if name.startswith('zh/') == bool(prefix)}
        assert locale_pages <= visited, f'{home}: orphaned pages {sorted(locale_pages - visited)}'
    root = ET.fromstring((directory / 'sitemap.xml').read_text(encoding='utf-8'))
    urls = [element.text for element in root.findall('{*}url/{*}loc')]
    assert set(urls) == expected and len(urls) == len(expected), 'Sitemap must contain exactly the canonical pages'
    for element in root.findall('{*}url'):
        value = element.findtext('{*}lastmod')
        assert value, f'{element.findtext("{*}loc")}: missing lastmod'
        assert datetime.fromisoformat(value.replace('Z', '+00:00')) <= datetime.now(timezone.utc), 'Future lastmod'
    manifest = json.loads((directory / 'seo-manifest.json').read_text(encoding='utf-8'))
    assert manifest['schema'] == 1 and set(manifest['pages']) == expected, 'SEO manifest must match sitemap'
    for element in root.findall('{*}url'):
        url = element.findtext('{*}loc')
        entry = manifest['pages'][url]
        lastmod = element.findtext('{*}lastmod')
        assert entry['lastmod'] == lastmod, f'{url}: lastmod differs from manifest'
        path = urlsplit(url).path.lstrip('/')
        if path.removeprefix('zh/').startswith('blog/'):
            assert len(entry.get('contentHash', '')) == 64, f'{url}: missing blog content fingerprint'
        page = pages[path]
        for schema in map(json.loads, page.scripts):
            if schema['@type'] == 'BlogPosting':
                assert schema.get('dateModified') == lastmod, f'{url}: article date differs from sitemap'
                assert page.meta.get('article:modified_time') == lastmod, f'{url}: social date differs from sitemap'
    robots = (directory / 'robots.txt').read_text(encoding='utf-8')
    assert f'Sitemap: {ORIGIN}/sitemap.xml' in robots and 'Disallow: /' not in robots
    check_llms(directory, expected)
    print(f'Verified {len(expected)} canonical pages, shared headers and footers, bilingual metadata, visible breadcrumbs, homepage schemas, internal link reachability and discovery files, including both llms.txt indexes.')


if __name__ == '__main__':
    check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'doc_build')
