# DB/API 독립 검토 — IDR-DATA-001

- 검토자: product_design. docs05/06의 작성자가 아니며 수정 소유권 없음.
- 입력: 00→01→02, 요구03·화면04, CONTRACT-DATA-1.0 및 최종 보완1.0b (2026-09-21), AI-001 결과/상태 협의.
- 체크리스트: [independent-data-review](../../checkList/product-design/independent-data-review.md).
- 현재 결과: **REVIEW_COMPLETE / PASS**, 본 검토 범위 미해소 개발 차단 없음. 아래 PASS는 문서 정합 검토이며 실행/통합 테스트 PASS가 아니다.

## 검토 기준과 결과

| ID | 심각도·대상 | 발견 내용·영향 | 수정 요청 | 재검토 결과 |
|---|---|---|---|---|
| DR-D01 | 개발 차단 / 06 §4·7 | 기준·운영계정 단건 GET이 없어 직접 상세 URL/새로고침에서 ID로 안정 조회 불가 | GET guidelines/{id}, references/{id}, operations/accounts/{id} 추가 | 1.0a §4/7에서 해당 GET과 scope 확인. **해소** |
| DR-D02 | 개발 차단 / 06 §6 | 이슈 assignee_id 쓰기는 있으나 허용 사용자 후보를 영업 화면이 얻는 API 없음 | 최소 ID/이름/role의 현재 범위 후보 계약 | 1.0a GET issues/{id}/assignees와 비활성·운영자·타범위 제외 확인. **해소** |
| DR-D03 | 개발 차단 / 06 §5·6·8 | 관제 region/date/is_active 필터와 제출/이슈 목록 필터가 달라 KPI 근거를 같은 모집단으로 열 수 없음 | 공통 필터 및 기본값을 drilldown에 포함, 이슈 날짜 기준 명시 | 1.0a에 region/date/is_active, dashboard true·history 모두, Issue 날짜 Submission.created_at 추가. 1.0b 미해결 KPI=open+in_progress에 unresolved=true 추가 및 status 동시지정422 확인. **해소** |
| DR-D04 | 데이터 누락 / 06 §8·6 | needs_attention 혼재 상태에서 최신 작업 state가 DTO에 없고 이슈 행에서 매장/카테고리 이름 없음 | latest_job 및 IssueSummary 대상 이름 추가 | 1.0a에 latest_job:Job/null와 store/category id/name 확인. **해소** |
| DR-D05 | 개발 차단 / 05 §6·06 §1 | 멱등 scope/hash에 대상 URL ID 포함 규칙이 불명확. 같은 key·reason으로 다른 job/매장에 보내면 다른 객체 응답 replay 위험 | canonical operation과 target ID를 key scope 또는 request_hash에 포함하도록 명시 | 1.0b 고정 operation과 method/실제targetID/본문/순서별 이미지 hash, 다른대상 재사용409를 두 문서에서 확인. **해소** |
| DR-D06 | 개발 차단 / 05 §4·06 §4 | Reference.version은 불변 revision 번호인데 status PATCH는 같은 version으로 반복 상태 변경 가능. 이전 revision 재활성/교체시 stale 동작과 lineage 잠금 기준 불명확 | current lineage 기준 비교·원자 잠금·stale409 규칙 또는 별도 mutable lock version 명시 | 1.0b state_version DB/DTO/요청 추가, 최신lineage 잠금과 id/state_version 비교, 상태증가/새revision/구버전409 확인. 04에도 반영. **해소** |
| DR-D07 | 누락 / 06 요청 전반 | 필드 제한/기본값/nullable·unknown 필드·빈 PATCH·password 길이 정책이 DTO 수준에서 미완성 | DB 문자열 길이 상속 및 요청 공통 검증 정책, password/login과 빈PATCH 명시 | 1.0b extra forbid·05 제한상속·명시null·기본값·login/password 한도·빈PATCH422/noop 정책 확인. **해소** |

## 정합 확인한 경계

- 세션: 익명 CSRF→로그인 rotate→HttpOnly opaque session→현재 DB role/mapping 검사→logout revoke. CSRF/Origin 명시, 기존 세션 비활성/범위 축소 반영.
- scope: 점주 연결 매장/자기 후속, OFC 담당, 지역 소속, HQ 전사. 운영자에게 영업 DTO·원본/썸네일 금지; metadata 재처리만.
- 스냅샷: 4단계 기준 version, Reference lineage, 제출 이미지 위치·hash, 부모 연결. 과거 평가·시도 삭제/덮어쓰기 없음.
- AI: pass/fail/unknown, 기준/사진/Reference ID 검증, rate 0..100 소수1자리와 null, 실제/Mock·생성 이미지 source_kind 구분.
- queue: Job와 Attempt 분리, 종료 실패만 재처리, 예약 queued attempt·DB 잠금·CAS·늦은 결과 거절, PostgreSQL 동시성 인수.
- 운영: 업무 변경/감사 원자성, 이전 mapping ended_at, master 비활성, 안전한 DTO·감사 fields.
- 목록: page/page_size/total·안정 sort·범위 밖 total 차단. dashboard는 집계 응답이며 리스트형 resources와 구별.
- 이슈·알림: Escalation 통합, 자체 scope·현재 assignee, 수신자/읽음·현재 target 권한, 외부 전송 제외.
- 분석: 제출 없는 매장은 위반 아님, Mock 명시, n<3/분산0/null 처리·유효 주차쌍, 기본 기간 리포트만.
- 적용 요구: 03 AT-02~20에 필요한 도메인이 존재하며 AT-01/21~24는 실행/시드/프론트/인계 계약에서 검증한다.

## 화면 명세 자체 수정 사항

독립 검토 중 발견한 화면04의 추정 필드(data_origin/public_message/accepted/observed_pairs 등)는 PD-002로 실제06 DTO에 맞게 수정했다. API 작성자 파일을 직접 바꾸지 않았다. 04 §7에 실제 메서드/endpoint 대응표와 수정된 scope/filter 원칙을 반영했다.

## 최종 재검토·다음 행동

CONTRACT-DATA-1.0b의 실제 저장본을 다시 읽고 DR-D01~07 전부 해소 확인했다. 특히 state_version은 불변 분석 입력의 version과 분리되어 과거 평가를 보존하며, 미해결 drilldown은 서버 단일 목록으로 재현 가능하다. API 명세의 응답/입력/범위/버전·목록/이슈·알림을 공통04에 반영하고 최종 링크 검사 누락0을 확인했다.

root는 본 PASS와 다른 독립 검토를 합쳐 G1 확정을 판정한다. 현재 실제 소스·DB·API 테스트를 실행하지 않았으며 코드 구현은 하지 않았다. 00~02 및 사용자의 기존 자료·Git 상태를 변경하지 않았다.
