"""직접 열람한03 viewport 캡처만 원본 그대로 사용자 설명에 연결한다."""
from pathlib import Path
from html import escape
import hashlib,json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
MANUAL=ROOT/'deliverables/manuals/concept-03'
SOURCE=ROOT/'execute/designReview/concept-03/evidence'
ASSETS=MANUAL/'assets';ASSETS.mkdir(exist_ok=True)
SHOTS={
 'preview':('vp-mobile390-first-preview.png','음료 사진 한 장의 미리보기, 사진 1 번호, beverage-before-01.png 파일명과 2.2MiB, 삭제 버튼이 보이는 제출 화면.','점주 · 모바일 제출 · 390×844 viewport. 선택 목록은 아래 사진 번호·파일명·미리보기로 확인합니다. 사진을 추가하거나 삭제하고, 아래 점주 질문을 입력한 뒤 사진 제출하기를 누릅니다.','mobile'),
 'processing':('vp-mobile390-first-processing.png','점주 질문 아래 사진을 분석하고 있어요 안내와 경과14초, 상태를 다시 확인 버튼, 적용 기준과 Reference 영역.','점주 · 첫 실제 제출 처리 중 · 390×844 viewport. 접수 후 결과를 기다리는 화면입니다. 상태를 다시 확인할 수 있고 이력에서 다시 열 수 있습니다. 아직 준수 판정이나 실제 AI 완료 결과가 표시된 화면은 아닙니다.','mobile'),
 'dashboard':('vp-desktop1440-photo-dashboard-fixed.png','본사 사진 관제 첫 화면. 범위 필터 바로 아래 최근 도착한 매대 사진 세 장이 나란히 놓이고 지표·매장 현황 이동 링크가 보입니다.','본사 · 사진 관제 · 1440×900 viewport. 최근 사진이 먼저 보이며 집계와 매장별 상태는 하단 지표·매장 현황으로 이어집니다. 사진을 선택하면 관찰 근거와 후속 조치를 확인할 수 있습니다.','desktop'),
 'unknown':('vp-mobile390-unknown-mock.png','어둡고 일부 가린 매대 사진과 Mock 데이터 배지, 과거 합성 평가 안내, 준수율 대시와 판단 가능률0%, 판단불가4개.','점주 · 판단 불가 예시 · 390×844 viewport. 이 화면은 Mock 과거 평가입니다. 판단 가능한 기준이 없어 준수율은 대시로 표시되고 판단 가능률은0%입니다. 실제 신규 AI 실패 또는 진열 위반0%라는 뜻이 아닙니다.','mobile'),
 'failed':('vp-mobile390-technical-failure.png','분석을 완료하지 못했어요와 분석 서비스 연결 실패 안내, 운영자 복구 요청 및 상태를 다시 확인 버튼.','점주 · 기술 실패 예시 · 390×844 viewport. 준비된 시드 실패 사례로 복구 안내를 확인한 화면입니다. 기준별 판단 불가와 구별하며 새 실제 AI 제출의 실패 기록으로 소개하지 않습니다. 운영자에게 복구를 요청하거나 새로운 현장 사진을 별도로 제출할 수 있습니다.','mobile'),
 'empty':('vp-mobile390-empty-history.png','새봄로점 생활용품을 고른 사진 이력에서 선택한 기간에 제출한 사진이 없습니다 안내와0개 결과.','점주 · 빈 이력 · 390×844 viewport. 현재 범위와 기간에 사진이 없는 상태입니다. 필터를 확인하거나 초기화해 다른 범위를 찾아보세요. 제출 없음은 위반 판정이 아닙니다.','mobile')}
SHOTS.update({
 'first':('vp-mobile390-first-actual-result.png','첫 음료 제출의 점주 질문 아래 실제 AI 분석 배지와 앞줄 간격·중단 빈 공간 및 가격 숫자를 확인하기 어렵다는 답변.','점주 · 첫 실제 AI 답변 · 390×844 viewport. AI가 앞줄 정렬과 중간 빈 공간에 대한 관찰을 설명합니다. 가격 숫자 판독의 한계도 함께 읽고 필요한 현장 확인을 진행합니다. 전체 점수는 이 캡처의 보이는 구간 밖입니다.','mobile'),
 'child':('vp-mobile360-child-actual-result.png','개선 후 재제출 질문과 실제 AI 분석 배지, 이전보다 빈 공간과 정렬이 개선되고 새 라벨 기준에 관해 설명하는 답변.','점주 · 개선 후 실제 AI 답변 · 360×800 viewport. 이전 기록과 연결한 새 사진을 분석한 결과입니다. 이전 사진과 현재 사진의 관찰을 확인하되 변경된 라벨 기준은 동일 조건의 효과로 비교하지 않습니다.','mobile'),
 'comparison':('vp-desktop1440-comparison-dates-fixed.png','본사에서 확인한 전후 비교. 이전·현재 사진 위에 각각 연도를 포함한 제출 날짜와 KST가 보이고 아래에 준수율60%와100%가 표시됩니다.','본사 · 개선 전후 비교 · 1440×900 viewport. 양쪽 제출 시각과 원본 사진을 함께 확인합니다. 점주도 본인에게 허용된 기록에서 같은 비교를 열 수 있습니다. 점수 차이는 아래 적용 버전과 함께 읽습니다.','desktop'),
 'comparison_versions':('vp-desktop1440-comparison-versions-fixed.png','전후 기준 버전과 판정 변화 표. qa03_labels는v1에서v2로 바뀌어 비교 불가이며 facing과shelf_gap은 개선으로 표시됩니다.','전후 비교 · 기준별 변화 · 1440×900 viewport. 이전 기준 버전과 현재 기준 버전을 나란히 확인합니다. 같은 버전의 정렬·빈 공간 항목은 개선됐지만, 라벨 기준은 변경되어 판정의 직접 비교에 한계가 있습니다.','desktop'),
 'operator_retry':('vp-desktop1440-operator-retry-success.png','운영자의 처리 이력에서 첫 시도 expired와 적용 결과 없음이 보존되고 두 번째 시도 분석 완료·결과 저장 완료가 표시됩니다.','플랫폼 운영자 · 재처리 성공 후 · 1440×900 viewport. 연습용 실패 작업을 재처리한 사례입니다. 첫 만료 이력을 보존한 채 두 번째 시도가 완료됐고, 성공 상태에서는 다시 재처리할 수 없음을 확인합니다. 영업 사진이나 평가 본문은 표시하지 않습니다.','desktop'),
 'reference':('vp-desktop1440-reference-versions.png','Reference 사진 갤러리에서 QA03 음료 Reference v2 사용 중 카드와 v1 과거 버전/비활성 카드, 각각의 생성 이미지 출처와 내용·상태 변경 링크.','본사 · Reference 버전 갤러리 · 1440×900 viewport. 현재 v2와 과거 v1을 사진 중심으로 확인합니다. 과거 관리 사진도 현재 허용 범위 안에서 열리며 이전 제출에 적용된 자료는 유지됩니다.','desktop')})
manifest=[]
def figure(key):
 name,alt,caption,kind=SHOTS[key];source=SOURCE/name;dest=ASSETS/name;shutil.copyfile(source,dest)
 with Image.open(dest) as decoded:width,height=decoded.size;actual_format=decoded.format
 data=dest.read_bytes();manifest.append({'key':key,'source':str(source.relative_to(ROOT)),'manual_asset':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'width':width,'height':height,'actual_format':actual_format,'source_bytes_equal':source.read_bytes()==data,'caption':caption,'alt':alt,'inspection':'작성자 직접 원본 열람, 변형 없이 복사'})
 return f'<figure class="screen-{kind}" id="screen-{key}"><a href="assets/{name}" aria-label="{escape(alt,quote=True)} 원본 열기"><img src="assets/{name}" width="{width}" height="{height}" alt="{escape(alt,quote=True)}" loading="lazy"></a><figcaption>{escape(caption)} <a href="assets/{name}">원본 보기</a></figcaption></figure>'
p=MANUAL/'index.html';s=p.read_text();assert 'id="screen-preview"' not in s,'generator03을 실행해 이미지 없는 초안에서 시작하세요.'
s=s.replace('<h3>접수와 결과 확인</h3>',figure('preview')+'<h3>접수와 결과 확인</h3>',1)
s=s.replace('<h3>개선 후 다시 제출하고 비교</h3>','<div class="shot-pair">'+figure('first')+figure('child')+'</div><h3>개선 후 다시 제출하고 비교</h3>',1)
s=s.replace('</section><section id="business"',figure('comparison')+figure('comparison_versions')+'</section><section id="business"',1)
s=s.replace('</section><section id="states"',figure('operator_retry')+'</section><section id="states"',1)
s=s.replace('<h3>확인 이슈에 대응</h3>',figure('reference')+'<h3>확인 이슈에 대응</h3>',1)
s=s.replace('<h3>담당 매장 연결 · OFC</h3>',figure('dashboard')+'<h3>담당 매장 연결 · OFC</h3>',1)
s=s.replace('<p class="compact">대기/기술 처리 상태와 기준별 진열 판정은 서로 다른 의미입니다.', '<div class="shot-pair">'+figure('unknown')+figure('failed')+'</div>'+'<p class="compact">대기/기술 처리 상태와 기준별 진열 판정은 서로 다른 의미입니다.',1)
s=s.replace('</style>','.shot-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;align-items:start}.screen-mobile{max-width:390px;margin:24px auto}.screen-desktop{margin:24px 0}figure a{display:block}figcaption a{display:inline}figure img{height:auto}.shot-pair figure{min-width:0;width:100%}@media(max-width:600px){.shot-pair{grid-template-columns:1fr}}</style>',1)
s=s.replace('data-manual-status="draft-not-run"','data-manual-status="review-partial-images"')
s=s.replace('초안 · 화면 캡처/브라우저 문서 검증 NOT_RUN','검수 중 · 실제 화면 10장 / 문서 브라우저 검수 NOT_RUN')
s=s.replace('초안 · 실제 화면 캡처와 문서 렌더 검증 NOT_RUN','실제 화면 10장 반영 · 문서 렌더 검증 NOT_RUN')
s=s.replace('최종 브라우저 인수와 완성 화면 캡처가 아직 인계되지 않았으므로 이 문서에는 화면 이미지를 넣지 않았습니다. 빈 그림 틀이나 다른 시안 사진을 실제 화면처럼 제공하지 않습니다.','직접 확인한 시안03의 정상 viewport 캡처10장을 업무 설명에 연결했습니다. 사진 관제, 점주 미리보기·첫 실제 답변·재제출 답변·전후 사진과 기준 버전 비교, Reference 버전, Mock 판단 불가·시드 기술 실패, 운영자 재처리 성공을 보여줍니다. 그 밖의 관리·운영 증거와 최종 문서 렌더 검수는 대기입니다. 이 그림으로 전체 인수를 완료했다고 보지 않습니다.')
s=s.replace('로그인·점주 제출/결과·관리/운영의 해당 시안 실제 캡처</td><td>NOT_RUN · root가 최종 vp-*.png 인계 후 반영','사진 관제·미리보기·첫/재제출 답변·날짜/버전 비교·Reference·판단 불가·기술 실패·운영 재처리 캡처</td><td>정상10장 반영 · 최종 문서/추가 업무 검수 대기')
s=s.replace('실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>root의 시안별 검증 결과 인계 대기','실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>첫 분석·재제출 succeeded · 두 건 모두30초 목표 미달 · 전체 기능 인수 진행 중')
s=s.replace('독립 디자인 최종 PNG 검수</td><td>contract_ai 재검수 결과 인계 대기','독립 디자인 최종 PNG 검수</td><td>사진 관제·기준 이력·비교 날짜/버전 개별 항목 확인 · 전체 디자인 판정 대기')
s=s.replace('외부 CDN/스크립트 없음 · 실제 화면 인계 후 갱신','외부 CDN/스크립트 없음 · 실제 화면 10장 반영 · 최종 문서 검수 대기')
# 지연은 모델 실행, DB 완료, 브라우저 관찰을 각각 정본 값으로 표시한다.
actual=json.loads((ROOT/'execute/workHitory/integration-concept-03/actual-ai.json').read_text())
first=next(row for row in actual if row['submission_id']=='46e985b6-58cd-4376-b035-cd5f0e38c600')
child=next(row for row in actual if row['submission_id']=='dfc9189b-e833-4500-bc37-c0f4976f0625')
first_observation=json.loads((SOURCE/'first-latency.json').read_text())
child_observation=json.loads((SOURCE/'child-latency.json').read_text())
assert first['status']==child['status']=='succeeded' and first['source_kind']==child['source_kind']=='real_ai'
seconds=lambda ms:f"{ms/1000:.3f}"
latency=f'''<h3>시안 03 실제 분석과 개선 후 제출</h3><p>별하천점·음료의 사진1장씩을 각각 기준5개·Reference2개와 함께 실제 AI로 분석했습니다. 첫 평가 준수율은<b>60%</b>, 개선 후 평가는<b>100%</b>였고 두 평가의 판단 가능률은<b>100%</b>였습니다. 같은 기준으로 비교할 수 있는 앞줄 정렬과 빈 공간 항목은 개선 필요에서 준수로 바뀌었습니다. 다만 <code>qa03_labels</code>는 v1→v2로 내용이 바뀌었으므로 해당 항목은 직접 비교하지 않습니다. 전체 점수 차이를 동일 조건의 개선 효과로 해석하지 마세요. 합성 사진 한 사례의 결과이며 일반 정확도 검증은 아닙니다.</p><p>첫 분석의 모델 처리는<b>{seconds(first['model_ms'])}초</b>, 접수부터 DB 결과 저장까지<b>{seconds(first['submit_to_db_result_ms'])}초</b>, 브라우저 최초 완료 관찰은<b>{seconds(first_observation['browser_first_visible_ms'])}초</b>였습니다. 마지막 관찰 간격3초가 있어 정확한 표시 순간과 차이가 날 수 있습니다.</p><p>개선 후 제출의 모델 처리는<b>{seconds(child['model_ms'])}초</b>, 접수부터 DB 결과 저장까지<b>{seconds(child['submit_to_db_result_ms'])}초</b>였습니다. 브라우저는<b>{seconds(child_observation['last_pending_observed_ms'])}초</b>에 처리 중을 확인했고<b>{seconds(child_observation['browser_first_observed_ms'])}초</b>에 완료를 처음 관찰했습니다. 따라서 화면 전환 시점은 그 사이<b>{seconds(child_observation['observation_window_ms'])}초 관찰 구간</b>안에 있으며70.687초를 정확한 렌더 완료 시점으로 보지 않습니다. <b>두 건 모두30초 목표 미달</b>입니다.</p><p>첫 질문 답변은 가격 숫자가 보이지 않아 판독을 확정할 수 없다고 설명했습니다. 개선 후 질문은 새 라벨 기준과 새 Reference 적용을 요청했고, 새 분석에서 해당 조건의 관찰을 확인했습니다. 이전 제출의 적용 기준과 Reference는 별도로 보존됩니다. 두 실제 분석 성공과 전체 기능·디자인·문서 최종 인수는 구분합니다.</p><p class="compact">근거: <a href="../../../execute/workHitory/integration-concept-03/actual-ai.json">실제 AI 실행 기록</a> · <a href="../../../execute/designReview/concept-03/evidence/first-latency.json">첫 브라우저 관찰</a> · <a href="../../../execute/designReview/concept-03/evidence/child-latency.json">재제출 관찰 구간</a> · <a href="../../../execute/workHitory/integration-concept-03/browser.md">시안03 실제 기능 인수 기록</a>.</p>'''
s=s.replace('<h3>권한과 자료 취급</h3>',latency+'<h3>권한과 자료 취급</h3>',1)
# 일반 시연과 실제 완료된 사례를 구분해 정확한 역할/매장/기준 흐름을 안내한다.
s=s.replace('<li><strong>영업 준비 · hq.demo 또는 ofc.north</strong>음료 기준과 Reference를 확인합니다.', '<li><strong>영업 준비 · hq.demo 또는 ofc.south</strong>별하천점·음료 기준과 Reference를 확인합니다.',1)
s=s.replace('<li><strong>첫 점검 · owner.north</strong>','<li><strong>첫 점검 · owner.south</strong>',1)
s=s.replace('버튼을 열고 봄빛역점·음료를 선택합니다.','버튼을 열고 별하천점·음료를 선택합니다.',1)
s=s.replace('<li><strong>개선 사진</strong>','<li><strong>새 기준과 개선 사진</strong>실제 시연에서는 본사가 라벨 기준 qa03_labels와 매장 Reference를 v2로 바꾼 뒤, 점주가 이전 결과에서 재제출을 시작했습니다. ',1)
s=s.replace('<li><strong>현장 확인 · ofc.north</strong>','<li><strong>현장 확인 · ofc.south</strong>',1)
s=s.replace('regional.north / hq.demo','regional.south / hq.demo',1)
p.write_text(s)
(ROOT/'execute/workHitory/manuals-others/concept03-image-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('03 정상 원본 이미지 반영:',len(manifest))
