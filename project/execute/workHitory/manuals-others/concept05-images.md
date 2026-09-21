# MAN-IMG05 첫 실제 화면 반영

상태: REVIEW · 최초7장 문서 동결 · 담당 product_design

## 범위와 선별
05 매뉴얼 본문/assets 및 본인 작성·검증 기록만 수정했다. 01/03/04 본문 해시는 이전과 동일하다. 제품/공유 코드·root PNG·브라우저·DB·서비스·다른 담당 문서는 수정하지 않았다.

인계된 첫9장을 모두 직접 열람했다. 이력 홈390, 사진 미리보기390, 사진 형식 오류390, 지연390, 본사 매장 비교1440, 기준 편집1440, Reference 등록 준비1440의7장을 선택했다. 질문2000자 화면과26초 처리 화면은 중복을 줄이기 위해 현재 본문에 넣지 않았다. 후속 결과·재제출·운영은 별도 인계를 기다린다.

이력 홈의 보이는 과거 별하천점 기록을 이번 노을공원점 신규 결과로 설명하지 않았다. 사진 형식 오류는 기존 정상 사진이 유지된다는 관찰만 썼고 모든 파일 경계가 검증됐다고 확대하지 않았다. 기준 four-levels라는 파일명과 달리 실제 보이는 QA05 CATEGORY v1만 설명했다. Reference 오른쪽은 등록 전 미리보기이고 왼쪽은 기존 다른 자료임을 구분했다. 저장 완료·4단계 전체 본문 확인으로 과장하지 않았다.

## 실제 실행 표현
root는 첫 실제 submission3fdb0cf3-61da-4008-84c1-79e2a58cde05 완료를 인계했다. 작업 시작 시 actual-ai.json 및 최종 결과 PNG는 아직 없어 모델/DB·최종 점수·답변을 추정하지 않았다. 기존 latency-first.json의51.315초 대기→63.181초 최초 완료 관찰/11.866초 관찰창과30초 미달만 구분해 설명했다. 정밀 paint 시간이나 전체 인수 PASS가 아니며 결과/재제출/운영 정본 후속 대기 상태다. 기본 시연 경로는 owner.south/ofc.south의 노을공원점·음료로 맞췄다.

## 정적 검증
`add_concept05_images.py`는 `generate_drafts.py 05`의 초안에서만 실행한다. 그 밖의 시안은 재생성하지 않는다.

`server/.venv/bin/python execute/workHitory/manuals-others/validate_drafts.py` 결과4개 PASS. 05는 이미지7, 앵커19, 로컬 링크27, 외부 리소스0, 비밀 값 없음이다. 원본/복사본 byte·SHA, 실제 decoded 크기/형식, HTML alt/width/height, 로컬 파일 및 앵커 존재를 확인했다. 사진은 크롭/리사이즈하지 않았다.

HTML 43290bytes, SHA-256 `a795364aface5d39af0ba266365ac9630be52d348c92207e9497b65ddd78b426`. `concept05-image-manifest.json`에 이미지별 근거·캡션·alt·해시, `static-validation.json`에 전체 검사 결과가 있다.

## 인계
root의 후속 결과/재제출/운영 증거를 기다린다. contract_ai의 내용/이미지 독립 검수, root의 실제 문서 렌더·200%·오프라인 확인은 별도 대기다. 기존01/03/04 렌더 검수 URL path/앵커는 root에게 전달했으며 `render-targets-010304.md`에 보존한다.


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
