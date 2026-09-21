# 시안03 모바일 질문 경계·오류 UX 준비

상태 SOURCE_REVIEW_ONLY. root 요청에 따라 소스만 확인했고 직접 브라우저·실제 API·제품 소스·서비스·DB를 조작하지 않았다. 실제 판정은 root가 수행한다.

## 확인한 계약과 구현

- `web-concepts-03/src/store-owner/pages.tsx` Submit: `question`은 React 상태이며 textarea `maxLength={2000}`, `rows={4}`, 선택 입력이다. 현재 길이를 `question.length/2,000자 · 선택 입력`으로 표시한다. `server/submissions/schemas.py`도 `question: str = Field(default='', max_length=2000)`을 적용한다.
- `question.length`와 DOM maxlength는 UTF-16 code unit 기준이다. 기본 경계 시험은 한글·ASCII처럼1 code unit 문자를 쓰며 이모지의 육안 글자 수와 차이가 있음을 별도 참고한다. 서버/클라이언트 경계에 관한 일반 UI 안내를 새로 확장하거나 코드는 수정하지 않았다.
- Submit은 `validatePhotos(files)`가 실패하면 `setValidation(problem); return`하여 upload를 호출하지 않는다. 사진0장이면 `사진은 1~5장을 선택해 주세요.`를 사진 구간의 `p role=alert`로 표시한다. 질문 값과 매장/카테고리는 초기화하지 않는다.
- 사진 검증 실패 메시지의 자동 focus/scroll 코드는 없다. 모바일 질문·제출 영역에서 오류 발생 시 실제 viewport에 문구가 드러나는지는 브라우저 확인이 필요하다. 소스만으로 접근성 실패나 통과를 확정하지 않는다.
- 서버/API 오류는 Submit 아래 FormStatus/ErrorBox에 표시되고 입력 상태는 유지한다. busy 동안 제출과 파일 입력은 disabled다. 질문에는 명시 required가 없으므로 빈 질문 허용은 정상이다.

## root 실제 브라우저 준비 항목

| ID | 조작 | 기대 관찰 | 실제 상태 |
|---|---|---|---|
| QB03-01 | 활성 연결 매장/카테고리 선택, 사진 없이 점주 질문에 한글2,000자 입력 | counter2000/2,000, value길이2000, 모바일가로overflow없음 | NOT_RUN |
| QB03-02 | 끝에서 일반키1자 추가 입력 | native maxlength가 추가를 막아2000유지; 붙여넣기도 실제maxlength동작 확인 | NOT_RUN |
| QB03-03 | Tab으로 제출버튼 이동·Enter(사진0장) | role=alert의 사진1~5장안내, 질문/매장/category 유지, POST /submissions없음, 실제AI추가실행없음 | NOT_RUN |
| QB03-04 | 오류가 보이지 않으면 현재scroll/focus·문구위치를기록하고사진구간으로이동 | 안내의발견가능성/키보드초점/해결동선 실제평가; 위치수정을미리단정하지않음 | NOT_RUN |
| QB03-05 | 질문을 지우고 같은 사진없는 제출 | 질문은선택입력,질문필수오류없고사진검증만나옴 | NOT_RUN |

실제API 422·CSRF·네트워크오류 입력보존은 기존 회귀/별도 인수와 구분한다. 이 준비를 위해 서버를 중지하거나 실제AI 실패를 의도적으로 유발하지 않는다. nativemaxlength를 우회한합성단위시험은 실제브라우저입력검수로세지않는다.


## root 실제키검수 결과 수신

root browser.md 후속실제재검수에서390×844 질문2000자,실제x키추가입력후length2000/maxlength2000 유지,문서가로넘침없음이확인됐다. 사진없이매장/분류선택후제출은사진1~5장경고와질문보존,실제AI호출없음을확인했다. 이는QB03-01/02/03 해당관찰PASS이며본에이전트직접실행이아니다. QB03-04 오류focus/위치의상세평가및QB03-05빈질문별도검수는수신되지않아NOT_RUN유지한다.

CUA 문자열삽입은maxlength를우회해2002자가됐다는도구특성을root가별도기록했다. 실제키x입력제한PASS와혼합하지않으며2002문자삽입을사용자키입력제한실패의근거로취급하지않는다. source여기에추가수정없음.
