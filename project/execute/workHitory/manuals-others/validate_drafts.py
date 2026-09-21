from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json
import hashlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class ManualParser(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.hrefs=[];self.resources=[];self.stack=[];self.errors=[];self.images=[];self.lang=None;self.viewport=False;self.charset=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a:self.hrefs.append(a['href'])
        if tag in {'img','script','iframe','link','source'}:self.resources.append((tag,a.get('src') or a.get('href')))
        if tag=='img':self.images.append(a)
        if tag=='html':self.lang=a.get('lang')
        if tag=='meta':
            self.viewport|=a.get('name')=='viewport'
            self.charset|=a.get('charset')=='utf-8'
        if tag not in VOID:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag in VOID:return
        if not self.stack or self.stack[-1]!=tag:self.errors.append('tag mismatch: '+tag)
        else:self.stack.pop()

credentials=json.loads((ROOT/'.local/demo-credentials').read_text())
# 비밀번호는 메모리에서 포함 여부만 비교하며 값이나 파생값을 출력하지 않는다.
secrets=[v['password'] for v in credentials.values() if isinstance(v,dict) and v.get('password')]
results=[]
for cid in ['01','03','04','05']:
    path=ROOT/'deliverables/manuals'/f'concept-{cid}'/'index.html'
    data=path.read_bytes();text=data.decode('utf-8');p=ManualParser();p.feed(text)
    errors=list(p.errors)
    if p.stack:errors.append('unclosed tags')
    if len(p.ids)!=len(set(p.ids)):errors.append('duplicate IDs')
    if p.lang!='ko' or not p.viewport or not p.charset:errors.append('locale/meta missing')
    for href in p.hrefs:
        parsed=urlparse(href)
        if parsed.scheme:
            if parsed.scheme!='http' or parsed.hostname!='127.0.0.1':errors.append('unexpected external link')
            continue
        if not parsed.path:
            if parsed.fragment not in p.ids:errors.append('missing anchor: '+parsed.fragment)
        elif not (path.parent/unquote(parsed.path)).resolve().exists():errors.append('missing local link: '+parsed.path)
    for tag,ref in p.resources:
        if tag!='img':errors.append('unexpected resource dependency: '+tag)
        elif not ref or urlparse(ref).scheme or not (path.parent/ref).is_file():errors.append('invalid local image')
    for img in p.images:
        if not img.get('alt') or not img.get('width') or not img.get('height'):errors.append('image accessibility/dimension missing')
        else:
            with Image.open(path.parent/img['src']) as decoded:
                if decoded.size!=(int(img['width']),int(img['height'])):errors.append('image dimensions mismatch')
                decoded.verify()
    expected_images={'01':8,'03':10,'04':10,'05':12}[cid]
    if len(p.images)!=expected_images:errors.append('unexpected verified image count')
    if expected_images:
        manifest=json.loads((ROOT/f'execute/workHitory/manuals-others/concept{cid}-image-manifest.json').read_text())
        if len(manifest)!=len(p.images):errors.append('image manifest count mismatch')
        for item in manifest:
            source=ROOT/item['source'];asset=ROOT/item['manual_asset'];image=next((img for img in p.images if (path.parent/img['src']).resolve()==asset.resolve()),None)
            if not image:errors.append('manifest image not embedded')
            elif image['alt']!=item['alt']:errors.append('manifest image alt mismatch')
            if source.read_bytes()!=asset.read_bytes() or hashlib.sha256(asset.read_bytes()).hexdigest()!=item['sha256']:errors.append('image original/hash mismatch')
    if 'url(' in text or '@import' in text:errors.append('external CSS dependency candidate')
    if any(secret in text for secret in secrets):errors.append('credential value found')
    required=['NOT_RUN','판단 불가','기술 실패','Mock','AI 생성 시연 이미지','30초','최종 사용할 시안은 사람이 선택','모바일','operator.demo','.local/demo-credentials']
    errors.extend('required content missing: '+token for token in required if token not in text)
    result={'concept':cid,'status':'PASS' if not errors else 'FAIL','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'anchors':len(p.ids),'local_links':len([h for h in p.hrefs if not urlparse(h).scheme and urlparse(h).path]),'images':len(p.images),'external_resource_dependencies':len([r for r in p.resources if r[1] and urlparse(r[1]).scheme]),'errors':errors}
    results.append(result)
report={'scope':'HTML/로컬 이미지 링크 정적 검사. 별도 root 실제 문서 desktop1440×900/mobile390×844·로컬 이미지·키보드/본문 건너뛰기 및 독립 PNG 재검수 PASS. 200% 확대·OS 네트워크 차단 오프라인 검사 NOT_RUN, 전체 제품 인수 진행 중.','credential_check':'비밀 값 노출 없음' if not any('credential value found' in x['errors'] for x in results) else '실패','results':results}
(ROOT/'execute/workHitory/manuals-others/static-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if all(r['status']=='PASS' for r in results) else 1)
