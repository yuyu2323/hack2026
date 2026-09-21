"""다른 작성자의 매뉴얼 이미지·캡션·로컬 링크를 독립 확인한다."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]


class ManualParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images, self.ids, self.links, self.figures = [], [], [], []
        self.figure = None
        self.caption = self.link = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.link = True
            self.links.append(attrs.get('href', ''))
        if tag == 'figure':
            self.figure = {'images': [], 'caption': ''}
        if tag == 'img':
            self.images.append(attrs)
            if self.figure is not None:
                self.figure['images'].append(attrs)
        if tag == 'figcaption':
            self.caption = True

    def handle_data(self, data):
        if self.caption and not self.link and self.figure is not None:
            self.figure['caption'] += data

    def handle_endtag(self, tag):
        if tag == 'a':
            self.link = False
        if tag == 'figcaption':
            self.caption = False
        if tag == 'figure':
            self.figures.append(self.figure)
            self.figure = None


def check(concept):
    path = ROOT / f'deliverables/manuals/concept-{concept}/index.html'
    manifest_path = ROOT / f'execute/workHitory/manuals-others/concept{concept}-image-manifest.json'
    if not manifest_path.exists():
        return {'concept': concept, 'status': 'NOT_RUN', 'reason': '이미지 manifest 미인계'}
    parser = ManualParser()
    parser.feed(path.read_text(encoding='utf-8'))
    rows = []
    for item in json.loads(manifest_path.read_text()):
        asset, original = ROOT / item['manual_asset'], ROOT / item['source']
        relative = str(asset.relative_to(path.parent))
        matches = [i for i in parser.images if i.get('src') == relative]
        figures = [f for f in parser.figures if any(i.get('src') == relative for i in f['images'])]
        rows.append({
            'source': item['source'], 'asset': item['manual_asset'],
            'sha256': hashlib.sha256(asset.read_bytes()).hexdigest(),
            'copy_and_hash_equal': original.read_bytes() == asset.read_bytes() and hashlib.sha256(asset.read_bytes()).hexdigest() == item['sha256'],
            'alt_equal': len(matches) == 1 and matches[0].get('alt') == item['alt'],
            'caption_equal': len(figures) == 1 and figures[0]['caption'].strip() == item['caption'],
        })
    broken, count = [], 0
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or url.netloc:
            continue
        count += 1
        if url.path and not (path.parent / unquote(url.path)).exists():
            broken.append(href)
        if not url.path and url.fragment and url.fragment not in parser.ids:
            broken.append(href)
    passed = not broken and len(parser.images) == len(rows) and len(parser.ids) == len(set(parser.ids)) and all(r['copy_and_hash_equal'] and r['alt_equal'] and r['caption_equal'] for r in rows)
    return {'concept': concept, 'status': 'PASS' if passed else 'FAIL', 'scope': '원본/복사/manifest·alt·캡션과 정적 링크 검사. 사진 직접 시각 검수 기록과 별도로 사용하며 Browser 문서 렌더를 대신하지 않는다.', 'html_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'images': rows, 'local_links': count, 'broken_links': broken}


if __name__ == '__main__':
    for concept in sys.argv[1:] or ['01', '03', '04', '05']:
        if concept not in {'01', '03', '04', '05'}:
            raise ValueError('검수 소유 대상인 01/03/04/05만 허용한다.')
        result = check(concept)
        (ROOT / f'execute/workHitory/manual-review/concept{concept}-images-latest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(concept, result['status'], len(result.get('images', [])))
