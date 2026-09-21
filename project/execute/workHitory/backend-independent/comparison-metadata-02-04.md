# 시안02/04 전후 비교 날짜·기준 버전 보완

- docs04 S-O05 및 §84는 부모/현재 사진·날짜·적용 기준 version·항목별 변화가 필수다. 독립 디자인 검수에서02 날짜/버전,04 버전 누락을 발견하여 root가 제한 소유권을 배정했다.
- 정확 경로: web-concepts-02/src/store-owner/Owner.tsx Comparison(id,prefix), web-concepts-04/src/store-owner/Owner.tsx Comparison(prefix). 신규 테스트 외 다른 제품 소스/CSS/API/DB는 변경하지 않는다.
- 비교 DTO에는 날짜/버전이 없으므로 기존 GET /submissions/{id}와 부모 detail을 조회하여 당시 snapshot의 rule_key/version을 사용한다.04의 기존 current detail을 재사용한다. 현재 가이드라인 목록이나 최신 버전으로 과거를 추정하지 않는다.
- 계획: 의미 회귀 RED→최소 표시/조회 보완→기준 추가/제거·부모 없음·조회 실패 경계와 기존 수치/경고/사진 보존→전체 tests/build→독립 검토자 contract_ai/root에 freeze 전달.

## 의미 RED
- 신규 각 `tests/comparison-metadata.test.tsx`는 순서가 다른 부모/현재 snapshot에서 rule_key로 v1/v2·제거v3/추가v4를 대응하고, 전후 날짜·사진 URL·수치·기준변경 경고를 확인한다. 부모 상세 실패/재시도 및 부모 없는 경우의 불필요한 조회 방지도 검사한다.
- 수정 전 `npm test --workspace @storeloop/concept-02 -- tests/comparison-metadata.test.tsx` → 2 FAIL/1 PASS(2.56초). 같은04 명령 → 2 FAIL/1 PASS(2.57초). 실패는 버전 표시 누락과 부모 상세 오류 안내 부재이며, 부모 없음 안내는 기존에도 통과했다.

## GREEN 구현과 검증
- 기존 GET comparison에 더해 현재/부모 SubmissionDetail을 조회한다.04는 기존 current detail 요청을 재사용하고 부모만 추가했다. 현재 guideline API나 최신 기준은 요청하지 않는다.
- 양쪽 카드에 당시 제출 날짜를 KST·연도 포함으로 표시하고, native details에 당시 적용 기준 개수·버전·본문을 보여 준다. 평가가 없더라도 snapshot의 적용 버전은 확인할 수 있다.
- 항목별 행은 rule_key로 양쪽 snapshot을 연결하여 ‘이전 기준 v1 → 현재 기준 v2’로 표시한다. 추가/제거로 해당 snapshot에 없는 기준만 ‘미적용’이다. 실패/로딩을 미적용으로 추정하지 않으며 기존 Resource/DataState 오류·재시도 UI를 사용한다.
- 기존 사진·source metadata, 준수/판단가능 수치, 판정 및 criterion_changed 경고·비교 불가 분기를 유지했다. 기존 comparison-grid/comparison의 모바일1열과 comparison-row의 flex-wrap을 사용하며 CSS는 변경하지 않았다.
- 신규 각3개 GREEN:02 517ms,04 528ms. 전체 검증 `npm test --workspace @storeloop/concept-0N && npm run build --workspace @storeloop/concept-0N`:02 **19 PASS**, tsc/Vite build PASS(38 modules,505ms);04 **14 PASS**, tsc/Vite build PASS(48 modules,600ms).
- 리팩터 검토: 각 Comparison 안에 작은 versionFor 조회를 두어 행마다 동일한 미적용 규칙을 사용한다. 공통 hook/API/DB/CSS로 변경 범위를 넓히지 않았다.
- root와 contract_ai에 정확 소유 파일·테스트·동결을 전달했다. 본 결과는 UI 구현 자기검증이고 contract_ai의 독립 소스 검토 및 root의 실제 브라우저 재촬영은 별도 결과로 추적한다.
- contract_ai 독립 소스 검토 **PASS** 회신 수신: 양쪽 불변 snapshot 버전·연도/KST 날짜·미적용·실패/재시도·사진/rate 유지와 신규 회귀의 요청 범위·버전0 추정 방지·무부모 처리를 확인했다. 실제 시각 판정은 root의 수정 후 캡처를 기다리므로 아직 PASS로 표시하지 않는다.
