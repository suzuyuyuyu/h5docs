#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["markdown"]
# ///
"""兄弟プロジェクトの Markdown を静的リファレンスへ変換する。

    uv run scripts/build_reference.py

依存と Python のバージョンは上のメタデータで宣言しているので、
uv が条件を満たす環境を用意する。
"""
from html import escape
from posixpath import relpath
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ('h5fortran', 'h5c', 'h5cpp', 'h5xdmf')


def page(title, body, current, prefix=''):
    """既存トップページの外枠をそのまま使う。"""
    shell = (ROOT / 'index.html').read_text()
    head, rest = shell.split('<main class="page">', 1)
    _, tail = rest.split('</main>', 1)
    head = re.sub(r'<title>.*?</title>', '<title>' + escape(title) + ' — h5</title>', head)
    head = head.replace(' aria-current="page"', '')
    head = head.replace(f'<a href="{current}"', f'<a href="{current}" aria-current="page"')
    head = re.sub(r'href="([^"]+)"', lambda m: f'href="{prefix}{m[1]}"', head)
    return head + '<main class="page">\n' + body + '\n</main>' + tail


class SiteLinks(Treeprocessor):
    def __init__(self, md, source, targets):
        super().__init__(md)
        self.source, self.targets = source, targets

    def run(self, root):
        used = set()
        for node in root.iter():
            if re.fullmatch(r'h[1-6]', node.tag) and 'id' not in node.attrib:
                slug = re.sub(r'[^\w\- ]', '', ''.join(node.itertext()).lower()).replace(' ', '-')
                anchor, suffix = slug, 0
                while anchor in used:
                    suffix += 1
                    anchor = f'{slug}-{suffix}'
                used.add(anchor)
                node.set('id', anchor)
            if node.tag != 'a' or 'href' not in node.attrib:
                continue
            url = urlsplit(node.get('href'))
            if url.scheme or url.netloc or not url.path:
                continue
            target = (self.source.parent / unquote(url.path)).resolve()
            if target in self.targets:
                path = relpath(self.targets[target], self.targets[self.source]) + '/'
            else:
                # 変換対象外の README・実例は元リポジトリへ案内する。
                # Path.is_relative_to() は 3.9 以降にしかないので使わない。
                project_root = next((ROOT.parent / p for p in PROJECTS
                                     if (ROOT.parent / p) in target.parents), None)
                if project_root is None or not target.exists():
                    raise ValueError(f'参照先が見つかりません: {self.source}: {url.path}')
                kind = 'tree' if target.is_dir() else 'blob'
                path = (f'https://github.com/suzuyuyuyu/{project_root.name}/{kind}/main/'
                        + quote(target.relative_to(project_root).as_posix()))
            node.set('href', urlunsplit(('', '', path, url.query, url.fragment)))


class SiteExtension(Extension):
    def __init__(self, source, targets):
        self.source, self.targets = source, targets
        super().__init__()

    def extendMarkdown(self, md):
        md.treeprocessors.register(SiteLinks(md, self.source, self.targets), 'site_links', 5)


def main():
    sources = [p.resolve() for project in PROJECTS
               for p in sorted((ROOT.parent / project / 'docs').glob('*.md'))]
    targets = {p: f'{p.parent.parent.name}/{p.stem.lower()}/' for p in sources}
    destination = ROOT / 'reference'
    destination.mkdir(exist_ok=True)
    for project in PROJECTS:
        for old in destination.glob(f'{project}-*.html'):
            old.unlink()
    groups = ['<h1>リファレンス</h1><p class="lede">各プロジェクトの docs/*.md から生成した詳細資料です。</p>']
    for project in PROJECTS:
        groups.append(f'<h2>{project}</h2><ul>')
        for source in sources:
            if source.parent.parent.name != project:
                continue
            converter = markdown.Markdown(extensions=['tables', 'fenced_code'])
            SiteExtension(source, targets).extendMarkdown(converter)
            body = converter.convert(source.read_text())
            title = f'{project} / {source.stem}'
            body = (f'<p>出典：<code>{project}/docs/{escape(source.name)}</code></p>'
                    f'<div class="reference">{body}</div>')
            name = targets[source]
            output = destination / name / 'index.html'
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(page(title, body, 'reference/', '../../../'))
            groups.append(f'<li><a href="{name}">{escape(source.stem)}</a></li>')
            print(f'生成: reference/{name}')
        groups.append('</ul>')
    (destination / 'index.html').write_text(page('リファレンス', '\n'.join(groups), 'reference/', '../'))
    print('生成: reference/index.html')
    print(f'完了: {len(sources)} 文書 + 索引 1 ページ')


if __name__ == '__main__':
    main()
