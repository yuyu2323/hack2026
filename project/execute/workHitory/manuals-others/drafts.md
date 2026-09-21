# 매뉴얼 01·03·04·05 작성 기록

- 상태: REVIEW · 초안 완료/정적 PASS · 화면 캡처 및 독립 검수 대기
- 체크리스트: execute/checkList/manuals-others/drafts.md
- docs02 §10의 필수 구성, docs09 E08/지연·캡처 규칙, docs10 G5와 실제 README/scripts 실행 순서를 읽었다.
- 각 시안의 app shell/role menu, 점주 제출·상세·비교, 영업 기준/Reference/담당/조치, 운영 폼 소스를 읽고 실제 버튼명을 확인했다.
- 런타임 자격 파일에서 login_id와 role만 출력해 공개 시연 ID를 확인했다. 비밀번호 값은 출력·매뉴얼에 복사하지 않는다.
- 01 관제→표·근거,03 사진작업실→사진선택·근거,04 4단계 제출·하단더보기,05 범위탐색→조건유지·행렬·전후비교로 서로 다른 설명을 작성한다.
- 최종 화면 캡처가 없는4개 시안은 초안/캡처·브라우저문서 검증 NOT_RUN으로 명시한다. 다른 시안02의 이미지·문서를 수정하거나 완성 캡처로 재사용하지 않는다.
- docs02의 선택 정본 예정경로 execute/question/frontend-selection/select-concept.md가 아직 없어 root에 위치협의 메시지를 보냈다. 존재하지 않는 선택 문서로 깨진 링크를 만들지 않는다.

## 초안 인계 · 2026-09-21

| 시안 | HTML | 실제 소스에 따른 안내 구분 |
|---|---|---|
| 01 | deliverables/manuals/concept-01/index.html | 왼쪽 관제 메뉴, 사진·평가 표, 상세 탭, 160px Reference 관리 행, 점주 하단 메뉴 |
| 03 | deliverables/manuals/concept-03/index.html | 사진 작업실, 사진 무대/관찰 연결, 사진 번호 선택, Reference 갤러리, 상단 업무 탐색 |
| 04 | deliverables/manuals/concept-04/index.html | 매장→사진→질문→확인 단계, 하단 5개 메뉴/더보기, 현장 조치 카드와 변경 확인 |
| 05 | deliverables/manuals/concept-05/index.html | 범위 탐색과 주소 유지, 비교 행렬, 목록/상세 작업 영역, 연결 이력과 전후 비교 |

- 네 문서에 역할별 시작 경로, 실제 메뉴·버튼, 입력 규격, 담당 등록, 기준/Reference 버전, 이슈 상태 저장과 별도 코멘트, 운영 계정/연결/기준 정보/실패 복구/감사/공지를 넣었다.
- 점주 정상·빈·대기·기술 실패·판단 불가·기준/Reference 누락·동시 변경·권한 변경의 의미와 다음 행동을 설명했다. 운영자의 영업 본문/알림 제외도 명시했다.
- 실행 스크립트 및 workspace 명령, 합성 로그인 ID만, 사용자 전용 비밀번호 파일 안내, 실제 AI와 Mock·생성 사진의 구별, 30초 목표와 실제 지연 미확정, 네트워크가 필요한 모델 실행의 한계를 기록했다.
- `contract_ai`의 비교자료 확정 경로 `deliverables/frontend-comparison.md` 수신/연결. root 선택 정본 `execute/question/frontend-selection/select-concept.md` 경로 ACK. 파일 생성 전이므로 현재 경로 텍스트만 표시해 깨진 링크를 피한다.
- 소스 대조: 각 `src/app`의 역할 메뉴/라우트, `src/store-owner`의 제출·상세·비교, `src/ofc-admin`의 기준/Reference/조치, `src/platform-admin`의 계정·연결·재처리, 공유 UI의 기본 저장 버튼 문구. 네 가지 이슈 상태 저장 버튼은 01 저장 / 03 조치 변경 저장 / 04·05 변경 저장으로 구분했다.

### 실행한 검사

`python3 execute/workHitory/manuals-others/validate_drafts.py` → 4개 PASS. UTF-8, ko 언어/viewport, 태그 짝, 중복 ID 없음, 12개 앵커/문서, 10개 로컬 링크/문서 존재, 외부 CSS/JS/이미지 의존 없음, 필수 상태/역할/제약 설명, 비밀 값 메모리 비교에서 포함 없음. 출력은 비밀 값이나 비밀 파생값을 남기지 않는다.

정적 결과와 각 HTML SHA-256: `execute/workHitory/manuals-others/static-validation.json`.

### 미완료와 재개 순서

1. root의 시안별 정확한 `vp-*.png`를 받는다. 다른 시안 이미지/깨진 fullPage 캡처를 재사용하지 않는다.
2. 실제 파일을 직접 확인하고 해당 설명·역할·시점에 맞는 로컬 이미지와 캡션/alt를 넣는다. 현재 모든 문서는 화면 이미지 0개이며 NOT_RUN을 상단과 검증 표에 표시했다.
3. root 선택 문서 링크를 연결하고 정적 검사를 최종 이미지 검사에 맞춰 확장한다. 현재 검증 스크립트는 의도적으로 이미지 없는 초안만 검사한다.
4. root 브라우저 문서 렌더·모바일·오프라인 검사와 contract_ai의 독립 내용/이미지 검수를 반영한다. 이 검증 전에는 매뉴얼을 완료로 올리지 않는다.
5. 생성기는 초안 기록이다. 수동 캡처 삽입 후 다시 실행하면 삽입을 지우므로 이미지 반영 시 생성기/HTML 처리 방식을 함께 갱신한다.

앱·공유 API·DB·브라우저·02 매뉴얼은 수정하지 않았다. 최종 선택은 사람에게 남아 있으며 선택 대기는 구현/검증의 완료와 별개다.

### 독립 사전 검토 반영 · MAN-D01

contract_ai가 01 계정 등록 펼침 명칭, 동적 버튼명의 조사, 사진 오류 재시도 문구를 지적했다. 실제 01 운영 화면의 `일반 계정 등록` 펼침 → 입력 → `계정 등록` 제출로 보완했다. 네 문서의 동적 버튼명 뒤 조사는 `버튼을/버튼으로`로 통일했다. 사진 오류에는 존재하지 않는 사진 재시도 버튼을 안내하지 않고 목록에서 기록 다시 열기 및 제공되는 처리 상태 버튼 사용으로 정정했다. 생성기와 4개 HTML에 반영 후 정적 검사 4 PASS, SHA-256 증거 갱신. 캡처/브라우저 검수 상태는 NOT_RUN 유지.

## MAN-IMG01 착수

root가 01의 실제 viewport 이미지 반영을 재배정했다. 정상 vp PNG를 직접 확인하고 점주 모바일 홈/제출/진행/실제 결과, 본사 관제/Reference 관리/기준 변경 중 대표 화면을 고른다. 실제 첫 분석 지연과 스냅샷 근거는 actual-ai.json 및 browser-latency-first.json으로 대조한다. 재제출을 포함한 전체 인수는 진행 중이므로 완료를 선언하지 않는다. 선택 정본 파일이 생성되어 01/03/04/05에 링크 연결을 허용받았다. 앱/브라우저/02 매뉴얼 소유 범위는 변경하지 않는다.


### MAN-IMG01 반영 완료 · REVIEW

- 01 대표8장: 모바일390 홈/미리보기·키보드초점/첫 실제 답변, desktop1440 본사관제/Reference160px관리행/전후비교/OFC해결, desktop1280 CATEGORY v2. 모두 원본을 직접 열람하고 보이는 기능만 alt·캡션에 설명했다.
- 작성 중 root가 F01-FILTER/F01-ANALYTICS 최소수정을 우선 배정해 매뉴얼을 잠시 대기했다. 두 소스 변경은 UI14/build PASS 후 동결 인계했으며 해당 frontend01 이력에 별도 기록했다.
- 캡처 파일 이름은 .png이지만 실제 바이트는 JPEG였다. 최초 PNG 헤더 가정으로 치수를 잘못 읽은 중간값을 발견하고 제출 전 Pillow 실제 디코더로 정정했다. 현재 HTML width/height는 실제375×812,1425×891,1265×791이며 원본 바이트는 변형하지 않았다. 매뉴얼 caption의 viewport는 root가 설정한390×844/1440×900/1280×800 촬영 조건이다. 이미지 편집/합성/리사이즈는 하지 않았다.
- 최초 임시 선택의 결과 상단/진행중 두 그림은 최종 대표 구성에서 전후비교/OFC해결로 교체했고 해당 로컬 복사본만 제거했다. 원본 증거는 보존했다. 깨진 것으로 보고된 vp-mobile360-resubmit-preview 및 오해를 부르는 filter-loss 이름 캡처는 사용하지 않았다.
- 실제첫 분석 모델90.824초/DB91.132초/Browser91.732초, 재제출 모델54.601초/DB55.622초/Browser 최초관찰69.336초 이하 상한을 정본 JSON과 대조했다. 두 건 모두30초목표미달. 두 사진20→100%는 합성사례/변경기준비교제한을 명시했다. 기능·디자인 전체PASS로 표현하지 않았다.
- 01/03/04/05 선택 정본 링크 연결. 03/04/05는 이 링크 외 본문/상태 수정 없음. 02 매뉴얼 수정 없음.
- 정적 검증: `server/.venv/bin/python execute/workHitory/manuals-others/validate_drafts.py` →4 PASS. 01 anchors20/local links31/images8, 다른 세 문서 anchors12/local links11/images0. 외부 리소스0, 원시 비밀번호 포함 없음. 각 이미지 디코딩·실제치수/alt·상대경로와 소스 동일바이트/hash 확인.
- 이미지 출처/치수/format/alt/caption/hash 정본: `concept01-image-manifest.json`. HTML검사/해시: `static-validation.json`.
- 재생성은 `python3 execute/workHitory/manuals-others/generate_drafts.py 01` 후 `server/.venv/bin/python execute/workHitory/manuals-others/add_concept01_images.py` 순서다. 이 외 세 문서 동결을 유지하려면 generator에01 인자를 생략하지 않는다.
- 남음: 운영자/추가경계의 필요한 최종 그림 여부는 root 인수 범위에서 확인, root 실제 문서 브라우저·모바일·오프라인 렌더 및 contract_ai 독립 내용/이미지 검수. 현재01 매뉴얼 상태는 검수 중이며03/04/05는 화면미반영초안이다.

### MEDIA-CLARIFY-2 수신 ACK

root가 영업 관리자의 현재 관리 범위 안 비활성/교체 Reference 원본·썸네일 열람을 목록·상세 이력과 일치시키는 인가 보완을 통보했다. 03 현재 설명의 “과거 평가에 쓰인 원본 유지” 및 현재 범위의 원본/썸네일 제한과 충돌 없음 확인. 03 최종 화면 반영 때 관리자가 과거 관리 사진도 확인할 수 있음을 명시한다. 점주 활성/snapshot 기준·운영자 영업 사진 불가·범위 밖 비공개는 유지한다. 이 수신 작업에서는 동결 HTML·API·인가 소스는 수정하지 않았다.


### MR-004 / MEDIA-CLARIFY-2 반영 완료 · REVIEW 동결

contract_ai의 독립 대비 지적에 따라 01/03/04/05 header a:focus-visible만 #f4d486으로 지정했다. 어두운 header #173c48 대비8.224:1이고 흰 본문의 기존 #176ac6 대비5.366:1은 유지했다. 02 매뉴얼은 수정하지 않았다. 공통 generator도 같은 규칙으로 맞췄으며 기존01의8개 화면·문서 상태·증거 링크는 유지했다.

네 매뉴얼의 Reference 변경 안내에 OFC·지역 관리자·본사가 현재 관리 범위 내 교체/비활성 Reference 사진을 확인할 수 있다는 문장과 점주의 허용 활성/제출 적용 예시, 운영자의 영업 사진 열람 불가를 명시했다. MEDIA-CLARIFY-2의 범위 제한과 일치한다. 기존 안내에는 충돌이 없었으며 사용자에게 과거 관리 사진 동작을 더 명확히 설명하는 보완이다.

정적 재검사4 PASS. 이미지/경로/앵커/alt·원본일치·비밀값 미포함 확인, HTML hash 갱신(static-validation.json). 대비 근거 focus-contrast.json. 실제 키보드 포커스/브라우저 문서 렌더는 root 후속이며 독립 검토는 contract_ai에게 인계한다.

### MAN-IMG03 착수

root의03 실제 첫 제출 진행·정상미리보기 인계와 기존 상태 화면 사용 안내를 받아 6장을 직접 열람했다. 원본은 fixed photo dashboard, first preview/processing, unknown-mock, technical-failure, empty-history이다. 업로드 결함 재현 그림과 기존 사진0장 관제 그림은 완료 예시로 사용하지 않는다. 아직 실제 AI 결과 및 시안전체/문서렌더 인수 완료를 의미하지 않는다. D03-V01의 새 사진 우선 관제 문구를 실제 메뉴/anchor와 일치시킨다.


### MAN-IMG03 정상6장 반영 · REVIEW 동결

정상 사진 관제1장, 모바일미리보기·처리·Mock판단불가·시드기술실패·빈이력5장을 원본 그대로 복사했다. 업로드 실패 재현 및 수정 전 관제 사진은 사용하지 않았다. 제목/정확한 업무 위치에 figure를 넣고 각 상태의 의미를 캡션에 설명했다. Mock판단불가는 신규 실제AI로, 시드기술실패는 이번 신규실행 실패로 표현하지 않았다. 현재 03 실제AI완료/재제출/추가관리·운영·문서렌더 인수는 대기다.

이미지는 직접 decoded된 원본 치수와 format을 기록하고 가공 없이 복사했다. source/hash/alt/caption 정본은 concept03-image-manifest.json. 사진 우선 관제의 현재 필터→최근사진→지표·매장현황 동선 문구도 generator와03HTML에 반영했다. generator03 재생성 후 add_concept03_images.py로 다시 넣을 수 있다.

검증 스크립트는01/03의 manifest개수·embedded이미지·alt·원본바이트/hash도 대조하도록 확장했다. 정적4 PASS:01 images8,03 images6(anchors18/local links23),04/05 images0. 캡처는 모두 정상 viewport며 최종 문서브라우저 렌더는 NOT_RUN 유지. contract_ai의 MR-004/MEDIA-CLARIFY-2 독립 소스 PASS 수신,03 상태사진5장 직접검수에서도 사용가능 확인을 받았다.


### MAN-IMG03 독립 검사 수신

contract_ai가03 정상6장의 원본/복사/manifest hash·HTML alt/캡션·로컬 링크를 대조해 PASS 판정했다(concept03-images-005.json). first-actual-result 및 Reference2개 캡처는 후속 사용가능하나 root가 child 완료 후 별도 이미지 반영을 지시했으므로 현재6장과 상태를 유지한다. D03-V02가 보이는 guideline-v2 캡처는 수정 후 재촬영본을 기다린다.

### MAN-IMG03 실제 AI·재제출 보완 착수

root가03 child succeeded와 새 캡처 반영을 재배정했다. actual-ai.json의 첫 모델96.072/DB97.227초, child모델64.730/DB66.783초를 읽고 first-latency.json의98.468초(관찰3초), child-latency.json의마지막pending66.443→최초완료관찰70.687초(구간4.244초)를 대조했다. 30초목표미달을 유지한다. 별하천점·음료의첫60%/child100%는 합성사례이고 qa03_labels v1→v2는 직접비교불가다. D03-V02가 남은 guideline-v2 캡처는 사용하지 않는다.


### MAN-IMG03 실제 결과·child 반영 완료 · REVIEW 동결

- 대표8장 구성: 모바일 첫 미리보기·첫 실제 답변·child 실제 답변, desktop 전후사진·사진관제·Reference v2/v1 갤러리, 모바일 Mock판단불가·시드기술실패. 신규4장 직접 원본열람 후 복사했고 이전 processing/empty 두 로컬복사본만 제거했다. root 원본은 보존했다. old-snapshot/comparison-criteria/child-preview/inactive-reference-fixed도 직접 읽어 본문 사실을 대조했으나 대표8장에 추가로 넣지는 않았다.
- 첫 분석 모델96.072초/DB97.227초/브라우저98.468초(관찰3초), child모델64.730초/DB66.783초/브라우저pending66.443→완료관찰70.687초(구간4.244초)를 각각 구분했다. 값은 actual-ai.json·first-latency.json·child-latency.json에서 읽어 렌더한다. 정확한 렌더완료 순간으로 오해하지 않도록 설명했다. 두건30초목표미달.
- 별하천점·음료/사진1·기준5·Reference2, 첫60%/child100%, 판단가능률100%를 설명하되 qa03_labels v1→v2 직접비교불가와 합성1사례라는 제한을 명시했다. 정렬/빈공간2항목 개선은 비교가능한 항목으로 설명했다. 실제 첫 가격숫자판독 한계, 새 라벨/Reference 적용 응답, 이전 제출 자료 보존을 구분했다.
- 시연 흐름의 점주/OFC/지역을 south로, 매장을 별하천점으로 맞췄고 새 기준·Reference 변경 후 연결된 결과에서 재제출하는 순서를 적었다. 일반 절차와 실제관찰 값을 혼동하지 않도록 성능근거4링크를 함께 제공했다.
- D03-V02 guideline-v2 결함 캡처는 사용하지 않았다. D03-V03 비교 날짜/버전 누락 후보는 독립 검수에서 새로 전달되어 root의 소유 이관을 기다리며 실제 전체기능PASS를 선언하지 않는다.
- 4개 정적 검사 PASS. 03 HTML44860bytes, images8/anchors20/local links31.01/04/05는 이번 단계 미수정. manifest·alt/caption·원본바이트/hash·actual치수·비밀미포함/외부리소스0 확인. 최종문서브라우저 NOT_RUN/추가관리·운영증거대기 유지.
- 현재03 소스와 매뉴얼 REVIEW 동결. root 후속 실제 화면·contract_ai 독립 문서 재검수에 인계한다.


### MAN-IMG03 최신 비교·운영 처리 반영 · REVIEW 동결

root의추가요청으로옛비교그림을vp-desktop1440-comparison-dates-fixed로교체하고versions-fixed와operator-retry-success를추가해정상10장으로갱신했다. 세원본을직접열어KST양쪽날짜,qa03_labels v1→v2비교불가/정렬·빈공간개선,시도1expired적용없음→시도2분석완료·결과저장완료를확인했다. 비교캡처는HQ역할이므로caption을본사에서확인한비교로명시했다. 운영자성공캡처는viewport-correction-operator.json에서재지정된1440×900임을대조했고파일명만믿지않았다.

원본은변형없이복사,옛comparison 매뉴얼로컬복사본만제거,root증거는보존했다. 03정상10장/anchors22/local links35,01정상8장/04·05무이미지초안. 4개정적검사PASS,manifest·alt/caption·source바이트/hash·decoded치수·비밀미포함확인. 정확한지연/관찰구간·Mock/실제AI·30초목표미달·전체인수/문서렌더NOT_RUN상태유지.

root가아직교체하지말라고명시한03점주resolved그림은사용하지않았다(새파일존재와별개). 현재매뉴얼에는해당이슈그림없음. 질문2000자경계·오류UX는source review만수행하고concept03-question-boundary-prep.md로준비정보를전달했다. 실제브라우저는조작하지않았다. 모든본범위문서REVIEW동결,root/contract_ai후속문서검수대기.


### MAN-IMG03 최신10장 독립 검수 및추가증거수신

contract_ai가최신10장원본/복사/hash/alt/caption·링크/anchor를독립검사해PASS(manual-review/review-001.md,concept03-images-latest.json)로인계했다. root가03resolved-fixed 그림의실제조작·독립시각PASS도확인해후속사용을허용했다. 현재대표10장구성을유지하여새이미지는추가하지않았으며그림선정과별개로해결상태안내실제PASS를기록한다. 최종매뉴얼Browser/오프라인검수는대기다.


## MAN-IMG04 · 실제04 화면10장 반영

04 정상10장과 실제 스낵 시연/지연을 반영하여 REVIEW 동결. HTML SHA `436dbbe7c2da87e259cc843157bacc32af84c50bb9c80516cc6d008cc9d716e6`. 정적4 PASS, 01/03/05 본문 해시 유지. 자세한 선별·원본·검증은 `concept04-images.md`, `concept04-image-manifest.json`, `static-validation.json`을 따른다. root 실제 문서 렌더와 contract_ai 독립 검수는 대기다.


## MAN-IMG05 · 첫 실제 화면7장

초기 정상9장 직접 검토 후7장 반영하여 REVIEW 동결. 05 HTML SHA `a795364aface5d39af0ba266365ac9630be52d348c92207e9497b65ddd78b426`. 정적4 PASS,01/03/04 본문 hash 보존. 최초 AI 완료 인계와 관찰값만 반영하고 결과/재제출/운영의 상세 정본은 대기. `concept05-images.md`, `concept05-image-manifest.json` 참고.


## 첫 실제 AI 정본 도착 후 보완

최초 인계 직후 root의 actual-ai.json이 생성되어 직접 읽고 모델60.273초/DB61.422초, 사진1·기준5·Reference2, 실제 succeeded를 본문에 보완했다. 브라우저 관찰창과 분리하며30초 미달은 유지한다. 새 first-result는 contract_ai가 흰 화면을 확인해 정상 예시에서 제외 요청한 파일이므로 사용하지 않았다. 기존 정상7장 선택은 그대로다.

정적4 PASS 재확인. 최종05 HTML43524bytes, SHA `98cc686a15fbc05fea2dd7bcc3119e90d2b67b8c9fb943a206cc677ef5b1cd20`, 이미지7/앵커19/로컬링크28. 앞선 a795364a…는 정본 도착 전 최초 인계 상태로 남기고 이 해시를 최신 동결본으로 사용한다. 최종 결과 캡처·child·운영 및 문서 Browser 렌더는 후속 대기다.


## MAN-IMG05 후속 실제 결과·비교·조치 · REVIEW 동결

root가 본인05 체크/이력·생성기·정적검사 범위 갱신을 명시 허용했다. 제품/타매뉴얼/타담당 문서/원본 PNG는 수정하지 않았다.

새 정상7장(first-result-fixed, child-result, desktop comparison-dates, comparison-versions-fixed, mobile comparison-right-fixed, ofc-resolved, owner-resolved)을 모두 직접 열람했다. 기존 홈·사진 선택·본사 매장 비교3장과 합해 대표10장으로 갱신했다. 형식 오류·처리 지연·기준편집·Reference등록 준비 그림은 본문 설명을 유지하고 대표 이미지에서는 제외했다. 해당 미사용 매뉴얼 복사본4개만 정리했고 root의 원본 증거는 보존했다. 흰 first-result는 계속 제외한다.

실제 결과는60→100%이며 판단 가능률은 두 건 모두100%다. facing은v2→v2, shelf_gap은v1→v1에서 개선됐고 qa05_labels는v1→v2라 양쪽 모두준수라도 직접 비교하지 않는다고 설명했다. 사진 자체의 정답/일반정확도로 확대하지 않는다. 날짜 비교 사진은 상단 구간으로 한정했고, 모바일 비교는 표 자체의 오른쪽 열/초점/스크롤을 설명하며 왼쪽 기준명은 반대 방향으로 확인하도록 안내했다.

OFC.south 해결 화면에는 관리 입력이 있고 owner.south의 연결 이슈는 읽기 전용이라는 실제 역할 차이를 캡션에 반영했다. 점주의 하단 이력 전체를 한 캡처에서 다 읽었다고 하지 않았다. 가격은 첫 AI/후속 AI/사람 해결 내용 모두 사진 밖 정보로 추정하지 않고 별도 현장 확인으로 구분했다.

actual-ai.json 두 행과 latency-child.json을 직접 대조했다. 첫 모델60.273/DB61.422초, child 모델63.876/DB66.097초를 표시했다. child의 마지막 확정 대기56.504초 이후 완료는 확인됐지만 타이머 변수 기록 오류가 있어94.159초는 보수적 상한이며 관찰구간37.655초라고 명시했다. waitFor 예외를 확정 pending으로 인용하지 않았고94.159초를 정확한paint/완료시점으로 소개하지 않았다. 두 건의30초 미달은 모델/DB의 정확한 수치만으로도 확인된다.

정적4 PASS. 05 HTML48713bytes/SHA `3cc37c628a3708ead8942a7d12670e66dd460a9a63e135b195511410c8100888`. 이미지10, 앵커22, 로컬링크35, 외부리소스0, 비밀값 없음. 01/03/04 본문 해시는 유지됐으며 manifest의 byte/hash/alt/실제 decoded 치수·포맷과 링크를 다시 확인했다. `add_concept05_images.py`는 base05 생성 후 실행하는 최신10장 생성기로 갱신했다.

운영 화면 추가, 전체 제품/디자인 판정, 매뉴얼 Browser/200%/오프라인 렌더는 별도 대기다. 이번 정적 PASS로 해당 항목을 완료 처리하지 않는다. root에 재촬영 불필요한 현재 정상10장 매뉴얼 및 contract_ai 내용·이미지 재검수로 인계한다.


## MAN-IMG05 운영2장 추가 · 12장 REVIEW 동결

root 배정 범위대로 제품 변경 없이 최신 정상 운영2장만 추가했다. `vp-desktop1440-operator-home.png`와 `vp-desktop1440-retry-success-applied.png`를 직접 열람하고 root browser.md E05와 대조했다. 홈의 계정↔매장 연결 누락 및 실제 처리/Mock 장애 별도 집계, 재처리의 첫 AI_UNAVAILABLE 실패 보존/두 번째 완료·결과 반영 예/성공 재처리 금지를 그림으로 설명했다.

이 작업은 Mock 장애 fixture이며 최초 접수가 과거다. 전체 접수기간을 신규 사진 제출 성능으로 쓰지 않는다고 캡션·본문에 명시했고 fixture 모델/run 수치를 성능표에 추가하지 않았다. 앞선 실제 신규2건의 모델/DB/Browser 상한 설명은 그대로 유지한다. 원본사진·root기록·제품소스·타매뉴얼은 수정하지 않았다.

200% 확대/문서 Browser·오프라인 렌더는 NOT_RUN으로 유지했다. 정상12장 추가가 전체 기능/디자인/문서 렌더 최종 PASS라는 뜻은 아니다. 사용한 이미지 원본 복사/해시/alt/캡션은 `concept05-image-manifest.json`에 갱신했다.

정적4 PASS. 최종05 HTML51363bytes/SHA `d2f40a302b03bca7cc87cd538c0769a5bf3b762b33d148a3ddd60750f1758126`, 이미지12/앵커24/로컬링크39/외부리소스0/비밀값 없음. 01/03/04 본문hash는 이전과 같다. 운영 그림 앵커는 #screen-operator_home 및 #screen-operator_retry다. root 실제 문서 렌더 및 contract_ai 독립 내용·이미지 재검수로 인계한다.
