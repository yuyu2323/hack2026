# 내장 브라우저 200% 확대 제안 · DOC-ZOOM-001

상태: DOCUMENT_REVIEW_COMPLETE / 실제 UI NOT_RUN

## 결론
현재 설치된 앱에는 내장 브라우저 전용 확대 조작이 있다. root가 실제 화면에서 **Browser options → Zoom → Zoom in** 버튼을 눌러 표시값이 **200%**가 되도록 확인하는 방법을 우선 권장한다. 동일 그룹의 **Reset**으로100%로 되돌릴 수 있다. 이 문서는 읽기 전용 소스/공식 문서 확인 결과이고, 메뉴를 실제로 열거나 확대를 실행한 결과가 아니다.

## 확인 근거
- [Computer Use 스킬](/Users/soonkee/.codex/plugins/cache/openai-bundled/computer-use/1.0.1001103/skills/computer-use/SKILL.md)을 읽었다. UI 동작은 node_repl의 @oai/sky를 사용하고 get_app_state로 최신 AX를 확인한 뒤 element_index를 써야 한다. 이번에는 root의 조작 금지 배정에 따라 get_app_state/list_apps/키/클릭을 포함한 앱 동작을 호출하지 않았다.
- 설치 경로는 `/Applications/ChatGPT.app`, bundle ID는 `com.openai.codex`, 버전26.915.31945/build9922다. 번들의 app.asar를 읽기만 했다. 앱 파일을 추출해 실행하거나 수정하지 않았다.
- `webview/assets/tab-content-06f66038d12c.js`: `thread.browser.options`의 기본 접근성 이름은 Browser options다. 그 메뉴의 Zoom 그룹 안에 Zoom out, 현재 백분율, Zoom in, Reset 버튼이 실제 구현되어 있다. 숫자는 텍스트이며 드롭다운이라고 추정하지 않는다. 브라우저 탭에 연결된 확대 명령으로 전달된다.
- `.vite/build/main-DUHZj4_w.js`: 앱 메뉴의 Zoom In은 CmdOrCtrl+Plus, Zoom Out은 CmdOrCtrl+-, Actual Size는 CmdOrCtrl+0으로 등록된다. 확대 핸들러는 먼저 focused visible browser page 명령을 보내고, 해당 페이지를 찾지 못하면 step-window-zoom으로 넘어간다. 따라서 앱 전체 글꼴 확대를 페이지200% 검증으로 오인하지 않으려면 브라우저의 옵션 메뉴를 쓰는 편이 명확하다.
- [공식 단축키 문서](https://learn.chatgpt.com/docs/reference/commands)는 macOS 증가/감소/초기화로 ⌘+Plus/⌘+-/⌘+0을 안내한다. 문서 자체는 font size 명칭이므로 내장 브라우저만 확대되는 증거는 위 로컬 코드와 실제 root 조작에서 별도로 확인한다. [공식 Browser 문서](https://learn.chatgpt.com/docs/browser)에는200% 조작의 상세 안내를 찾지 못했다.
- 파일별 해시·버전·정확한 식별자는 `browser-zoom-source.json`에 기록했다. 확인을 위해 앱의 비밀/인증/브라우저 저장소를 열지 않았다.

## root의 실제 검증 절차 제안
1. 현재 작업 중인 Browser 탭과 사이트를 유지한다. computer-use 스킬에 따라 `sky.get_app_state({app:'com.openai.codex'})`로 최신 AX/화면을 확인한다. 저장된 좌표나 임의 element_index를 사용하지 않는다.
2. 브라우저 툴바의 Browser options(앱 언어에 따라 번역된 이름일 수 있음)를 열고 Zoom 그룹을 찾는다. Zoom in을 한 번씩 눌러 매번 새 상태를 읽으며 **200%** 표시를 확인한다. 초기 비율을 기록하고 임의 고정 클릭 횟수로200%라고 단정하지 않는다.
3. 메뉴를 닫은 뒤 실제 페이지의 텍스트·컨트롤/줄바꿈·표 스크롤·고정 탐색·포커스가 유지되는지 확인한다. 브라우저100/200% 표시의 전후 증거와 사이트 viewport/배치를 함께 남긴다. 단순 OS 화면 확대, 이미지 확대, viewport 축소를 같은 검사로 기록하지 않는다.
4. Mac 네이티브 View → Zoom In 또는 ⌘+Plus는 대안이다. 일반 US 자판의 Plus는 Shift+= 조합이지만 실제 키보드/도구 조합을 가정하지 말고 메뉴 항목을 확인한다. 페이지 본문에 포커스가 없으면 앱 전체 글꼴만 바뀔 수 있어 전용 Zoom 메뉴가 우선이다.
5. 검사가 끝나면 같은 Browser options → Zoom의 Reset으로 원래100%로 복귀시키고 기존 탭/URL/세션이 유지되는지 확인한다. 실제 메뉴가 없거나 비활성이면 버전/표시 상태와 함께 NOT_RUN으로 남기고 내부 IPC·DevTools·CSS 강제 확대를 검증 우회로 사용하지 않는다.

화면200% 표시와 실제 레이아웃 확인 이전에는 확대 검증 PASS로 처리하지 않는다. 본 작성자는 앱/Browser를 조작하지 않았고 서비스나 세션도 변경하지 않았다.
