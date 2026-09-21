# DR-FINAL-001 · 기존 디자인 증거 대조 및 독립 시각 후속 검수

- 2026-09-21 / contract_ai / **REVIEW_COMPLETE(이 후속 작업)**. 전체 제품·전체 디자인 완료가 아니다.
- 범위·이유: 사용자의 매뉴얼 우선/검수 최소화 지시 아래 이미 있는 입력·복구·없음·분산0 PNG14장과 root가 추가한01 운영 상태2장만 직접 열람했다. 이미 본 화면은 재열람하지 않았고 새 실행/테스트/Browser/DB/AI/서비스/구현/매뉴얼 변경은0이다.
- 계획·완료 체크: [x] 정본5acceptance·docs02/09 대조 [x] 미검토16이미지 직접 시각검수 [x] 기능/시각·화면밖 구분 [x] 정본5보고서 최신화 [x] 필수 잔여/권장 분리. 본 작업의 수정 파일은 이 문서와 정본5개뿐이다.
- 관찰 결과: 보이는 범위에서 새 명백한 겹침·오표시·읽기 방해 결함은 발견하지 않았다. 모든 사진/제어/문구가 한 viewport에 들어온다는 판정은 아니다. 화면 밖은 결함이나 PASS로 바꾸지 않았다.

## 근거와 버전

[docs02 §8.5](../../../docs/02-development-orchestration.md)와 [docs09 §6](../../../docs/09-validation.md), 각 [01](../../design/concept-01/acceptance.md)·[02](../../design/concept-02/acceptance.md)·[03](../../design/concept-03/acceptance.md)·[04](../../design/concept-04/acceptance.md)·[05](../../design/concept-05/acceptance.md)의 필수 기준은 그대로 유지했다.01은 DS01-002 v1.1-review, 나머지는 DS02/03/04/05-001 기준이다. 구현자/기능 인수자와 독립된 검수이며 소스/DOM만으로 시각 PASS를 만들지 않았다.

입력/충돌 PNG는 root의 테스트DB 합성자료 실제 조작 시점의 dev 화면이다. [input-boundary/browser.md](../input-boundary/browser.md)·[browser-evidence.json](../input-boundary/browser-evidence.json)·독립 [01](../input-boundary/independent-recovery01-review.md)/[02](../input-boundary/independent-recovery02-review.md)/[04](../input-boundary/independent-recovery04-review.md) 소스 복구 기록과 연결한다. 최신 최종 산출물은 [build-files.json](build-files.json)의01 index-hnJ_xClo,02 index-C6hz82zD,03 index-DwKifTuH,04 index-BM4lTLjU,05 index-kGtlCAeC다. 과거 PNG를 이 마지막 build에서 촬영했다고 소급하지 않는다. 파일별 SHA는 아래에 고정했다.

health/model2장은 일반 시연DB storeloop·operator.demo·최종소스 dev이며 요청1440×900/innerWidth1440/document1425, decoded1425×891이다. [안전 메타데이터](concept01-health-evidence.json)와 [이미지 식별](concept01-health-images.json)을 연결한다. 나머지 파일명 viewport는 root 기록을 따르며 실제 decoded 크기는 아래처럼 별도로 기록한다. 원본 PNG 확장자와 실제JPEG 형식의 차이를 보정/편집하지 않았다.

## 새로 직접 본16장

| 시안 | 원본 | decoded/형식 | SHA-256 | 독립 관찰 범위 |
|---|---|---|---|---|
| 01 | [vp-mobile390-photo-order-boundary.png](../../designReview/concept-01/evidence/vp-mobile390-photo-order-boundary.png) | 375×812 / JPEG | bbca11fbc1bdd1afe7ad24a2bfdca4d32f76550353d48f5e0eedf418a2373ed7 | 선택폼·제약 안내와 두 사진 상단만 보임. 번호/순서/제거는 화면 밖. |
| 02 | [vp-mobile390-photo-order-boundary.png](../../designReview/concept-02/evidence/vp-mobile390-photo-order-boundary.png) | 375×812 / JPEG | 2b81b836ba54c00ff5721bc18d27ed2ac3264653fa7b668ebc6a54443758697e | 매장/분류·사진선택·순서 안내가 읽힘. 미리보기 번호/조작은 화면 밖. |
| 03 | [vp-mobile390-photo-order-boundary.png](../../designReview/concept-03/evidence/vp-mobile390-photo-order-boundary.png) | 375×812 / JPEG | 53e8c6ea23b0585059145f07b0314ad6908c4c09c50b96512c179da4b17faa03 | after사진1·uncertain사진2의 원본/파일명/용량 확인. 나머지 사진/제어행은 화면 밖. |
| 04 | [vp-mobile390-photo-order-boundary.png](../../designReview/concept-04/evidence/vp-mobile390-photo-order-boundary.png) | 375×812 / JPEG | 05415c6b00df553834c43da9c5c8fdc6abaff8050e714fd9012a7c25bc81f8bc | 사진2단계·제약 안내·두 사진 상단 확인. 번호/제어행은 화면 밖. |
| 05 | [vp-mobile390-photo-order-boundary.png](../../designReview/concept-05/evidence/vp-mobile390-photo-order-boundary.png) | 375×812 / JPEG | ea58b5161cba069bcf5c918efbc33d98fcbb7c392ed3ba9d49a7283a4cdf4728 | after사진1·파일명/용량·앞으로 비활성/삭제 확인. 두 번째 사진은 일부만 보임. |
| 01 | [vp-desktop1280-conflict-draft-preserved.png](../../designReview/concept-01/evidence/vp-desktop1280-conflict-draft-preserved.png) | 1265×791 / JPEG | ccca6f3229164655401d93423bf93b7ca0d981ca39980789c2c2338fdc78a411 | 서버v3 본문과 별도 편집초안/409 안내 확인. 사유/명시저장 버튼은 화면 밖. |
| 01 | [vp-desktop1280-reference-conflict-preserved.png](../../designReview/concept-01/evidence/vp-desktop1280-reference-conflict-preserved.png) | 1265×791 / JPEG | 32c7a06e1b6d6c28d9a62bd4ac7d82cc29104c3a198dd0fc11696ed5ad86b69e | 현재편집v4·보존caption·선택파일명 확인. 사유 하단/저장은 잘림. |
| 02 | [vp-desktop1440-csrf-draft-preserved.png](../../designReview/concept-02/evidence/vp-desktop1440-csrf-draft-preserved.png) | 1425×891 / JPEG | 1f7c5d8202c939a6d5e438f93a14d2be344fc48fb84141104a6d48d750f3a23c | caption/reason 입력과 preview 상단 확인. CSRF 오류 자체/파일명/저장은 화면 밖. |
| 02 | [vp-desktop1440-reference-conflict-saved.png](../../designReview/concept-02/evidence/vp-desktop1440-reference-conflict-saved.png) | 1425×891 / JPEG | 2f0b8dfa0139823e2f0778b31a439a7eb2cc728c10f6a4082cfaecde95527f63 | 새v3 활성 Reference의 원본/생성배지·보존caption 확인. 앞선 오류/복구 단계는 root 기록. |
| 04 | [vp-desktop1440-reference-conflict-preserved.png](../../designReview/concept-04/evidence/vp-desktop1440-reference-conflict-preserved.png) | 1425×891 / JPEG | e075e6a97439d34e112a29887cfb174772758018db89fcb6f5d0298ebd218087 | 보존caption·선택파일명/미리보기 확인. 기존v5 카드와 최신편집대상을 혼동하지 않음. |
| 01 | [vp-mobile390-no-criteria-reference-final.png](../../designReview/concept-01/evidence/vp-mobile390-no-criteria-reference-final.png) | 375×812 / JPEG | fc2ee89d2b555c5b83304ec7c0b38e1525979720fcc0facf1802948758ede733 | Mock·기준/Reference없음·OFC안내·준수/판단률 —/— 직접 확인. |
| 02 | [vp-mobile390-no-criteria-reference-final.png](../../designReview/concept-02/evidence/vp-mobile390-no-criteria-reference-final.png) | 375×812 / JPEG | d8c92fe925fda9b3342ddd57d4e0d224babec21f0bb62d77bf56cd8c03969e8a | Mock 완료/사진 상단만 보임. 기준0/Reference없음 본문·지표는 화면 밖: 해당 구간 시각미확인. |
| 05 | [vp-mobile390-no-criteria-reference-final.png](../../designReview/concept-05/evidence/vp-mobile390-no-criteria-reference-final.png) | 375×812 / JPEG | 632908b39a939d245d67ac1128dff44cc037fc3c6c76d0e4d2b04d21d83b6e04 | 적용기준0·Reference없음·OFC안내·Mock —/— 직접 확인. |
| 03 | [vp-desktop1280-zero-variance-final.png](../../designReview/concept-03/evidence/vp-desktop1280-zero-variance-final.png) | 1265×791 / JPEG | 843092450a851552db05ea2e7173e35e7a3e7673b6aaa98e0efe6a233fd98878 | Mock/비인과·n3·Pearson —·분산0 계산불가 및 같은 높이 표본 직접 확인. |
| 01 | [vp-desktop1440-concept01-health.png](vp-desktop1440-concept01-health.png) | 1425×891 / JPEG | a68bf73c39abc4704aa524030f6be05a838f2cf4129363ee8b8ff0e16d14dfde | 4서비스up·heartbeat·실제 작업카운트0 확인. 운영 본문 미노출. |
| 01 | [vp-desktop1440-concept01-model.png](vp-desktop1440-concept01-model.png) | 1425×891 / JPEG | a620563bdd540f547812d48795b6aeb32c6dbd1c408a92404149fc0373faf74a | 모델 판단불가/마지막성공실패 —·조회비실행 안내 확인. Mock25/7은 화면 밖이며 JSON 기능 근거만 있음. |

## 해소한 범위

| 시안 | 최신 판정 반영 | 남은 범위의 해석 |
|---|---|---|
|01|D01-02 동일필터 동선,03 정보구조 차별성,11 health/model+기존 재처리,18 출처/운영안전,19 실제매뉴얼 근거 PASS. 기준/Reference409의 입력보존과 root v4/v5 명시저장 연결.|새 photo-order는 폼 상단만 보임. 조작5장/2000자 기능은 root 기록,44px·긴기준 전체는 별도. 기준없음 Mock —/—는 직접 확인.|
|02|DS02-02 점주 제출,05 사진입력,08 출처 구분 PASS. CSRF→409→최신v2→명시v3 기능과 보존폼/새v3 카드 시각 확인.|Reference번호 결함의 수정결과 구간은 여전히 화면 밖. no-criteria 새PNG도 Mock완료 상단뿐이므로 본문 시각PASS로 확대하지 않음.|
|03|DS03-07 입력 제약/미리보기,12 분산0/n3/null·Mock·비인과,13 안전 운영/독립HTTP,18 증거 종류 구분 PASS.|기존결측/n0와 새분산0을 함께 사용. root 기간리포트도 이미 완료하므로 같은 통계를 재실행할 이유 없음.|
|04|DS04-03 preview/필터복귀,04 네단계 입력,18 증거 구분 PASS. 기존10 관리/이력 PASS에409초안/파일보존을 추가.|v6 조회·명시v7저장은 root 기능 기록. 새PNG는caption/선택파일/미리보기까지만 보이며 사유/저장버튼은 화면 밖.|
|05|D05-06 기존 모든 대표 상태에 통신복구 및 기준0/Reference없음·Mock —/—를 결합해 PASS.|복사URL 직접재열기/상세복귀,05 자체CSRF/409는 추가 근거가 없어 완료로 올리지 않음.|

위 PASS는 새16장만으로 판단한 전수 완료가 아니라, 각 정본에 이미 직접 검수한 정상/오류/권한/운영/매뉴얼 증거와 새 관찰을 결합한 해당 기준의 판정이다. 사진순서1~5/형식/10MiB초과/6장/0장·질문2000자,01/02/04 실제복구는 새 모델 분석을 요구하지 않으며 반복하지 않는다.

## 아직 필요한 최소 근거 — 제품 결함과 구분

아래는 정본의 필수 항목 중 검수 근거가 아직 부족한 범위다. 모르는 것을 새 결함으로 판정하지 않았으며 기존 자료가 있으면 먼저 연결하고, 같은 기능·화면 전체 재실행은 요구하지 않는다. 실제200%는 사용자 후행 NOT_RUN을 그대로 유지한다.

| 범위 | 필수 근거가 남은 부분 / 정본 ID |
|---|---|
|01|지역 포함5역할 최종 메뉴 범위(01); 정상 결과 근거/Reference·비교표 오른쪽·관리옵션/과거이력·분석의 미검토 구간(06~08,10); 운영 변경 충돌/감사after의 남은 구간(12); 모든해당화면4상태·접근성·긴기준·지정320/768/1024 및200%(04,13~17). health/model·출처/매뉴얼은 더 이상 대기 아님.|
|02|결과Reference1/2/3 실제카드(07/D02-004); 운영첫화면/5역할·원본근거/관리이력·운영폼/guard·분석/알림의 아직 대체되지 않은 구간(03/04/10~15); 목록상태·URL작업맥락·접근성/200%(16~19). 이미 본 정상 board/unknown/비교/attempt를 반복하지 않음.|
|03|44px·키보드/명칭/대비(02/17), 미제출 표현(10), 관리충돌(11), 남은 감사/기준정보(14), 세션·URL작업맥락/목록4상태의 미확인 범위(15/16). 분산0/기본리포트·운영HTTP·preview는 재실행 대상 아님.|
|04|화면이탈 polling 종료조건(05); 미제출/unknown카드·분산0/기간집계·지역/매장폼의 아직 없는 독립 시각 근거(08/12/13); 모든목록4상태·키보드/표명명·접근성(15~17). 입력/Reference복구/preview 대기는 해소.|
|05|복사URL 직접 재열기/상세복귀(02), 실제05폼409/CSRF 초안·파일보존/명시재시도·중복키(08), 아직 안 본 지역/매장 등 기준정보 폼(09),44px·키보드/대비/200%(05). 다른 시안 성공을 전용하지 않음.|

- **명시적 권장:** D01-20 대표10화면 시각 일관성 추가표는 권장이다. 사용자 최소 검수 지시에 따라 현재 자료의 대표 화면 비교로 인계하고 별도 전수 검수는 보류한다. 필수 미완료와 같은 수준의 차단 사유로 추가하지 않는다.
- **별도 추가시험 방법:** OS 네트워크를 막는 매뉴얼 오프라인 시험/인쇄는 docs02 §10에서 지정한 필수 방법이 아니다. 상대자산·외부CDN 없음·실제 로컬 렌더/링크 검수 완료와 구분해 미실행 추가시험으로 남긴다. 실제200%는 이와 달리 필수 접근성 후행이다.
- **입력 경계의 검증 층:** 정확10MiB/합계50MiB의 바이트 경계는 docs09 U-MEDIA01 단위층의 필수 검증이다. 이번 사진순서 PNG가 그 단위 결과를 대신하지 않으며, 동일 경계를 모든 시안에서 다시 촬영해야 한다는 별도 디자인 요구를 만들지도 않는다. 긴기준의 실제 표시 근거는 E06/해당 acceptance에 남긴다.

## 기존 인계 문장의 정정

[root 최종 실행](runtime.md)은5build/setup/start/중복start/stop→restart 및 preview3경로군×5 완료다. 하나의 새 탭에서15조합을 차례로 확인한 기록이며 마지막 콘솔조회 warn/error0다. 현재 최종 build/preview 대기나 stop→restart 진행중 문장은 옛 기록이다. 신규AI0이며 모든화면 디자인 전수PASS를 뜻하지 않는다.

pending-visual-evidence.md §3의05 ‘복사 URL 직접 재현/상세 복귀 완료’는 근거가 없는 확대 문장이다. integration-concept-05/browser.md와 정본 D05-02에서 이를 입증하지 못했으므로 **해당 부분은 NOT_RUN/기준 전체BLOCKED**가 맞다. root에게 정정 요청했고 본인의 이번 수정 범위 밖인 pending/비교자료는 편집하지 않았다. 최종preview 경로reload는 필터주소/상세뒤로 검증이 아니다.

정본5보고서와 이 기록은 현 시점에 동결한다. 후행200% 및 위 필수 근거가 남아 있어 전체 디자인완료/전체목표완료는 선언하지 않는다. 사용자 요청대로 새 검수범위나 PNG 촬영 요청을 추가하지 않는다.
