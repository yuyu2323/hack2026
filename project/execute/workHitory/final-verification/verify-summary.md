# 전체 검증 명령 결과
- 명령: scripts/verify.sh --postgres
- 종료코드: 0
- 원본 로그: 공유하지 않는 .local/final-verify.log
- 서버93 PASS/실제AI 표시1개별도, AI 단위39 PASS, 보안9 PASS, 런타임1 PASS, 공통클라이언트2 PASS.
- 프론트01 정책6+UI9,02 16,03 17,04 11,05 15 PASS. 5개 타입검사·build PASS.
- 알려진 테스트 경고: 03 회복 테스트2개에서 빈 img src 경고; 실제 브라우저 검수 때 확인 예정. httpx/Starlette 비파괴 폐기예정 경고2.
- 실제AI·브라우저·디자인·초기설치/시작/종료 재현을 이 통과로 대체하지 않는다.

```text
StoreLoop 비밀·금지 파일 검사 통과
Ran 9 tests in 5.853s
Ran 1 test in 0.001s
93 passed, 1 deselected, 2 warnings in 41.20s
39 passed, 2 warnings in 8.67s
ℹ tests 2
ℹ pass 2
ℹ fail 0
ℹ tests 6
ℹ pass 6
ℹ fail 0
 Test Files  3 passed (3)
      Tests  16 passed (16)
   Duration  674ms (transform 231ms, setup 0ms, import 339ms, tests 346ms, environment 875ms)
An empty string ("") was passed to the src attribute. This may cause the browser to download the whole page again over the network. To fix this, either do not render the element at all or pass null to src instead of an empty string.
An empty string ("") was passed to the src attribute. This may cause the browser to download the whole page again over the network. To fix this, either do not render the element at all or pass null to src instead of an empty string.
ℹ tests 17
ℹ pass 17
ℹ fail 0
 Test Files  2 passed (2)
      Tests  11 passed (11)
   Duration  534ms (transform 86ms, setup 0ms, import 153ms, tests 169ms, environment 156ms)
ℹ tests 15
ℹ pass 15
ℹ fail 0
 Test Files  1 passed (1)
      Tests  9 passed (9)
   Duration  630ms (transform 148ms, setup 0ms, import 239ms, tests 155ms, environment 156ms)
✓ built in 1.22s
✓ built in 441ms
✓ built in 433ms
✓ built in 552ms
✓ built in 444ms
```

## 전체 실행 후 발견 결함의 한정 재검증
- 01 필터/분석표 표시명 보완: 작성자 UI14 PASS(기존9+신규5), 정책6 유지, TypeScript/build PASS. 실제브라우저 재검수 대기.
- 03 빈 이미지 src/실패 카드 안내 보완: 작성자 전체21 PASS(기존17+신규4), TypeScript/build PASS. 실제브라우저 재검수 진행중.
- 따라서 위 전체명령 소스해시는 이 두 후속수정 전 기준이며 최종 build 해시는 후속동결 후 갱신한다. 관련 테스트만 재실행했으며 전체 결과를 새소스의 전체재실행으로 과장하지 않는다.
