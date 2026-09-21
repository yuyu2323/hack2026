# F03-UPLOAD 파일 선택 체크리스트

root의 모바일 실제 제출 차단 재현에 따라 product_design이 Submit 파일 선택 핸들러와 신규 회귀만 소유한다.

- [x] 원인 후보 확인: React StrictMode에서 state updater가 나중에 다시 실행되면 비운 input.files를 읽는다.
- [x] 브라우저의 input.value='' → files 비움과 StrictMode를 함께 재현해 RED.
- [x] 이벤트 안에서 FileList를 복사하고 updater는 복사 배열만 사용.
- [x] 연속 선택·미리보기·제출 파일 보존 회귀 및 전체 테스트/build.
- [x] REVIEW 동결, root 실제 모바일 재제출/AI 인계.

REVIEW 동결: 24 PASS/build PASS. root 실제 모바일·실제 AI 인수는 별도 진행.
