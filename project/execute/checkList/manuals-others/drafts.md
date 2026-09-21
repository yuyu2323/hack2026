# 사용자 매뉴얼 01·03·04·05 초안

- 담당: product_design
- 상태: REVIEW · 01 화면8장, 03/04 화면10장씩, 05 화면12장 · 정적4 PASS · 최종 문서 브라우저 검수 대기
- 소유: deliverables/manuals/concept-{01,03,04,05}/** 및 본 체크리스트/이력. concept02는 contract_ai 소유이며 수정하지 않는다.
- 근거: docs02 §10·docs09 E01~E08·docs10 G5, README/실제 실행 스크립트, 각 시안 실제 메뉴/폼/경로.
- [x] 명세 및 실제 소스·시연 로그인 ID만 확인 (비밀번호 출력/복사 없음)
- [x] 시안별 독립 동선으로 오프라인 HTML4개 작성
- [x] 역할·입력·상태·실제AI/Mock·지연·모바일·로컬실행·시연 순서 포함
- [x] 초안 NOT_RUN/캡처 미포함 명시, 가짜 화면이나 깨진 이미지 없음
- [x] 내부 앵커/로컬 링크/UTF-8/비밀 비노출 정적 검증
- [ ] root의 정확한 vp-*.png 인계 후 시안별 화면·캡션 반영
- [ ] 실제 브라우저 문서 렌더·모바일/오프라인 이미지 검수 (root/contract_ai)
- [x] 비교자료 `deliverables/frontend-comparison.md` 연결, root 선택 정본 경로 `execute/question/frontend-selection/select-concept.md` 수신
- [x] root 선택 정본 생성 후 네 문서에 클릭 링크 연결

정적 증거: `execute/workHitory/manuals-others/static-validation.json`. 현재 01은8장, 03/04는10장씩 실제 화면을 반영했다. 05는 실제 결과·비교·조치·운영12장을 반영했으며 네 문서 모두 최종 브라우저 문서 검수 미완료다.

## 01 실제 화면 반영 · MAN-IMG01

- 상태: REVIEW · 실제01 화면8장과 재제출/OFC해결 반영. 03/04/05는 선택 링크만 연결, 02는 수정하지 않았다.
- [x] 실제 01 viewport PNG 직접 확인 후 대표 5~8장 로컬 원본 복사
- [x] 캡처가 실제 보여주는 동작만 캡션·alt로 설명
- [x] 첫 실제 AI 정본/91,732ms 브라우저 지연 반영, 재제출 포함 전체 PASS로 확대하지 않음
- [x] 네 문서 선택 링크와 상대 이미지/앵커 정적 검증
- [ ] root 매뉴얼 실제 브라우저 렌더·contract_ai 이미지 독립 검수 결과 반영


## MR-004 / MEDIA-CLARIFY-2 보완

- [x] 01/03/04/05 header 전용 focus outline 밝은색으로 수정, 본문 규칙 유지.
- [x] 영업 관리자의 현재 관리 범위 내 교체·비활성 Reference 사진 확인 및 점주/운영자 범위 유지 설명.
- [x] 대비 계산·4개 정적 재검증 후 독립 검수 인계.

## MAN-IMG03 최초 화면 반영

- [x] root가 인계한 정상 viewport6장 직접 확인(관제·모바일미리보기·처리·Mock판단불가·기술실패·빈이력).
- [x] 원본 복사·캡션/alt·실제 decoded dimension/format·hash 기록.
- [x] 사진 우선 관제 설명과 실제 AI 미완료 상태를 정확히 반영.
- [x] 정적검사 후 REVIEW 동결, root 실제 문서/contract_ai 독립 검수 대기.

## MAN-IMG03 실제 AI·재제출 반영

- [x] root actual-ai.json과 first/child-latency.json, 새 viewport 원본 직접 대조.
- [x] 대표8장으로 갱신하고 실제 첫답·child답·전후사진·Reference 버전 업무에 연결.
- [x] 별하천점·음료 60%/100%와 기준변경 비교제한, 모델/DB/Browser 관찰 지연을 구분.
- [x] 전체 인수·문서 브라우저 검수 미완료 유지, 정적 검사 후 REVIEW 동결.

## MAN-IMG03 최신 비교·운영 처리
- [x] 새 dates-fixed/versions-fixed/운영재처리success 원본 직접 열람, 실제 촬영 viewport 정정기록 대조.
- [x] 옛 비교복사본 교체·전후버전/운영처리 그림 추가와 정확한 캡션.
- [x] 질문2000자·오류UX 소스확인만 수행하고 root 테스트 준비 정보 전달.
- [x] 정적 검사 후 REVIEW 동결, resolved 점주 그림은 요청대로 미교체.

## MAN-IMG04 실제 화면·지연 반영
- [x] 정상 viewport10장 직접 열람·원본 복사와 역할별 alt/캡션 작성.
- [x] 수정 전 미리보기/근거/축소 이미지 제외, D04-V01/V02 수정본 사용.
- [x] 첫/child 실제 지연 및 관찰창·30초 미달·변경 기준 비교 한계 구분.
- [x] 정적4 PASS 및 REVIEW 동결. 실제 문서 렌더·독립 검수 인계.

## MAN-IMG05 최초 화면 반영
- [x] 최초 정상9장 직접 열람 후7장 원본 복사·정확한 caption/alt 연결.
- [x] 노을공원점·음료 시연 및 첫 완료 인계/관찰창과 후속 증거 대기 구분.
- [x] 정적4 PASS,01/03/04 본문 hash 유지. 첫7장 REVIEW 동결.
- [ ] 결과·재제출·운영 사진은 후속 인계 후 추가한다.

## MAN-IMG05 실제 결과·비교·조치10장
- [x] 정상 후속7장 직접 열람 후 이전 대표3장과10장 구성/manifest 갱신.
- [x] 60→100%/기준변경 비교불가·child 타이머 오류 상한을 정확히 구분.
- [x] 정적4 PASS·다른매뉴얼hash 유지 후 REVIEW 동결.
- [ ] 운영 화면·문서Browser/200%/오프라인 최종 인수 대기.

## MAN-IMG05 운영2장 최종 반영
- [x] 정상 운영홈/재처리적용 원본 직접 열람·복사·12장 manifest 갱신.
- [x] Mock fixture 재처리와 신규 제출 성능 구분,200%/문서Browser NOT_RUN 유지.
- [x] 정적4 PASS 및 REVIEW 동결.
