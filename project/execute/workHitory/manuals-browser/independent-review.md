# 매뉴얼 PNG 독립 시각검수

현재 후속 판정: 수정 후 10장 직접 재검수로 D-MAN-H01과 OBS-MAN02-01이 해소됐다. [최신 재판정](independent-recheck.md)은 PASS_WITH_NOT_RUN이며, 아래 초기 관측과 근거는 이력으로 보존한다.

판정: **REVIEW_COMPLETE_WITH_OPEN_FINDING**. contract_data가 HTML 작성자와 분리하여 5개 시안의 데스크톱·모바일 Browser 렌더 PNG 22장을 `view_image`로 직접 확인했다. 초기 21장 전부와 추가 `concept-01-desktop1440-runtime-final.png`가 대상이다. 파일별 크기·SHA-256·관측은 [독립 근거](independent-evidence.json)에 기록했다.

## 발견 사항

**D-MAN-H01 — 01·03·04·05 상단 작성일·역할 문구의 낮은 대비.** 네 시안의 `desktop1440-top.png`에서 링크를 제외한 작성일·역할 글자가 어두운 배경에 묻혀 읽기 어렵다. 01의 추가 `runtime-final.png`에서도 재현된다. 읽은 CSS의 글자색 `#516977`과 배경 `#173c48`을 계산하면 대비는 약 2.047:1이다. contract_ai가 먼저 전달한 동일 결함을 PNG에서 독립 확인했다. 작성자 수정과 root 최신 재캡처 후 재판정이 필요하다. 본 검수에서 HTML은 수정하지 않았다.

**OBS-MAN02-01 — 경미한 가독성 보완.** `concept-02-mobile390-table-fixed.png`의 시연 로그인 ID가 `owner.no`/`rth`, `ofc.nort`/`h`처럼 단어 중간에서 줄바꿈된다. 글자가 사라지거나 겹치지는 않아 기능 차단으로 판정하지 않는다. 정확히 옮겨 적기 쉽도록 해당 열의 코드 문자열에 줄바꿈 금지와 충분한 열폭을 적용하거나, 초점 가능한 표 내부 가로 스크롤을 유지하는 보완을 권한다. 수정 여부는 작성자/root가 판단한다.

## 직접 관측

| 시안 | 직접 연 파일 | 확인 결과 |
| --- | --- | --- |
| 01 | desktop top/evidence, mobile image/table, 추가 runtime-final (5장) | 본문·삽입 사진·캡션 정상. 표 초점 테두리와 내부 가로 스크롤바가 보인다. 추가본에서 본문 건너뛰기 초점 및 Node 22.12/npm 10 문구 확인. D-MAN-H01 잔존. |
| 02 | desktop top/recovery, mobile image/recovery/table-fixed (5장) | 본문과 상태별 안내 표 가독성 양호. 표 수정본의 주황색 초점 테두리 및 3개 열 정상. 로그인 ID 중간 줄바꿈 외 새로운 결함 없음. |
| 03 | desktop top/evidence, mobile image/table (4장) | 판단 불가·기술 실패를 구분한 그림과 캡션이 서로 맞는다. 전후 비교 캡션·원본 보기 표시 정상. D-MAN-H01 잔존. |
| 04 | desktop top/evidence, mobile image/table (4장) | 사진 선택 그림·파일 상태 설명과 운영 재처리 캡션이 보이는 화면과 맞는다. 표 초점·스크롤 정상. D-MAN-H01 잔존. |
| 05 | desktop top/evidence, mobile image/table (4장) | 재처리 두 시도와 모바일 비교 오른쪽 열의 캡션이 보이는 이미지와 맞는다. 표 초점·스크롤 정상. D-MAN-H01 잔존. |

확인한 PNG 안에서 깨진 이미지, 본문 겹침, 문서 전체의 가로 잘림, 캡션과 이미지의 의미 불일치는 관측하지 않았다. 01/03/04/05 계정 표의 왼쪽 일부가 안 보이는 장면은 가로 이동된 내부 표이며, 초점 테두리와 스크롤바가 보인다. root의 별도 DOM 기록도 해당 표 `scrollLeft=40`을 기록한다. 이를 문서 넘침으로 오판하지 않았다. PNG 상·하단에서 이어지는 내용은 viewport 밖이므로 요소 잘림으로 판정하지 않았다.

## 범위와 제한

- root의 [렌더 기록](render.md)과 [모바일 DOM 관측](mobile-dom.json)을 읽었다. 해당 기록의 키보드 실행·이미지 전체 로드 수는 root의 관측이며 독립 재실행으로 표기하지 않는다.
- 파일 이름의 1440/390은 요청 viewport이다. 실제 PNG는 데스크톱 1425×891, 모바일 375×812이다. root DOM의 문서 폭 1425/375 기록과 구분하여 보존했다.
- 01/03 초기 상단 PNG는 명령 문구 수정 전일 수 있어 레이아웃 검수에 사용했다. 01 추가본의 최신 문구는 직접 보았으며, 03 최신 문구 재캡처는 이 판정에 포함하지 않았다.
- **200% 확대는 NOT_RUN**이다. 사용자가 후속 진행을 선택했으며, 모바일 viewport 확인으로 대체하지 않았다.
- 이번 독립 검수는 기존 PNG의 보이는 범위에 한정한다. Browser 직접 조작, 전체 문서의 모든 위치, 링크 동작, 인쇄, OS 네트워크 차단, 서비스·DB·AI 검증은 수행하지 않았다.
- HTML·이미지·Browser·서비스를 변경하지 않았다. 작성 파일은 `execute/workHitory/manuals-browser/independent-*`뿐이다.
