"""직접 확인한 실제01 viewport 원본을 설명 위치에 연결한다. 이미지 편집 없음."""
from pathlib import Path
from html import escape
import hashlib,json,shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
MANUAL=ROOT/'deliverables/manuals/concept-01'
SOURCE=ROOT/'execute/designReview/concept-01/evidence'
ASSETS=MANUAL/'assets';ASSETS.mkdir(exist_ok=True)
SHOTS={
'home':('vp-mobile390-owner-home.png','점주 모바일 홈. 사진으로 점검하기 버튼, 매장과 카테고리 필터, 하단 네 가지 탐색이 보입니다.','점주 · 홈 · 390×844 viewport. 큰 제출 버튼에서 새 점검을 시작합니다. 공지에서 AI 생성 사진·Mock 과거 자료와 새 실제 AI 분석을 구분합니다.','mobile'),
'preview':('vp-mobile390-preview-keyboard.png','스낵 사진 한 장의 미리보기와 질문, 파란 키보드 초점이 표시된 사진 접수하고 분석 시작 버튼.','점주 · 제출 입력 구간 · 390×844 viewport. 파일명·용량과 순서/제거, 질문 62/2,000자, 제출 버튼 초점을 확인합니다. 이 캡처는 사진 한 장을 선택한 상태입니다.','mobile'),
'running':('vp-mobile390-analysis-running.png','사진과 질문 아래 분석 중 상태, 경과 32초, 이력에서 다시 확인할 수 있다는 지연 안내.','점주 · 처리 중 · 390×844 viewport. 접수 후 32초의 분석 중 상태입니다. 화면을 나가도 이력에서 다시 볼 수 있다는 안내를 확인합니다. 아직 판정이 나온 화면은 아닙니다.','mobile'),
'result':('vp-mobile390-real-first-top.png','은행길점 스낵의 분석 완료 상태와 생성 이미지 배지, 원본 사진, 30초 목표 초과 안내.','점주 · 첫 실제 결과 상단 · 390×844 viewport. 분석 완료와 AI 생성 시연 이미지 출처를 구분합니다. 화면의 91.6초 표시는 화면을 떠난 시간도 포함하는 앱 표시값입니다. 아래 브라우저 관찰 기록과 같은 측정값으로 혼동하지 마세요.','mobile'),
'answer':('vp-mobile390-real-first-answer.png','점주 질문과 실제 AI 분석 배지 아래 상품 앞줄 정렬과 라벨 가림에 대한 한국어 답변.','점주 · 실제 질문 답변 · 390×844 viewport. 실제 AI 분석 배지와 질문에 대한 답을 확인합니다. 이 화면에는 기준별 점수 전체가 보이지 않으며 일반 정확도를 뜻하지 않습니다.','mobile'),
'dashboard':('vp-desktop1440-hq-dashboard.png','본사 관제. 왼쪽 메뉴와 범위 필터, 네 가지 처리 지표, 매장별 기록 표가 배치되어 있습니다.','본사 · 매장 관제 · 1440×900 viewport. 범위를 고른 뒤 지표와 매장 행에서 확인할 기록으로 이동합니다. 표본과 Mock 평가 수를 함께 읽습니다. 수치는 촬영 당시 테스트 자료입니다.','desktop'),
'reference':('vp-desktop1440-reference-list.png','Reference 관리 목록. 160픽셀 썸네일 옆에 버전, 설명, 대상 매장, 상태와 사진 설명 수정 버튼이 보입니다.','본사 · Reference 목록 · 1440×900 viewport. 썸네일과 카테고리·대상·버전·설명을 한 행에서 확인하고 사진 · 설명 수정으로 편집합니다. 생성 출처 배지는 사진 아래에 있습니다.','desktop'),
'criterion':('vp-desktop1280-category-v2.png','기준 변경 저장 확인과 새 버전 저장 폼, 변경 이력의 버전 2가 표시된 본사 화면.','본사 · CATEGORY 기준 변경 후 · 1280×800 viewport. 저장 완료 안내와 버전 2 이력이 보입니다. 과거 제출의 기준 보존 여부는 해당 제출의 적용 기준에서 별도로 확인합니다.','desktop'),
}
SHOTS['comparison']=('vp-desktop1440-before-after.png','이전 스낵 매대 사진과 개선 후 사진을 나란히 배치하고 기준 변경 시 직접 비교 제한을 안내하는 화면.','점주 · 개선 전후 비교 · 1440×900 viewport. 이전 사진과 이번 사진을 나란히 살핍니다. 기준이 변경된 항목은 동일 조건으로 비교할 수 없다는 안내가 위에 보입니다.','desktop')
SHOTS['issue']=('vp-desktop1440-ofc-resolved.png','OFC 확인 요청이 해결 상태이고 담당자, 해결 내용, 변경 저장 완료 안내가 표시된 화면.','OFC · 확인 요청 해결 후 · 1440×900 viewport. 담당자가 개선 사진과 새 기준을 검토한 해결 내용과 저장 완료를 확인합니다. 관련 사진과 평가 확인 링크에서 근거로 돌아갑니다.','desktop')
manifest=[]
def figure(key):
 name,alt,caption,kind=SHOTS[key]
 original=SOURCE/name;dest=ASSETS/name
 shutil.copyfile(original,dest)
 data=dest.read_bytes()
 with Image.open(dest) as decoded:width,height=decoded.size;actual_format=decoded.format
 manifest.append({'key':key,'source':str(original.relative_to(ROOT)),'manual_asset':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'width':width,'height':height,'actual_format':actual_format,'source_bytes_equal':original.read_bytes()==data,'caption':caption,'alt':alt,'inspection':'작성자 직접 원본 열람, 변형 없이 복사'})
 return f'<figure class="screen-{kind}" id="screen-{key}"><a href="assets/{name}" aria-label="{escape(alt,quote=True)} 원본 열기"><img src="assets/{name}" width="{width}" height="{height}" alt="{escape(alt,quote=True)}" loading="lazy"></a><figcaption>{escape(caption)} <a href="assets/{name}">원본 보기</a></figcaption></figure>'

path=MANUAL/'index.html';html=path.read_text()
if 'id="screen-home"' in html:raise SystemExit('이미 이미지가 반영되었습니다. 생성기로01 초안을 재생성한 뒤 실행하세요.')
html=html.replace('<h3>접수와 결과 확인</h3>', '<div class="shot-pair">'+figure('home')+figure('preview')+'</div><h3>접수와 결과 확인</h3>',1)
html=html.replace('<h3>개선 후 다시 제출하고 비교</h3>',figure('answer')+'<h3>개선 후 다시 제출하고 비교</h3>',1)
html=html.replace('</section><section id="business"',figure('comparison')+'</section><section id="business"',1)
html=html.replace('<h3>추이·비교·기본 집계</h3>',figure('issue')+'<h3>추이·비교·기본 집계</h3>',1)
html=html.replace('<h3>담당 매장 연결 · OFC</h3>',figure('dashboard')+'<h3>담당 매장 연결 · OFC</h3>',1)
html=html.replace('<h3>좋은 진열 예시 · Reference</h3>',figure('criterion')+'<h3>좋은 진열 예시 · Reference</h3>',1)
html=html.replace('<h3>확인 이슈에 대응</h3>',figure('reference')+'<h3>확인 이슈에 대응</h3>',1)

css='.shot-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;align-items:start}.screen-mobile{max-width:390px;margin:24px auto}.screen-desktop{margin:24px 0}figure a{display:block}figcaption a{display:inline}figure img{height:auto}.shot-pair figure{min-width:0;width:100%}@media(max-width:600px){.shot-pair{grid-template-columns:1fr}}'
html=html.replace('</style>',css+'</style>',1)
html=html.replace('data-manual-status="draft-not-run"','data-manual-status="review-partial-images"')
html=html.replace('초안 · 화면 캡처/브라우저 문서 검증 NOT_RUN','검수 중 · 실제 화면 8장 / 문서 브라우저 검수 NOT_RUN')
html=html.replace('초안 · 실제 화면 캡처와 문서 렌더 검증 NOT_RUN','실제 화면 8장 반영 · 문서 렌더 검증 NOT_RUN')
html=html.replace('최종 브라우저 인수와 완성 화면 캡처가 아직 인계되지 않았으므로 이 문서에는 화면 이미지를 넣지 않았습니다. 빈 그림 틀이나 다른 시안 사진을 실제 화면처럼 제공하지 않습니다.','직접 확인한 시안 01의 실제 viewport 캡처 8장을 해당 업무 설명에 연결했습니다. 재제출·비교·OFC 해결 화면까지 포함했습니다. 운영 화면 등 추가 증거와 매뉴얼의 실제 브라우저 검수는 대기 중입니다. 현재 그림만으로 모든 역할과 전체 시연이 통과했다고 보지 않습니다.')
html=html.replace('로그인·점주 제출/결과·관리/운영의 해당 시안 실제 캡처</td><td>NOT_RUN · root가 최종 vp-*.png 인계 후 반영','점주 홈·제출·첫 답변·전후 비교, 본사 관제·Reference·기준 변경, OFC 해결 캡처</td><td>8장 반영 · 운영 화면/추가 경계 증거 대기')
html=html.replace('실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>root의 시안별 검증 결과 인계 대기','실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>첫 분석·재제출 succeeded · 30초 목표 미달 · 전체 기능 인수 진행 중')
html=html.replace('독립 디자인 최종 PNG 검수</td><td>contract_ai 재검수 결과 인계 대기','독립 디자인 최종 PNG 검수</td><td>캡처별 독립 확인 진행 중 · 최종 디자인 판정 대기')
latency='''<h3>시안 01 첫 실제 분석 기록</h3><p>은행길점·스낵의 사진 1장, 기준 5개, Reference 2개로 실제 모델 분석이 완료되었습니다. 모델 처리 <b>90.824초</b>, 접수부터 DB 결과 저장까지 <b>91.132초</b>, 제출 버튼 Enter부터 브라우저의 완료 텍스트 관찰까지 <b>91.732초</b>였습니다. <b>30초 목표 미달</b>입니다. 이 사례의 기준별 결과는 준수 1개·개선 필요 4개로 준수율 20%, 판단 가능률 100%였으며, 합성 사진 한 사례의 응답입니다. 마지막 관찰 간격 약 3초가 포함된 브라우저 기록이므로 정확한 화면 갱신 순간과는 차이가 있을 수 있습니다.</p><p>재제출은 모델 처리 <b>54.601초</b>, 접수부터 DB 결과까지 <b>55.622초</b>였고 기준 5개 모두 준수로 응답했습니다. 브라우저 첫 완료 확인은 <b>69.336초 이하</b>이며, 중간 관찰 간격이 포함된 상한입니다. 정확한 표시 순간으로 해석하지 않습니다. 이번 20%→100%는 합성 사진 사례이고 기준 버전이 달라진 항목은 직접 비교하지 않습니다. 두 분석의 성공으로 전체 기능·디자인 인수를 완료했다고 보지 않습니다.</p><p class="compact">근거: <a href="../../../execute/workHitory/integration-concept-01/actual-ai.json">실제 AI 실행 기록</a> · <a href="../../../execute/designReview/concept-01/evidence/browser-latency-first.json">브라우저 지연 기록</a> · <a href="../../../execute/designReview/concept-01/evidence/browser-latency-child.json">재제출 관찰 시간</a> · <a href="../../../execute/workHitory/integration-concept-01/browser.md">시안 01 기능 인수 진행</a>.</p>'''
html=html.replace('<h3>권한과 자료 취급</h3>',latency+'<h3>권한과 자료 취급</h3>',1)
html=html.replace('외부 CDN/스크립트 없음 · 실제 화면 인계 후 갱신','외부 CDN/스크립트 없음 · 실제 화면 8장 반영 · 최종 문서 검수 대기')
path.write_text(html)
(ROOT/'execute/workHitory/manuals-others/concept01-image-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('01 실제 이미지 원본 복사·캡션·상태·지연 반영:',len(manifest),'장')
