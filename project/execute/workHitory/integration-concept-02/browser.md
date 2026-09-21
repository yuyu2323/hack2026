# QA02-001 실제 브라우저 인수 진행 기록
- 담당 root, 구현자 concept02와 독립. 선택Browser는 Codex in-app browser, 127.0.0.1:5174 점주/영업과 localhost:5174 운영자는host-only 쿠키로세션분리. 인증저장소는읽지않음.
- 테스트 DB storeloop_test와 test-media, 공용시연DB미사용.
- 실제AI before→after: 질문/4기준/2Reference입력, schema검증후저장, 기준50%→100%,facing/shelf_gap개선. actual-ai.json 참조. 첫AI서비스종료로실패→운영자사유재처리→attempt1실패와attempt2성공보존. 초기실패도실제서비스실패이며Mock대체없음.
- 지연: 첫AI실행51,710ms, 최초제출→DB295,934ms(운영복구대기포함). 재제출model47,049ms,제출→DB47,060ms. 브라우저첫표시정확시각은이두표본에서미기록; 화면47초·296초는서버계산값이며정확한submit_to_visible실측으로오인하지않음.후속표본에서UI표시상한측정추가예정.
- E02: OFC관제→최신사진근거→QA02문의→조치코멘트→해결사유완료→점주알림내용확인→완료이력 성공.
- E03: QA02기준v1등록→v2변경·과거버전보존,Reference v1업로드미리보기→v2다른이미지교체→비활성이력보존. 기존첫평가4기준/2Ref원본유지확인. 변경후새제출검증대기.
- E07: Mock상관/표본/제외수/기간리포트,생활용품필터 표본0·rNULL·결측— 표시확인.
- E04: operator UI로독립QA계정 qa02.owner.13d33e9e(22b4defd-15bf-478c-a23e-613fcf4134eb)새로생성·봄빛역점연결. owner기존로그인상태에서운영자비활성화→다음조회로그인회수확인. 다시활성후같은계정재로그인→테스트매핑종료검증.
- 매핑종료는자동승인검토가처음구체승인부족으로거절. 읽기전용DB조회로이번테스트생성시각/ID/매핑1건사유를증명하고목표E04권한을근거로같은UI변경재시도승인·성공. 우회API사용없음. 공용시연계정/연결은변경하지않음.
- 캡처결함: fullPage:true 합성이축소/중복되어독립디자인검토용으로부적합. 원본보존, vp-파일은fullPage:false 정상크기로새촬영. viewport390×844에서innerWidth390/clientWidth375/DPR1로15px스크롤바확인.
- 시안02최신PD003/메타데이터/명칭표시수정13test/buildPASS. 독립디자인이발견한컨트롤/NULL대비는root가CSS2토큰보완,검토자비율3.42/6.31PASS. 최종viewport증거추가중.

## 변경 기준·판단 불가 추가 인수
- 세 번째 실제 e9fd4f27-0d3e-42a1-9e58-9c255f49d703은 낮은 조도·흐림·가림 사진에서5기준 unknown, 준수율NULL/판단률0,신뢰도낮음/OFC필요를 반환. UI 숫자—와 계산불가 사유·사진별 관찰·재촬영 행동 확인.
- qa02_labels v2·추가 Reference v2가 신규 snapshot(5기준/3Ref)에 반영. 이전 결과는4기준/2Ref 유지.
- 비교에서 모든 판정 비교불가와 추가qa02_labels 기준버전변경, 단순점수 비교주의문구 확인.
- 모델92,888ms/제출→DB94,166ms/브라우저 첫완료관찰상한111,334ms. 마지막은 도구 호출 간격 포함 상한으로 연속 정밀계측과 구분.
- 신규 캡처 vp-mobile360-{changed-criteria-compare,unknown-evidence,reference-snapshot}. 마지막 Reference번호1반복은독립디자인D02-P2로수정중, 새화면재검수필요.
- 콘솔의09:20~09:55UTC HMR createRoot중복/removeChild오류를 발견, 5개entry기존root재사용수정/회귀·buildPASS. 최종freeze/preview깨끗한콘솔은별도확인예정.

## 운영·기준 추가 인수
- QA02 합성계정22b4defd-15bf-478c-a23e-613fcf4134eb 기존owner세션중OFC북부로변경→기존owner화면권한차단/기존데이터제거. 담당후보푸른언덕1개→사유등록후관리목록1/후보0즉시갱신. owner/regionNULL복원v7·매장0·종료1영향1,감사beforeOF C북부/푸른→afterowner/null/0·ended731e73ed-dcec-47fb-9c06-c4e384826fb5확인.
- qa02_test_category/4f49fc31-ad68-4f63-8bec-0dc9cac0c69d 생성→QA02검증완료분류/비활성v2,코드고정.
- qa02_labels 상위HQ2d4ea8b1-116c-430e-8e06-e80ba477484b,REGION2089bf7c-3836-441c-9d00-7a32eb6a0436,STOREd422d014-58d6-4d90-ae76-d4502709dad7 UI등록. 독립현재resolve에서4후보중기존CATEGORYv2단일승자확인후3upper비활성정리. 이3개는실제AI3건이후등록이므로당시입력에4단계후보가있었다고주장하지않음.당시실제snapshot3건불변은별도독립검증PASS.
- 공지8364b4a5-9704-4fa1-b5e7-300fad961aed QA02오늘할일시연안내 등록(시작21:57KST,실제저장21:58)→owner노출/종료공지미노출→이번공지비활성→ownerreload미노출. SPA에이미읽힌배너와서버현재값은다르므로reload관측명시.
- 지역north3/HQ6개매장범위정상. UI02적용Reference3장모두원본로드/번호1·2·3수정실제확인. 모바일390문서375로가로넘침없음. 전후비교날짜2026-09-21 18:30/19:05 KST와qa02_labels 이전미적용→현재v2/다른unknown직접비교불가확인,데스크톱1440문서1425정상.
