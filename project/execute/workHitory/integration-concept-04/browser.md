# 시안 04 실제 브라우저 인수

root / RUNNING. 공통 로컬 테스트 DB, API:8000, AI:8010, 시안:5176.
가상 매대 이미지와 합성 질문으로 실제 AI 호출을 수행한다. 기존 사용자 승인 범위.
실제 UI, DB 메타데이터, 단위 검사와 독립 디자인 검수를 구분한다.

## 계획
HQ에서 qa04_labels 동일 키의 HQ/REGION/STORE/CATEGORY 기준과 Reference를 등록한다. 봄빛점/스낵의 전후 사진 제출, CATEGORY·Reference 버전 변경, OFC 확인·조치·알림과 운영 경계를 검증한다.

## E01 실제 첫 제출
- HQ03cd가 아닌 실제 HQ ID3cd24e5c-c191-4e71-955e-5b8f53f7d765, REGIONfdbd9805-09fc-4b0b-899a-34c39a9c45ed, STORE3e65241f-65eb-443a-9987-5b95ab72980b, CATEGORYafbd87b3-2b1e-487a-827a-25a2ea0eb8c9: qa04_labels 같은 키 4단계 실제 UI 등록. 매대가 봄빛역점/스낵에 우선 적용됨을 결과 본문에서 확인.
- 새 Reference는 snack-reference-01.png, 봄빛역점/스낵, 설명 `QA04 스낵 Reference v1: 선반 라벨과 앞줄 정렬 예시`. 등록 미리보기 원본 로드 확인.
- 모바일390×844 첫 화면·4단계: 빈 매장/분류 오류, 사진 미선택 오류, before+after 2장 선택→두번째앞으로→첫번째삭제 후 before1장만 보존, 이전단계 매장/분류/사진/질문 보존,2000자+x실제키 제한,최종확인내용 검수. 키보드Enter제출,전송중버튼disabled.
- 첫 submission e447d4e9-54c0-4c85-a0d6-20597b92d0ba, job5ad3342d-0a8b-40d5-a3f9-4cb4dbde42b2,reviewa6ec0539-7b6c-48ce-a193-1e296c11446c. 실제AI 모델70.973초,DB72.692초,브라우저첫관찰74.827초/직전대기74.721초. 관찰표본이며정확한paint시간아님.30초목표미달,지연안내실제확인.
- 기준5개/Reference3개/사진1개,준수0%/판단가능100%/높음,상품군혼재·앞줄·라벨·봉지밑단·간격 개선과구체행동/사진1근거,가격숫자·뒤쪽재고확인한계/OFC요청 구분.
- 적용snapshot 매대qa04_labels v1이상위동일키를대체,원래HQ/REGION/STORE/CATEGORY기준과함께총5개. 새Ref와기존스낵Ref2개가이미지/설명/차이관찰로표시. 사진근거버튼→사진1 이동.
- 자동이슈 a464fa6a-ef74-43d9-95bc-6ebd09b728fa와별도점주문의458992d7-7980-4dd3-9dd1-625241997fe6 생성확인. 아직조치대기.

## E02/E03 실제 재제출과 보존
- 매대 기준afbd87b3 v2 저장 직후 현재/버전2/버전1 모두 표시. Reference는 snack-reference-02.png와v2설명으로 교체. 과거 첫결과 재열람에서qa04_labels v1본문·이전Refv1원본loaded유지 확인.
- child80d35004-ef2b-4d18-8618-f2199b6878a2,parent첫제출 연결. 재제출4단계에서매장/분류고정,이전5판정펼침,after미리보기로드 확인 후 실제 제출.
- 모델64.762초/DB65.635초/브라우저첫관찰74.371초,직전대기66.229초/관찰공백8.142초이므로화면지연정확값아닌상한.30초목표미달.5기준·3Reference·사진1,준수100%/판단가능100%,새qa04_labels v2/Refv2 확인.
- 360×800 비교0→100%,두사진원본loaded,양쪽KST전체일시,기준별이전/현재v1및변경v2,직접비교불가주의와AI기록기반비교한계 표시. document.scrollWidth345/innerWidth360으로전체가로넘침없음.1440×900비교와버전구간도촬영.
- child자동OFC이슈b36acb71-b7cf-4b1c-8a5b-f072fee885ff 생성. 실제관리자검수이어감.

## OFC·점주 확인
- ofc.north 로그인에서담당2매장(봄빛역/은행길),HQ6매장/점주북부3매장과구분. 봄빛역+스낵조건적용→제출4/성공3/기술실패1/미해결4/표본3(Mock1),최신근거child연결. 상세목록복귀링크에지역/매장/분류/기간조건보존.
- 사진1근거버튼→제출원본확인→자동child이슈. ofc.north조치댓글저장→해결내용입력/해결상태저장,이전댓글과해결이력보존. 빈해결내용저장을시도했으나그오류화면을별도관찰하지않았으므로필수오류검증PASS로쓰지않음.
- 분석Mock배지/비인과설명/n6/r-0.0147/결측1·판단불가3제외. 생활용품조건은기간자료없음,n0/상관—/3개미만안내/매장별준수·판단가능·매출—확인.
- 점주모바일알림최신조치읽음→같은해결이슈이동,해결내용·댓글/이력열람가능,관리수정폼없음. 수신함재조회로읽음버튼감소확인.

## 운영·권한·경계 후속
- 새계정 qa04.owner.7391f994 / b2d7e6b5-a0b9-4b2e-9a9b-e674c920fac0,비밀번호는로컬0600별도보관. 봄빛역점만연결→별도127세션원본결과접근→localhost운영계정비활성화→기존세션재조회로그인/이미지0→재활성화새로그인→검증연결종료→기존상세404본문/사진제거.
- 새계정역할OFC/북부로변경→기존점주경로접근불가/시작화면OFC. 같은지역미배정푸른언덕점담당후보만노출→사유/확인후등록→담당목록1개/후보없음. 검증후점주로복구하며시험OFC연결1개종료,활성/미연결로보존. 기존담당자는변경안함. 감사계정v6→v7/OFC→점주/연결종료/actor·reason·result전체펼침검수.
- E05 fixture job667d69ab-2eca-565b-b5d7-7b2736b2b57c: 최초AI_UNAVAILABLE시도1보존. 빈사유native필수오류→사유입력/영향확인→실제재처리2대기→성공/결과반영완료. 진행·성공상태에재처리폼없음. retry-running파일은실제queued촬영이므로분석중으로해석하지않음. 성능정상신규표본에서제외.
- 운영자서비스/모델상태와Mock장애사례분리,영업결과직접경로접근불가본문없음. 독립liveHTTP403/범위외검증은별도검토진행.
- QA04 현장포켓공지생성→지역북부배너표시/종료된시드공지비노출. qa04_test_category신규→QA04검증완료분류이름변경/비활성/코드보존,변경확인단계검수.
- regional.north북부3매장/OFC북부2/HQ6차이,남부첫03결과직접상세404/사진0.1280×800비교가로넘침없음.
- 기준/Reference없는Mock과거평가540333dc(0개/준수—/판단가능—/OFC),실제unknown e9fd4f27(5unknown/준수—/판단가능0%/재촬영한계),북부기술실패이력(서비스연결실패/복구안내)구분표시.
- D04-V01 360px사진삭제버튼돌출은44px/wrap으로수정.360/390실제44×48·사진미리보기보존/문서overflow없음,독립시각PASS. D04-V021440사진sticky가질문가림은sticky제거후regional.north같은사진근거흐름재촬영;사진bottom386.18/질문top435.18,독립시각PASS. 영향테스트/빌드와최신hash는frontend-integration-dashboard/layout04-final-sha256.json.
- vp-mobile390-unmapped-empty.png은축소캡처결함이므로정상증거제외,unmapped-empty-fixed.png가교체본. 모든viewport파일은fullPage:false이며전후태그와실측을구분.
- E06 통신오류/queued지연fixture,200%와E08최종preview·HTML매뉴얼실제검수는미완료.
- 독립 보조 검증64개/실제HTTP14개PASS. operator영업detail/원본/thumbnail/알림403,owner.north남부상세404,regional.south북부detail/media404. 정상범위대조200/검증세션logout204. 근거 independent-review.md·independent-metadata-http.json·independent-probe.py. 브라우저권한검증과분리.
- retryfixture submission a24ff9dd-8389-5d8b-9234-0d4cfa98e9d8,모델47.432초/대기1.897초/실행47.540초. 과거시드제출부터시간은정상성능표본에서제외. actual-ai.json3건보존. retry-success-applied.png에2번째시도성공/결과반영완료구간추가.
- QA04 운영 공지 비활성화 저장완료. 다음시안로그인전운영세션로그아웃.

### 독립 미디어 권한 증거 정정
기존 독립64검사/HTTP14 결과 중 제출 사진 경로에 SubmissionPhoto ID를 사용한 지역404 검사는 실제 보호사진 범위 차단 증거에서 제외한다. 기존 산출물은 `independent-metadata-http-incorrect-media-target.json`에 PARTIALLY_INVALIDATED로 보존됐다. 최신 독립 재검증은 실제 media_id `2e2c314d-0a13-404d-8627-5ecff861ebcc`의 원본·thumbnail에서 owner.north200(원본hash일치) → operator403 → regional.south404를 대조하여 67검사/HTTP16 PASS다. `independent-review.md` 정정본을 최종 근거로 사용한다. 상세/Reference/스냅샷의 기존 유효 검사는 유지한다.
