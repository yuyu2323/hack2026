"""직접 열람한 시안04 viewport 원본 10장을 사용자 업무와 연결한다."""
from pathlib import Path
from html import escape
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MANUAL = ROOT / 'deliverables/manuals/concept-04'
SOURCE = ROOT / 'execute/designReview/concept-04/evidence'
ASSETS = MANUAL / 'assets'
ASSETS.mkdir(exist_ok=True)
SHOTS = {
    'home': ('vp-mobile390-owner-home.png',
        '점주 홈의 사진으로 점검하기 대표 버튼, 연결된 봄빛역점과 은행길점 카드, 홈·사진 제출·이력·문의·더보기 하단 메뉴.',
        '점주 · 모바일 홈 · 390×844 viewport. 큰 사진으로 점검하기 버튼에서 네 단계 제출을 시작합니다. 아래 연결 매장 카드에서도 해당 매장으로 들어갈 수 있습니다.', 'mobile'),
    'preview': ('vp-mobile360-upload-fixed.png',
        '사진 단계에 snack-after-01.png 한 장의 미리보기와 파일명·1.9MB가 보이며 앞뒤 이동과 삭제 버튼이 카드 안에서 두 줄로 배치됩니다.',
        '점주 · 개선 사진 선택 · 360×800 viewport. 파일 선택 칸이 초기화되어도 아래 미리보기와 파일 정보가 선택 목록을 나타냅니다. 사진이 한 장이면 순서 이동은 비활성이고 삭제는 가능합니다. 다음 단계 버튼 전체는 이 구간 밖에 있으므로 아래로 내려 확인합니다.', 'mobile'),
    'processing': ('vp-mobile390-processing-delayed.png',
        '스낵 진열과 가격 숫자에 대한 현장 질문 아래 분석 중·접수 후54초 및 시간이 더 필요하며 이력에서 확인할 수 있다는 안내.',
        '점주 · 첫 실제 분석 대기 · 390×844 viewport. 54초가 지난 상태에서 지연 안내가 표시됩니다. 아직 결과가 확정되지 않았으며, 화면을 나가도 이력에서 접수된 기록을 다시 열 수 있습니다.', 'mobile'),
    'first': ('vp-mobile390-actual-result.png',
        '첫 스낵 제출의 실제 AI 분석 완료, 상품군 혼재·앞줄 간격·선반 라벨 가림 요약, 준수율0%와 판단 가능100%, OFC 확인 안내.',
        '점주 · 첫 실제 결과 · 390×844 viewport. AI가 판단한 5개 기준은 모두 개선 필요로 표시되었습니다. 준수율0%와 판단 가능률100%를 함께 읽고 아래 기준별 사진 근거와 행동을 확인합니다. 이 점수가 모델의 일반 정확도를 뜻하지는 않습니다.', 'mobile'),
    'child': ('vp-mobile360-child-result.png',
        '개선 후 스낵 제출의 현장 질문과 실제 AI 분석 완료, 기준5개 준수, 준수율100%와 판단 가능100%, 이전 사진 부재와 기준 버전 변경의 비교 한계.',
        '점주 · 개선 후 실제 결과 · 360×800 viewport. 새 기준과 Reference를 적용한 재제출은100%로 평가됐습니다. 이전 평가 기록과의 비교이며 이전 사진을 다시 분석한 결과는 아닙니다. 바뀐 기준은 같은 조건의 개선으로 단정하지 않습니다.', 'mobile'),
    'comparison': ('vp-desktop1440-comparison.png',
        '점주 전후 비교의 이전·이후 카드에 KST 제출 날짜, 적용 기준5개 펼침, 준수율0%와100% 및 판단 가능률100%, 두 사진 상단이 나란히 보입니다.',
        '점주 · 전후 비교 상단 · 1440×900 viewport. 양쪽 제출 날짜와 준수율·판단 가능률을 확인하고 적용 기준을 펼칠 수 있습니다. 사진 전체와 아래 변화 항목은 스크롤하며 확인하세요.', 'desktop'),
    'versions': ('vp-desktop1440-comparison-versions.png',
        '기준별 변화 카드에서 같은 버전의 라벨 가림·빈 간격은 개선 완료, 스낵 봉지와 라벨 기준은 이전v1에서현재v2로 바뀌어 직접 비교 불가로 표시됩니다.',
        '전후 비교 · 기준 버전 구간 · 1440×900 viewport. 같은 v1 조건의 개선 항목과 v1→v2로 바뀐 qa04_labels를 구별합니다. 변경된 기준의 판정 차이는 동일 기준의 개선 효과로 읽지 않습니다.', 'desktop'),
    'business': ('vp-desktop1440-ofc-filtered.png',
        'OFC 현장 화면에서 조회 조건이 펼쳐져 봄빛역점·스낵이 선택되고 UTC 기간 입력과 조건 적용 버튼, 미해결 조치4건이 보입니다.',
        'OFC · 담당 범위의 현장 조회 · 1440×900 viewport. 조회 조건을 펼치고 매장·카테고리·필요한 UTC 기간을 정한 뒤 조건 적용을 누릅니다. 이 화면의 미해결 조치에서 같은 조건의 업무로 이동합니다. 집계 숫자는 촬영 당시 값입니다.', 'desktop'),
    'evidence': ('vp-desktop1440-ofc-evidence-fixed.png',
        '지역 관리자의 상세 화면에서 제출 사진·생성 이미지 배지·사진1 버튼 아래 현장 질문이 분리되고, 오른쪽에 실제 답변과 기준별 사진 근거가 보입니다.',
        '지역 관리자 · 사진과 판단 근거 · 1440×900 viewport. 사진 아래 현장 질문을 읽고 오른쪽 질문 답변과 기준별 관찰을 대조합니다. 사진 번호가 붙은 근거 버튼은 해당 사진으로 이동합니다.', 'desktop'),
    'retry': ('vp-desktop1440-retry-success.png',
        '플랫폼 운영자의 처리 상세에 분석 완료와 Mock 장애 사례, 갱신된 처리 시작·종료 시각, 첫 번째 기술 실패 시도와 결과 미반영 기록이 보입니다.',
        '플랫폼 운영자 · 실패 사례 재처리 후 · 1440×900 viewport. 준비된 Mock 장애 사례를 재처리한 뒤 현재 작업이 분석 완료로 표시되고 이전 실패 기록은 남아 있습니다. 두 번째 시도의 세부 결과 반영 정보는 이 구간 아래에서 확인합니다. 영업 사진이나 평가 본문을 보여 주는 화면은 아닙니다.', 'desktop'),
}

manifest = []
def figure(key):
    name, alt, caption, kind = SHOTS[key]
    source, dest = SOURCE / name, ASSETS / name
    shutil.copyfile(source, dest)
    with Image.open(dest) as decoded:
        width, height = decoded.size
        actual_format = decoded.format
    data = dest.read_bytes()
    manifest.append({'key': key, 'source': str(source.relative_to(ROOT)),
        'manual_asset': str(dest.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest(),
        'width': width, 'height': height, 'actual_format': actual_format,
        'source_bytes_equal': source.read_bytes() == data, 'caption': caption, 'alt': alt,
        'inspection': '작성자 직접 원본 열람, 크롭·리사이즈 없이 그대로 복사'})
    return f'<figure class="screen-{kind}" id="screen-{key}"><a href="assets/{name}" aria-label="{escape(alt, quote=True)} 원본 열기"><img src="assets/{name}" width="{width}" height="{height}" alt="{escape(alt, quote=True)}" loading="lazy"></a><figcaption>{escape(caption)} <a href="assets/{name}">원본 보기</a></figcaption></figure>'

p = MANUAL / 'index.html'
s = p.read_text()
assert 'id="screen-home"' not in s, 'generate_drafts.py 04로 이미지 없는 초안부터 시작하세요.'
def replace_once(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)

replace_once('<h3>접수와 결과 확인</h3>', '<div class="shot-pair">' + figure('home') + figure('preview') + '</div><h3>접수와 결과 확인</h3>')
replace_once('<h3>개선 후 다시 제출하고 비교</h3>', '<div class="shot-pair">' + figure('processing') + figure('first') + '</div>' + figure('child') + '<h3>개선 후 다시 제출하고 비교</h3>')
replace_once('</section><section id="business"', figure('comparison') + figure('versions') + '</section><section id="business"')
replace_once('<h3>담당 매장 연결 · OFC</h3>', figure('business') + '<h3>담당 매장 연결 · OFC</h3>')
replace_once('<h3>추이·비교·기본 집계</h3>', figure('evidence') + '<h3>추이·비교·기본 집계</h3>')
replace_once('</section><section id="states"', figure('retry') + '</section><section id="states"')
replace_once('</style>', '.shot-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;align-items:start}.screen-mobile{max-width:390px;margin:24px auto}.screen-desktop{margin:24px 0}figure a{display:block}figcaption a{display:inline}figure img{height:auto}.shot-pair figure{min-width:0;width:100%}@media(max-width:600px){.shot-pair{grid-template-columns:1fr}}</style>')
replace_once('data-manual-status="draft-not-run"', 'data-manual-status="review-partial-images"')
replace_once('초안 · 화면 캡처/브라우저 문서 검증 NOT_RUN', '검수 중 · 실제 화면 10장 / 문서 브라우저 검수 NOT_RUN')
replace_once('초안 · 실제 화면 캡처와 문서 렌더 검증 NOT_RUN', '실제 화면 10장 반영 · 문서 렌더 검증 NOT_RUN')
replace_once('최종 브라우저 인수와 완성 화면 캡처가 아직 인계되지 않았으므로 이 문서에는 화면 이미지를 넣지 않았습니다. 빈 그림 틀이나 다른 시안 사진을 실제 화면처럼 제공하지 않습니다.', '직접 확인한 시안04 정상 viewport 캡처10장을 업무 설명에 연결했습니다. 점주 홈·수정 후 사진 선택·지연 안내·첫 결과와 재제출 결과·날짜와 기준 버전 비교, OFC 조회, 지역 관리자의 사진 근거와 운영자 재처리를 보여 줍니다. 사진 제어행과 상세 질문 가림을 고친 최신 캡처를 사용했습니다. 전체 기능·디자인 및 최종 문서 렌더 검수는 별도로 진행 중입니다.')
replace_once('로그인·점주 제출/결과·관리/운영의 해당 시안 실제 캡처</td><td>NOT_RUN · root가 최종 vp-*.png 인계 후 반영', '점주 제출·결과·비교 및 영업·운영 실제 캡처</td><td>정상10장 반영 · 문서 브라우저 검수 대기')
replace_once('실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>root의 시안별 검증 결과 인계 대기', '실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>첫 분석·재제출 succeeded · 두 건 모두30초 목표 미달 · 전체 인수 진행 중')
replace_once('독립 디자인 최종 PNG 검수</td><td>contract_ai 재검수 결과 인계 대기', '독립 디자인 최종 PNG 검수</td><td>미리보기 제어행·상세 질문 가림 수정 화면 확인 · 전체 디자인 판정 대기')
replace_once('외부 CDN/스크립트 없음 · 실제 화면 인계 후 갱신', '외부 CDN/스크립트 없음 · 실제 화면 10장 반영 · 최종 문서 검수 대기')
replace_once('시안별 실제 측정값과 표본은 검증 완료 자료에서 확인해야 하며, 이 초안은 실제 지연 성능을 확정하지 않습니다.', '아래 실제 시연의 모델 처리·DB 저장·브라우저 관찰 시간은 측정 구간이 다릅니다. 이 두 건으로 일반적인 처리 성능을 보장하지 않습니다.')

actual = json.loads((ROOT / 'execute/workHitory/integration-concept-04/actual-ai.json').read_text())
first = next(r for r in actual if r['submission_id'] == 'e447d4e9-54c0-4c85-a0d6-20597b92d0ba')
child = next(r for r in actual if r['submission_id'] == '80d35004-ef2b-4d18-8618-f2199b6878a2')
first_observation = json.loads((SOURCE / 'latency-first.json').read_text())
child_observation = json.loads((SOURCE / 'latency-child.json').read_text())
assert first['status'] == child['status'] == 'succeeded'
assert first['source_kind'] == child['source_kind'] == 'real_ai'
seconds = lambda ms: f'{ms / 1000:.3f}'
latency = f'''<h3>시안 04 실제 스낵 분석과 개선 후 제출</h3><p>봄빛역점·스낵의 첫 사진과 개선 사진을 각각 사진1장·기준5개·Reference3개로 실제 분석했습니다. 첫 결과는 준수율<b>0%</b>, 개선 후 결과는<b>100%</b>였고 두 결과의 판단 가능률은<b>100%</b>였습니다. 같은 버전의 상품군·정렬·라벨 가림·간격 기준은 개선 필요에서 준수로 바뀌었습니다. 다만 <code>qa04_labels</code>는 v1→v2로 내용이 바뀌어 직접 비교 불가입니다. 전체 점수 차이를 모두 동일 조건의 개선 효과로 해석하지 마세요.</p><p>첫 분석의 모델 처리는<b>{seconds(first['model_ms'])}초</b>, 접수부터 DB 결과 저장까지<b>{seconds(first['submit_to_db_result_ms'])}초</b>였습니다. 브라우저는<b>{seconds(first_observation['last_pending_ms'])}초</b>에 처리 중을 관찰했고<b>{seconds(first_observation['first_observed_ms'])}초</b>에 완료를 처음 관찰했습니다. 관찰 간격은<b>{seconds(first_observation['observation_window_ms'])}초</b>로, 최초 완료 관찰을 정확한 화면 표시 순간으로 보지 않습니다.</p><p>개선 후 분석의 모델 처리는<b>{seconds(child['model_ms'])}초</b>, DB 저장까지<b>{seconds(child['submit_to_db_result_ms'])}초</b>였습니다. 브라우저는<b>{seconds(child_observation['last_pending_ms'])}초</b>에 처리 중, <b>{seconds(child_observation['first_observed_ms'])}초</b>에 완료를 관찰했으므로 그 사이<b>{seconds(child_observation['observation_window_ms'])}초 관찰 구간</b>이 있습니다. <b>두 건 모두30초 목표 미달</b>입니다. 이 지연은 별도 준비된 장애 작업의 재처리 시간과도 구별합니다.</p><p>합성 매대 사진 한 쌍의 실제 결과이며 모델의 일반 정확도를 검증한 결과는 아닙니다. 사진만으로 읽기 어려운 가격 숫자와 뒤쪽 재고의 한계를 함께 읽으세요. 새 분석에는 현재 사진과 고정된 이전 평가 기록을 사용하며, 이전 사진 원본을 다시 모델에 전달하는 비교는 아닙니다. 바뀐 기준·Reference는 새 제출에 적용되고 첫 제출의 적용 자료는 보존됩니다.</p><p class="compact">근거: <a href="../../../execute/workHitory/integration-concept-04/actual-ai.json">실제 AI 실행 기록</a> · <a href="../../../execute/designReview/concept-04/evidence/latency-first.json">첫 브라우저 관찰</a> · <a href="../../../execute/designReview/concept-04/evidence/latency-child.json">재제출 관찰 구간</a> · <a href="../../../execute/workHitory/integration-concept-04/browser.md">시안04 실제 기능 인수 기록</a>.</p>'''
replace_once('<h3>권한과 자료 취급</h3>', latency + '<h3>권한과 자료 취급</h3>')
replace_once('<li><strong>영업 준비 · hq.demo 또는 ofc.north</strong>음료 기준과 Reference를 확인합니다.', '<li><strong>영업 준비 · hq.demo 또는 ofc.north</strong>봄빛역점·스낵의 기준과 Reference를 확인합니다.')
replace_once('scripts/seed/assets/shelves/beverage-reference-01.png', 'scripts/seed/assets/shelves/snack-reference-01.png')
replace_once('봄빛역점·음료를 선택합니다.', '봄빛역점·스낵을 선택합니다.')
replace_once('beverage-before-01.png', 'snack-before-01.png')
replace_once('“앞줄 간격과 정렬을 확인해 주세요” 같은 질문', '“스낵 봉지의 앞면 방향과 선반 라벨 노출을 확인해 주세요” 같은 질문')
replace_once('<li><strong>개선 사진</strong>', '<li><strong>새 기준과 개선 사진</strong>실제 시연에서는 본사가 qa04_labels 기준과 매장 Reference를 v2로 바꾼 뒤, 점주가 이전 결과에서 재제출했습니다. ')
replace_once('beverage-after-01.png', 'snack-after-01.png')
p.write_text(s)
(ROOT / 'execute/workHitory/manuals-others/concept04-image-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('04 정상 원본 이미지 반영:', len(manifest))
