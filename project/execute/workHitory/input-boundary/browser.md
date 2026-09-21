# 실제 입력 경계 검증
root / RUNNING. 테스트 DB UI·추가 AI 호출 없이 업로드 선택/입력/삭제·긴 질문·없음 상태 검증. 원본 생성 이미지 보존.

- 5개 시안 실제 선택: unsupported.txt,10MiB+1 oversize.png,생성된6장 원본. 01/03은 제출 버튼에서 형식/용량/개수차단,02/04/05는선택시차단. 사진0장은01/02/03 제출오류,04다음단계오류,05기본disabled를확인. 5장정상미리보기와2번째사진앞으로이동/기존첫사진삭제 확인(01/03 6→5,02/04/05 5→4). 이미지로드와번호순서·질문보존 실제DOM저장.
- 모든시안질문2000자fill 뒤 실제 x키 추가입력이 제한됨. 04는확인단계까지이동하여정렬사진·질문보존,최종제출하지않음. 추가AI호출없음. browser-evidence.json 및 시안별 vp-mobile390-photo-order-boundary.png. 유효파일경계의정확10MiB/합계50MiB와긴기준본문은이번브라우저검증미포함.

- 01/02/05 기존Mock boundary-no-criteria submission540333dc-3e4d-5864-8d4b-0ae75d2da2a1을실제점주화면에서재열람. 기준0/Reference없음,Mock표시,준수율·판단가능률—/표본0of0·OFC확인안내확인.05고정기준영역펼침. 신규분석없음; 각 vp-mobile390-no-criteria-reference-final.png.
- IB-C01 실제FAIL:01기준 c56aae03-c8c0-4d82-bbd5-dcd0043dc4b2(기존QA비활성)의v1초안/사유입력→별도02v2저장→01저장409→최신v2재조회때초안과사유소실. JSON/PNG보존,product_design회귀수정중. 해당기준비활성유지.
- 별도02Reference신규등록중/forbidden이동관측.같은시간HMR수정과겹쳤고실제응답code를수집하지않았으므로CSRF원인으로확정하지않음. 후보CSRF회귀는저자실제App RED로별도입증.등록여부확인후재시도예정.

- 02 수정후실제Reference검증: 새전용푸른언덕/음료Reference생성v1(기존본문/기록불변),두번째02화면v2선행저장. 첫화면은실제CSRF오류에서caption/reason/선택beverage-reference-02.png보존·재전송안내표시. 명시재저장→실제409(Reference변경),최신정보다시읽기→서버v2설명표시+초안/파일유지,추가명시재저장→v3/새media9ab1b0aa-a778-49d5-a8cb-9319de62a747성공. AI호출없음. reference02-{csrf-preserved,conflict,refreshed,saved}.json. 이합성lineage는01/04추가복구확인후비활성화예정.
- 01 수정후같은비활성criterion v2초안→별도02v3선행저장→실제409후v3재조회에서도초안/사유유지PASS. conflict01-after-fix.json. 명시재저장확인진행중.

- 01 기준명시재저장v4비활성성공. Reference도실제CSRF입력보존→명시재시도409→최신Reference확인v4→caption/reason유지→명시v5/선택이미지반영성공. 04실제409→최신v6조회후caption/reason/beverage-reference-02미리보기보존→명시v7성공. 각reference01/04-{conflict,refreshed,saved}.json.
- 사용자최신지시에따라추가경계검수중단·매뉴얼우선인계. 합성Reference전용lineage는02화면에서사유입력후비활성화했으며활성목록에서제거확인. 검증용기존비활성기준 c56aae03...는v4비활성유지. 미실행05추가충돌검수는진행하지않고새05탭닫음.
