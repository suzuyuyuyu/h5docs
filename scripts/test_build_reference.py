# /// script
# requires-python = ">=3.9"
# dependencies = ["markdown"]
# ///
"""uv run scripts/test_build_reference.py"""
import re

import markdown

from build_reference import ROOT, SiteExtension, page


source = ROOT.parent / 'h5c/docs/USAGE.md'
targets = {
    source: 'h5c/usage/',
    source.with_name('FORMAT.md'): 'h5c/format/',
    ROOT.parent / 'h5cpp/docs/USAGE.md': 'h5cpp/usage/',
}
converter = markdown.Markdown()
SiteExtension(source, targets).extendMarkdown(converter)
html = converter.convert('[same](FORMAT.md?view=1#次元順序) '
                         '[other](../../h5cpp/docs/USAGE.md) '
                         '[self](USAGE.md#ビルド設定)')
assert 'href="../format/?view=1#次元順序"' in html
assert 'href="../../h5cpp/usage/"' in html
assert 'href="./#ビルド設定"' in html

for depth in range(4):
    directory = ROOT.joinpath(*(['level'] * depth))
    html = page('test', '', 'reference/', '../' * depth)
    href = re.search(r'rel="stylesheet" href="([^"]+)"', html)[1]
    assert (directory / href).resolve() == ROOT / 'assets/style.css'

for file in ROOT.rglob('*.html'):
    html = file.read_text()
    href = re.search(r'rel="stylesheet" href="([^"]+)"', html)[1]
    assert (file.parent / href).resolve() == ROOT / 'assets/style.css', file
    for href in re.findall(r'(?:href|src)="([^"#:]+)(?:#[^"]*)?"', html):
        target = file.parent / href
        assert target.is_file() or (target / 'index.html').is_file(), (file, href)
        if target.is_dir():
            assert href.endswith('/'), (file, href)
        assert not href.endswith('index.html'), (file, href)
