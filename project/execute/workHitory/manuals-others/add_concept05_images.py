"""시안05의 직접 열람한 정상 화면12장을 실제 제출·비교·조치 흐름에 연결한다."""
from pathlib import Path
from html import escape
import hashlib, json, shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MANUAL = ROOT / 'deliverables/manuals/concept-05'
SOURCE = ROOT / 'execute/designReview/concept-05/evidence'
ASSETS = MANUAL / 'assets'
ASSETS.mkdir(exist_ok=True)
SHOTS = {
    'home': ('vp-mobile390-owner-home.png',
        '점주 제출 이력 탐색 첫 화면. 접힌 범위 탐색, 사진으로 점검하기 버튼, 처리 상태 선택과 상태 적용, 사진 썸네일 이력이 보입니다.',
        '점주 · 제출 이력 탐색 · 390×844 viewport. 시안05는 이력에서 시작합니다. 범위 탐색을 펼쳐 매장과 기간을 좁히고, 사진으로 점검하기에서 새 기록을 만듭니다. 이 화면에 보이는 과거 음료 기록은 이번 QA05 신규 제출 결과가 아닙니다.', 'mobile'),
    'preview': ('vp-mobile390-upload-preview.png',
        '음료 사진 제출 폼의 beverage-before-01.png 미리보기, 사진1·2251KiB 정보, 비활성 앞으로 버튼과 사진1 삭제, 질문 입력 영역.',
        '점주 · 사진 선택과 질문 · 390×844 viewport. 사진 번호·파일명·미리보기로 실제 선택을 확인합니다. 한 장일 때 앞으로 이동은 비활성이고 삭제는 가능합니다. 같은 폼의 아래 질문 또는 현장 상황을 입력한 뒤 사진 제출하기를 누릅니다.', 'mobile'),
    'invalid': ('vp-mobile390-invalid-photo.png',
        '사진 선택 아래 JPEG 또는 PNG 사진만 선택해 주세요 오류가 표시되며, 이전에 선택한 정상 beverage-before-01.png 사진은 남아 있습니다.',
        '점주 · 사진 형식 오류 · 390×844 viewport. 허용되지 않은 형식을 선택하면 JPEG 또는 PNG 사진만 선택해 주세요 안내가 나옵니다. 이미 선택한 정상 사진은 유지되므로 목록을 확인하고 허용 형식의 사진을 다시 고릅니다. 분석 결과나 서버 기술 실패를 뜻하는 오류는 아닙니다.', 'mobile'),
    'processing': ('vp-mobile390-processing-delayed.png',
        '노을공원점 음료 점검 결과가 분석 중이며60초 경과, 시간이 더 필요하다는 안내, 상태를 다시 확인 버튼과 제출 질문이 표시됩니다.',
        '점주 · 실제 제출 처리 중 · 390×844 viewport. 60초 경과 시 지연 안내가 보입니다. 상태를 다시 확인하거나 이력에서 다시 열 수 있습니다. 이 캡처에는 완료된 점수와 답변이 아직 표시되지 않습니다.', 'mobile'),
    'dashboard': ('vp-desktop1440-hq-dashboard.png',
        '본사 매장 비교 작업영역. 왼쪽 지역·매장·카테고리·기간 탐색과 조건 적용, 오른쪽 매장별 제출/완료·준수율·판단 가능률·확인 이슈 행렬 및 이력 탐색·최신 근거 링크.',
        '본사 · 매장 비교 · 1440×900 viewport. 왼쪽에서 동일 기간과 범위를 적용하고 오른쪽 행렬에서 매장별 상태를 비교합니다. 조회 날짜는UTC, 표시 시각은Asia/Seoul입니다. 성공 평가의 Mock 포함 수를 확인하고 미제출·기술 실패를 미준수로 해석하지 마세요. 수치는 촬영 당시 값입니다.', 'desktop'),
    'guideline': ('vp-desktop1440-guidelines-four-levels.png',
        '진열 기준과 버전 화면에서 왼쪽 QA05 음료 라벨 확인 CATEGORY v1이 선택되고 오른쪽 현재v1 활성, 기준 제목·내용·변경 사유 입력이 보입니다.',
        '본사 · 기준 탐색과 편집 · 1440×900 viewport. 목록에서 선택한 매대 기준v1의 내용과 변경 사유를 확인합니다. 위 안내의 적용 우선순위와 실제 대상이 맞는지 살핀 뒤 새 버전을 저장합니다. 다른 세 단계 기준의 전체 내용이나 저장 성공까지 보여 주는 화면은 아닙니다.', 'desktop'),
    'reference': ('vp-desktop1440-reference-preview.png',
        'Reference 등록 폼에서 음료·노을공원점, beverage-reference-01.png 미리보기와 파일 정보·삭제, QA05 음료 Reference v1 설명 입력이 보입니다.',
        '본사 · Reference 등록 준비 · 1440×900 viewport. 적용 매장과 카테고리, 선택한 예시 사진 및 설명을 확인합니다. 왼쪽 목록은 다른 기존 Reference이며, 오른쪽 QA05 자료는 등록 폼의 미리보기입니다. 이 캡처만으로 저장 완료를 뜻하지 않습니다.', 'desktop'),
}
SHOTS.update({
    'operator_home': ('vp-desktop1440-operator-home.png',
        '플랫폼 운영자의 상태와 연결 탐색에서 점주 연결 누락과OFC 미배정 매장, 실제 처리 작업의 상태별 수치, 별도 Mock 장애 사례와 작업 탐색 링크가 보입니다.',
        '플랫폼 운영자 · 상태와 연결 탐색 · 1440×900 viewport. 계정과 매장의 연결 누락을 확인하고 필요한 계정·연결 업무로 이동합니다. 실제 처리 작업과 Mock 장애 사례는 따로 집계됩니다. 이 역할은 영업 사진·질문·평가 본문을 열람하지 않으며 수치는 촬영 당시 값입니다.', 'desktop'),
    'operator_retry': ('vp-desktop1440-retry-success-applied.png',
        'Mock 장애 작업의 보존된 시도1은AI_UNAVAILABLE 기술 실패·결과 반영 아니오, 시도2는분석 완료·오류 없음·결과 반영 예이며 대기·처리 중·성공 작업 재처리 불가 안내가 보입니다.',
        '플랫폼 운영자 · 재처리 결과와 시도 이력 · 1440×900 viewport. 연습용 장애 작업의 첫 실패는 보존되고 두 번째 시도는 완료돼 결과가 반영됐습니다. 성공 상태에는 재처리 폼 대신 재처리할 수 없다는 안내가 나타납니다. 과거에 접수된 Mock 장애 사례이므로 최초 접수부터의 기간을 새 사진 분석 성능으로 사용하지 않습니다.', 'desktop'),
    'first': ('vp-mobile390-first-result-fixed.png',
        '첫 음료 점검의 실제 AI 분석, 준수율60%·판단 가능률100%·판단 가능한 기준5/5, 중단 빈 공간과 앞줄 정렬 개선 답변 및 가격 숫자 판독 한계.',
        '점주 · 첫 실제 결과 · 390×844 viewport. 중단 초록 캔과 은색 캔 사이의 빈 공간, 앞줄 위치·간격·그림 방향을 먼저 확인합니다. 준수율60%와 판단 가능률100%를 함께 읽으며, 사진에서 가격 숫자를 확인할 수 없다는 한계를 별도로 확인합니다.', 'mobile'),
    'child': ('vp-mobile390-child-result.png',
        '개선 후 실제 AI 분석에서 준수율100%·판단 가능률100%·5/5, 빈 공간과 앞줄 개선 답변, 이전 사진이 아닌 이전 기록 기준 비교 및 가격 추정 제외 설명.',
        '점주 · 개선 후 실제 결과 · 390×844 viewport. 새 기준을 포함한5개 기준이 준수로 평가됐습니다. 이전 사진이 모델에 다시 제공된 것은 아니며 이전 평가 기록과 비교했다는 한계를 읽습니다. 가격은 사진 밖 정보로 추정하지 않습니다.', 'mobile'),
    'comparison': ('vp-desktop1440-comparison-dates.png',
        '점주 이전·이후 비교 화면에 기준이 달라 점수 비교에 주의하라는 안내와20시52분 이전 제출60%,20시59분 개선 후 제출100%, 양쪽 사진 상단이 나란히 보입니다.',
        '점주 · 전후 비교 상단 · 1440×900 viewport. 양쪽 제출 날짜와 준수율·판단 가능률을 함께 확인합니다. 표시 시간대는Asia/Seoul이며, 두 사진의 나머지 부분과 기준별 변화는 아래로 내려 살펴봅니다. 적용 기준이 달라 전체 점수 차이를 동일 조건의 효과로 단정하지 않습니다.', 'desktop'),
    'versions': ('vp-desktop1440-comparison-versions-fixed.png',
        '기준별 변화 표 전체. facing v2→v2와shelf_gap v1→v1은 개선됨, qa05_labels는v1→v2로 바뀌어 비교 불가이고 나머지 준수 항목은 변화 없음입니다.',
        '전후 비교 · 기준 버전과 변화 · 1440×900 viewport. 앞면 정렬과 빈 공간은 같은 버전에서 개선됐습니다. qa05_labels는 양쪽 모두 준수여도 기준이 바뀌어 직접 비교하지 않습니다. 표 아래 설명 역시 이전 검토 기록에 근거한 비교임을 밝힙니다.', 'desktop'),
    'mobile_comparison': ('vp-mobile390-comparison-right-fixed.png',
        '모바일 비교표에 주황색 키보드 초점 테두리와 오른쪽 끝으로 이동한 가로 스크롤이 보이며 이후 기준 버전·판정·변화 열에서 개선됨과 비교 불가를 읽을 수 있습니다.',
        '점주 · 모바일 비교표 오른쪽 · 390×844 viewport. 기준별 변화 표에 초점을 두고 오른쪽 방향키 또는 표 내부 가로 스크롤로 마지막 열까지 이동합니다. 이 구간에는 이후 버전·판정·변화가 보이며 기준 이름과 이전 값은 왼쪽으로 돌아가 확인합니다.', 'mobile'),
    'ofc_resolved': ('vp-desktop1440-ofc-resolved.png',
        'OFC.south의 노을공원점·음료 확인 이슈가 해결 상태이며 개선 사진 확인과 별도 가격 확인의 해결 내용, 원본 보기와 담당·상태·조치 의견 폼이 보입니다.',
        'OFC · 확인 이슈 해결 후 · 1440×900 viewport. 개선 사진을 확인한 내용을 남기고 해결 상태로 저장한 예입니다. 앞줄·간격·라벨 노출은 유지하며 가격은 현장에서 별도로 확인하도록 기록했습니다. 담당자는 상태와 추가 조치 의견을 관리할 수 있습니다.', 'desktop'),
    'owner_resolved': ('vp-mobile390-owner-resolved.png',
        '점주 확인 문의에서 노을공원점·음료 이슈의 해결 배지, 해결 내용, 원본 사진·평가·기준 보기와OFC 조치 이력 시작이 표시되고 관리 수정 폼은 없습니다.',
        '점주 · 해결 내용 다시 확인 · 390×844 viewport. 내 알림의 대상 확인으로 연결된 이슈를 열어 해결 내용과 OFC 조치 이력을 읽습니다. 원본 사진·평가·기준도 함께 확인할 수 있으며, 점주에게 담당·상태 변경 폼은 제공되지 않습니다. 이력의 나머지 내용은 아래로 내려 확인합니다.', 'mobile'),
})
manifest = []
def figure(key):
    name, alt, caption, kind = SHOTS[key]
    source, dest = SOURCE / name, ASSETS / name
    shutil.copyfile(source, dest)
    with Image.open(dest) as im:
        width, height = im.size
        actual_format = im.format
    data = dest.read_bytes()
    manifest.append({'key': key, 'source': str(source.relative_to(ROOT)), 'manual_asset': str(dest.relative_to(ROOT)),
        'sha256': hashlib.sha256(data).hexdigest(), 'width': width, 'height': height, 'actual_format': actual_format,
        'source_bytes_equal': source.read_bytes() == data, 'alt': alt, 'caption': caption,
        'inspection': '작성자 직접 원본 열람, 변형 없이 그대로 복사'})
    return f'<figure class="screen-{kind}" id="screen-{key}"><a href="assets/{name}" aria-label="{escape(alt, quote=True)} 원본 열기"><img src="assets/{name}" width="{width}" height="{height}" alt="{escape(alt, quote=True)}" loading="lazy"></a><figcaption>{escape(caption)} <a href="assets/{name}">원본 보기</a></figcaption></figure>'

p = MANUAL / 'index.html'
s = p.read_text()
assert 'id="screen-home"' not in s, 'generate_drafts.py 05의 초안에서 시작하세요.'
def once(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)

once('<h3>접수와 결과 확인</h3>', '<div class="shot-pair">' + figure('home') + figure('preview') + '</div><h3>접수와 결과 확인</h3>')
once('<h3>개선 후 다시 제출하고 비교</h3>', '<div class="shot-pair">' + figure('first') + figure('child') + '</div><h3>개선 후 다시 제출하고 비교</h3>')
once('</section><section id="business"', figure('comparison') + figure('versions') + '</section><section id="business"')
once('<h3>담당 매장 연결 · OFC</h3>', figure('dashboard') + '<h3>담당 매장 연결 · OFC</h3>')
once('<h3>추이·비교·기본 집계</h3>', figure('ofc_resolved') + figure('owner_resolved') + '<h3>추이·비교·기본 집계</h3>')
once('<h3>계정과 연결</h3>', figure('operator_home') + '<h3>계정과 연결</h3>')
once('<h3>감사 이력과 공지</h3>', figure('operator_retry') + '<h3>감사 이력과 공지</h3>')
once('</section><section id="data"', figure('mobile_comparison') + '</section><section id="data"')
once('</style>', '.shot-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;align-items:start}.screen-mobile{max-width:390px;margin:24px auto}.screen-desktop{margin:24px 0}figure a{display:block}figcaption a{display:inline}figure img{height:auto}.shot-pair figure{min-width:0;width:100%}@media(max-width:600px){.shot-pair{grid-template-columns:1fr}}</style>')
once('data-manual-status="draft-not-run"', 'data-manual-status="review-partial-images"')
once('초안 · 화면 캡처/브라우저 문서 검증 NOT_RUN', '검수 중 · 실제 화면 12장 / 문서 브라우저 검수 대기')
once('초안 · 실제 화면 캡처와 문서 렌더 검증 NOT_RUN', '실제 화면 12장 반영 · 문서 렌더 검증 NOT_RUN')
once('최종 브라우저 인수와 완성 화면 캡처가 아직 인계되지 않았으므로 이 문서에는 화면 이미지를 넣지 않았습니다. 빈 그림 틀이나 다른 시안 사진을 실제 화면처럼 제공하지 않습니다.', '직접 확인한 시안05 정상 viewport 캡처12장을 업무 설명에 연결했습니다. 이력 탐색·사진 선택, 첫 실제 결과와 재제출 결과, 전후 날짜·기준 버전 및 모바일 표 탐색, 본사 매장 행렬과 OFC·점주의 해결 내용, 운영자 상태·연결 및 실패 재처리 이력을 보여 줍니다. 첫 분석·재제출·과거 적용 자료 보존과 조치·알림 흐름의 실제 기록을 확인했습니다. 운영자 홈과 첫 실패·두 번째 성공이 보존된 재처리 결과를 반영했습니다. 전체 기능·디자인 및200% 확대·최종 문서 브라우저/오프라인 렌더 검수는 별도 대기입니다.')
once('로그인·점주 제출/결과·관리/운영의 해당 시안 실제 캡처</td><td>NOT_RUN · root가 최종 vp-*.png 인계 후 반영', '이력·사진 선택·실제 결과·비교·영업·조치·운영 실제 캡처</td><td>정상12장 반영 · 200%/문서 브라우저 검수 NOT_RUN')
once('실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>root의 시안별 검증 결과 인계 대기', '실제 앱 전체 흐름·실제 AI·지연 목표 인수</td><td>첫 분석·재제출 succeeded · 두 건 모두30초 목표 미달 · 전체 인수 진행 중')
once('독립 디자인 최종 PNG 검수</td><td>contract_ai 재검수 결과 인계 대기', '독립 디자인 최종 PNG 검수</td><td>정상 화면별 독립 검수와 후속 대조 진행 · 전체 판정 대기')
once('외부 CDN/스크립트 없음 · 실제 화면 인계 후 갱신', '외부 CDN/스크립트 없음 · 실제 화면 12장 반영 · 200%/최종 문서 검수 대기')
once('시안별 실제 측정값과 표본은 검증 완료 자료에서 확인해야 하며, 이 초안은 실제 지연 성능을 확정하지 않습니다.', '시안별 측정값은 모델 처리·DB 저장·브라우저 관찰을 구별해 읽어야 합니다. 아래 실제 분석 두 건의 실행 정본과 관찰 구간을 구별해 표시했습니다. 이 표본으로 일반적인 처리 성능을 확정하지 않습니다.')
actual = json.loads((ROOT / 'execute/workHitory/integration-concept-05/actual-ai.json').read_text())
first = next(r for r in actual if r['submission_id'] == '3fdb0cf3-61da-4008-84c1-79e2a58cde05')
child = next(r for r in actual if r['submission_id'] == 'b0dbd6a2-3b6c-4442-8b57-902448539127')
assert first['status'] == child['status'] == 'succeeded'
assert first['source_kind'] == child['source_kind'] == 'real_ai'
obs = json.loads((SOURCE / 'latency-first.json').read_text())
child_obs = json.loads((SOURCE / 'latency-child.json').read_text())
sec = lambda ms: f'{ms / 1000:.3f}'
latency = f'''<h3>시안 05 실제 분석과 개선 후 제출</h3><p>노을공원점·음료의 첫 사진과 개선 사진을 각각 사진1장·기준5개·Reference2개로 실제 분석했습니다. 첫 준수율은<b>60%</b>, 개선 후 준수율은<b>100%</b>이고 두 결과의 판단 가능률은<b>100%</b>입니다. 같은 기준 버전의 앞면 정렬(<code>facing</code>)과 빈 공간(<code>shelf_gap</code>)은 개선됐습니다. <code>qa05_labels</code>는 v1→v2로 바뀌어 양쪽 모두 준수여도 직접 비교하지 않습니다. 합성 사진 한 쌍의 결과로 일반 정확도를 보장하지 않습니다.</p><p>첫 모델 처리는<b>{sec(first['model_ms'])}초</b>, 접수부터 DB 저장까지<b>{sec(first['submit_to_db_result_ms'])}초</b>였습니다. 브라우저는<b>{sec(obs['last_pending_ms'])}초</b>에 처리 중을 관찰하고<b>{sec(obs['first_observed_ms'])}초</b>에 완료를 처음 관찰했으며 그 사이<b>{sec(obs['observation_window_ms'])}초</b>의 관찰 구간이 있습니다. 최초 완료 관찰은 정확한 화면 표시 순간이 아닙니다.</p><p>재제출 모델 처리는<b>{sec(child['model_ms'])}초</b>, 접수부터 DB 저장까지<b>{sec(child['submit_to_db_result_ms'])}초</b>였습니다. 브라우저는<b>{sec(child_obs['last_confirmed_pending_ms'])}초</b>에 처리 중임을 확정했고 이후 완료를 확인했지만, 완료 직후 타이머 변수 기록에 오류가 있었습니다. 따라서 후속 시각<b>{sec(child_obs['visible_completed_upper_ms'])}초</b>를 <b>보수적 상한</b>으로 남겼으며, 확인된 대기 시각과의 구간은<b>{sec(child_obs['observation_window_ms'])}초</b>입니다. 94.159초를 정확한 완료 또는 렌더 시간으로 사용하지 않습니다. <b>두 건 모두30초 목표 미달</b>이며 이 판단은 정확한 모델·DB 시간에서도 성립합니다.</p><p>첫 답변은 사진에서 가격 숫자를 확인할 수 없다고 설명했고, 개선 후 답변도 가격을 추정하지 않았습니다. 개선 후 분석에는 현재 사진과 이전 평가 기록을 사용했으며 이전 사진 원본을 다시 제공한 비교는 아닙니다. 기준·Reference를 새 버전으로 바꿔도 첫 제출의 적용 자료는 남아 있습니다. OFC의 해결 내용 역시 가격 확인은 현장에서 별도로 진행한다고 구분했습니다.</p><p class="compact">근거: <a href="../../../execute/workHitory/integration-concept-05/actual-ai.json">실제 AI 실행 기록</a> · <a href="../../../execute/designReview/concept-05/evidence/latency-first.json">첫 브라우저 관찰 구간</a> · <a href="../../../execute/designReview/concept-05/evidence/latency-child.json">재제출 관찰 상한</a> · <a href="../../../execute/workHitory/integration-concept-05/browser.md">시안05 실제 기능 인수 기록</a>. 운영 복구 그림은 별도 장애 사례의 기능 확인이며 위 신규 제출 성능 표본에 포함하지 않습니다. 200% 확대 및 전체 문서 브라우저 검수는 NOT_RUN입니다.</p>'''
once('<h3>권한과 자료 취급</h3>', latency + '<h3>권한과 자료 취급</h3>')
once('<li><strong>영업 준비 · hq.demo 또는 ofc.north</strong>음료 기준과 Reference를 확인합니다.', '<li><strong>영업 준비 · hq.demo 또는 ofc.south</strong>노을공원점·음료 기준과 Reference를 확인합니다.')
once('<li><strong>첫 점검 · owner.north</strong>', '<li><strong>첫 점검 · owner.south</strong>')
once('봄빛역점·음료를 선택합니다.', '노을공원점·음료를 선택합니다.')
once('<li><strong>현장 확인 · ofc.north</strong>', '<li><strong>현장 확인 · ofc.south</strong>')
once('regional.north / hq.demo', 'regional.south / hq.demo')
once('<li><strong>개선 사진</strong>', '<li><strong>새 기준과 개선 사진</strong>실제 시연에서는 본사가 qa05_labels 기준과 매장 Reference를 v2로 변경한 뒤, 점주가 이전 결과에서 후속 제출을 시작했습니다. ')
p.write_text(s)
(ROOT / 'execute/workHitory/manuals-others/concept05-image-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('05 정상 원본 이미지 반영:', len(manifest))
