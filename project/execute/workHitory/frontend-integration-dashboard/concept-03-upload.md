# F03-UPLOAD 보완 기록

root가 owner.south 사진 선택 후 files=[]/미리보기 없음/콘솔 오류 없음으로 실제 모바일 업로드 차단을 확인했다. Submit 핸들러는 updater 내부에서 e.target.files를 읽은 뒤 input.value를 비우고 있었다. 앱 entry는 React.StrictMode이며 updater의 지연/재실행에서 DOM 상태는 이미 비어 있을 수 있다. 기존 fireEvent.change({target:{files:[...]}}) 테스트의 plain array는 input.value 초기화와 연동되지 않아 이 경계를 검증하지 못한다.

새 회귀는 실제 React.StrictMode와 브라우저의 value 초기화→files 비움 동작을 흉내 내는 input getter/setter를 사용해 React updater가 비워진 DOM을 읽는 실패를 재현한다. 제품 변경은 이벤트 핸들러에서 배열을 즉시 복사하는 한 줄 변경으로 제한한다. 공유/미리보기/다른 페이지/패키지/브라우저·DB 변경 없음.


## RED → GREEN · REVIEW 동결

- 새 tests/file-selection.test.ts는 수정 전 첫 사진 미리보기를 찾을 수 없어 RED였다. React.StrictMode가 재실행한 updater가 초기화한 input.files를 읽는 조건을 재현했다.
- Submit onChange는 e.currentTarget.files를 이벤트 중 selected 배열에 즉시 복사하고 updater에서는 그 배열만 참조한다. input.value='' 동작은 유지해 같은 파일을 재선택할 수 있다.
- GREEN: 최초 선택 미리보기, native input 비움, 다음 파일 추가 미리보기, multipart에 실제 File객체가 원래 순서로 전달됨, 접수 결과 경로 이동까지 검증했다. 전체24 PASS, TypeScript/Vite build PASS(index-CV-ES-ec.js).
- 제품 소스 변경은 store-owner/pages.tsx Submit onChange 하나. 테스트 파일1개 신규. root에 즉시 재시도 가능 상태와 REVIEW 동결 전달했다. 실제 모바일·AI 인수는 root 후속이며 본 결과와 구분한다.


## root 실제 모바일 확인 수신

root는03 390px에서 미리보기 image loaded=true, 파일명2.2MiB/사진1, Tab으로 제출focus, Enter접수와 busy중복방지를 실제 브라우저로 확인했다고 전달했다. 증거 vp-mobile390-first-preview.png. 실제AI 첫 제출 진행 상태이며 이 보완의 실제UI 확인을 전체AI 인수로 확장하지 않는다.
