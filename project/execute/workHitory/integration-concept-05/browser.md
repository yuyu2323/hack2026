# 시안 05 실제 브라우저 인수

root / RUNNING. 공통 로컬 테스트 DB/API8000/AI8010/시안5177.
가상 사진과 합성 질문의 사용자 승인된 실제 AI 검증. 노을공원점/음료에 QA05 동일 키 4단계 기준과 Reference를 등록하고 전후 제출·버전 보존·관리자 조치·권한·운영 복구를 확인한다.
실제 UI·메타데이터·단위 검사·독립 디자인 검수는 구분한다.

## E01 첫 실제 분석과 입력 경계
- HQ/REGION/STORE/CATEGORY에 동일 `qa05_labels`를 UI로 등록. 노을공원점/음료의 CATEGORY v1이 첫 제출 스냅샷에 적용됨. Reference v1 dd5e826b-618a-4f55-8777-34eb3d9e81db 등록, 이미지 미리보기 확인.
- 모바일 390×844: 복수 사진 순서 변경/삭제, JPEG·PNG 외 텍스트 파일 거부와 기존 정상 사진 보존, 실제 키 입력의 2000자 상한, 키보드 Tab/Enter 제출, 중복 제출 방지 비활성 상태 확인.
- 첫 제출 `3fdb0cf3-61da-4008-84c1-79e2a58cde05`: 실제 AI/gpt-6-astra, 1사진·5기준·2Reference, 준수율60%/판단가능률100%. 질문 답변, 앞줄·간격 개선과 가격 숫자 판단 한계, 기준별 사진 근거 확인. 적용 기준 펼침의 원본1+Reference2 모두 자연크기>0로 로드.
- 모델60,273ms / 큐905ms / 실행60,393ms / 제출→DB61,422ms / 브라우저 성공확인63,181ms(직전 기록된 대기51,315ms; 관측구간11,866ms). 30초 목표 미달. `actual-ai.json`, `evidence/latency-first.json` 및 processing/delayed/result PNG 참조.
- 점주 문의 `4ae73b80-bf44-4828-92a9-3e9c9ee4c218` 등록, 자동 OFC 확인 `bb7ad441-02b2-4415-a915-46cff983e2e9`와 별개 연결 이력 보존.

## E03 새 기준·Reference 준비
- CATEGORY `1750bc1d-332f-472e-9f0f-528d5f632844`를 UI v2로 변경: 라벨 전체 노출·상품군·고른 앞줄 간격. 변경 사유와 v1 보존 목록 확인.
- Reference 사진 beverage-reference-02와 설명을 새 v2 `881d5e08-0690-41c4-8f6d-cf67a5d744fc`로 저장. 기존 v1 별도 보존. child에서 실제 반영 검증 예정.

## E02 실제 재제출 및 비교
- child `b0dbd6a2-3b6c-4442-8b57-902448539127`, parent 첫 제출에 연결. 부모 매장/카테고리 선택 비활성, 개선 사진과 새 질문 등록, 첫 사진을 재사용하지 않음.
- 실제 AI 모델63,876ms / 큐1,953ms / 실행64,011ms / 제출→DB66,097ms, 1사진·5기준·2Reference. 준수100%/판단가능100%. 변경된 qa05_labels v2와 Reference v2 로드 완료 확인. 분석은 이전 검토 기록 기준의 비교라는 한계와 기준 변경 시 직접 비교 불가를 명시한다.
- 브라우저 성공은 확인했으나 직후 타이머 변수 기록 오류가 있어 후속94,159ms를 보수적 상한으로 기록. 마지막 snapshot으로 확정된 pending56,504ms와 관측구간37,655ms. waitFor 예외를 pending 확정 증거로 쓰지 않는다. 30초 미달 판정은 정확한DB/모델 시간에도 성립한다.
- 비교 화면은 양쪽 제출 날짜(20:52/20:59), 60→100%, facing/shelf_gap 개선됨, qa05_labels v1→v2 비교불가 표시. 모바일 명명된 기준별변화 region(tabIndex0), ArrowRight에 scrollLeft0→40, 문서375px/viewport390으로 전체 가로넘침 없음.
- child 자동 OFC 확인 `c4ecb6f5-d284-42f4-bf90-d641e71097e3`. 관리자 조치와 알림 후속 검증 중.
- `vp-mobile390-first-result.png`는 도구 촬영 흰 화면으로 시각 증거에서 제외한다. 정상 결과 fixed 촬영으로 대체 예정.

### 관리자 확인과 조치·알림 연결 완료
- OFC.south 현재 담당매장2개. 노을공원/음료로 필터→주소 복사 성공 status→이력 링크의 지역/매장/카테고리/기간/상태 유지→child 상세의 사진1 앵커와 원본사진 표시→연결된 확인이슈 이동.
- child OFC 확인에 의견 저장 후 해결 내용과 함께 해결 상태 저장. 별도 의견과 해결 의견의 작성자/날짜/본문 두 이력이 보존됨.
- owner.south 알림 대상 확인으로 해당 해결이슈 연결, 점주 화면에는 수정 폼 없음. 해당 알림 읽음 및 읽지 않은 알림16→15 확인.
- 실제 비교표는 모바일390에서 키보드 초점과 ArrowRight로 scrollLeft0→312(max312), 문서 가로넘침 없음. `comparison-right-fixed`와 `desktop1440-comparison-versions-fixed`가 전체 변화/버전 행의 최종 캡처. 이전 right/versions는 일부만 보이는 보조 캡처.
- 첫 v1 기준과 Reference를 변경 후 다시 펼쳐 v1문구/이미지 로드 확인. `first-result-fixed`는 정상60% 결과, 원래 흰 first-result는 사용 금지.

### 분석 경계와 기간 집계
- OFC 전체 Mock 분석 n6/r=-0.5832, 결측0/판단불가제외2, 실제와Mock 주간 평가 수 구분.
- 노을공원/음료 n3, Mock매출250,000 동일→r — 및 값의 변화가 없어 계산불가 안내.
- 같은 매장 생활용품 n0/표본부족, 비교자료없음, 집계0/0·준수/판단가능/매출 모두 —. 비교 단위를 지역으로 바꾸면 가상남부권 집계 표시.
- Mock·상관관계가 인과나예측을 뜻하지 않는 안내와 명명된 원자료표 제공 확인. 30초 지연/unknown/기술실패/통신실패는 별도 상태이며, 미검증 상태를 완료 처리하지 않는다.

### 범위/정리
- regional.south 현재 남부3점, OFC.south 담당2점, HQ 전체6점. 지역 관리자의 북부 첫04 제출 직접 경로는 접근불가 화면, 본문0/이미지0. 시작화면 링크를 통해 로그인으로 복귀 가능.
- QA05 HQ/REGION/STORE 기준3개는 기능 검증 후 UI 사유와 함께 비활성화 확인, CATEGORY v2만 유지. 과거스냅샷은 보존됨.
- 독립 pair 검수35 PASS: 실제worker 입력projection+출력strict검증, 첫 결과/스냅샷 해시보존, child previous_review 일치, 4단계 후보 중CATEGORY선택 및Referencev1→v2원본hash검증. 도구 초기projection오류는 별도기록이며 제품결함아님.

## E04 현재 권한 즉시 반영
- UI생성 계정 qa05.owner.6f6771b2 / b979fd3d-661c-45eb-8c4d-f3c1dd155aa9. 비밀번호는 .local/browser-qa-credentials0600에만 저장, 출력/캡처 금지. localhost 운영자와127.0.0.1 QA 로그인으로 쿠키 분리.
- 노을공원1점 연결→QA 기존세션에서 첫 실제사진/결과 로드→운영자비활성→QA새로고침 시 로그인화면·본문0/사진0. 재활성/새로그인→동일사진접근→연결종료→기존세션새로고침접근불가·본문0/사진0. 재로그인 미연결홈0건 확인.
- 점주로 로그인한 채 남부OFC로 역할변경→기존점주경로거부→허용OFC시작→현재0매장/후보새봄로점만→사유로내관리매장등록→현재1매장/후보없음.
- 검증 후 운영자가 점주로복원하며 시험용OFC연결1개종료(v6→v7), 감사펼침에 actor/대상/사유/전후role/연결/ended_mapping_ids보존. 이어지역도NULL로복원(v8), 현재활성점주/미연결/지역없음. QA브라우저로그아웃·탭닫기완료. 기존 데모매장 담당자는 훼손하지 않음.
- QA별도탭 실제viewport1280×720. 해당 캡처는1280파일명이며1280×800검수와구분한다.
- 독립실제HTTP23확인/GET15 PASS. 실제media_id3111f4ec-d4d5-4f14-9bf8-7ecd2552f9f5의 점주원본200/hash일치·thumbnail200 대비 운영자403/북부지역404. 제출·이슈본문도 운영자403/범위밖404. `independent-http-review.md`참조. 브라우저기록과HTTP증거를구분함.

## E05 실패 복구
- 작업 aa73ad7e-9d08-5a5b-b035-96941a217621 / 제출96165c7c-53c9-5ded-9f99-f9ee67ec2c86은 Mock 장애 fixture. 첫실패AI_UNAVAILABLE/11초 보존, 사유공란 native required 오류, 사유입력 UI재처리→시도2 running→succeeded/결과반영예.
- 처리중/성공에는 재처리폼없고 상태안내만 표시. 운영자화면은 영업본문없이 기술metadata만표시. 과거오류/시각과새시도의기한/수용여부보존.
- 새시도실제AI/gpt-6-astra 모델50,635ms/큐520ms/run48,786ms. fixture=true, 최초접수가9월10일인 제출→DB994,545,750ms는 정상제출 성능 집계에서 제외. 모델/run차이는 독립검토중. `actual-ai.json`3행, retry-running/success-appliedPNG 참조.

### 기준 정보·운영 경로
- qa05_test_category 생성→QA05 검증 완료 분류로 이름변경/비활성 저장. 코드와과거기록보존안내확인.
- operator.demo의 owner첫결과직접경로는접근불가/사진0/질문없음,시작화면은운영홈. 실제HTTP403검사와별도기록.
- QA05 탐색과 비교 시연 안내 공지저장(화면의게시시작2026-09-21 21:17KST),운영배너노출확인. 점주노출과비활성정리후속예정.

### 후속 상태·공지와 계측 정정
- 360×800: Mock unknown77dba30a-92e6-52bf-9c12-fe7deb056ffb 준수—/판단0%/0of4/OFC·재촬영, 기술실패e3488415-6745-56a8-be69-7d3010521033 평가제외/복구안내, 새봄로/간편식0건 미제출안내를 실제UI에서 구분. 파일명owner-empty는상단범위만보여빈결과시각증거로쓰지않음(기존1280unmapped-empty는정상).
- QA05 공지 점주배너노출·종료된시연점검미노출확인. 테스트후QA05공지비활성저장확인. 1280×800운영홈 문서1265px로가로넘침없음. E06통신실패/긴queued, E08실제200%/preview/HTML렌더는미실행.
- 독립운영15검사기능PASS: QA계정v8/지역NULL/미연결, OFC연결종료감사, categoryv2비활성, retry실패1/성공2적용, 첫/childhash보존.
- CLOCK_BASIS_ANOMALY: adapter단조시계50,635ms와UTC시작→종료48,786ms의1,849ms역전은원본값그대로보존. 단순범위·반올림만으로설명되지않으며NTP등원인미확정. FUNCTIONAL_PASS_WITH_TIMING_ANOMALY로분리한다(`independent-operations-review.md`). 신규제출정상성능표본에서는fixture전체접수기간을제외한다.
