# DB·코어·계정·운영 구현
- 상태: RUNNING
- G1 ACCEPTED 등록부와 배정표 확인, 05/06 1.0b 확정 수신.
- product_design DR-D01~07 독립 검토 PASS 수신. 문서검증과 실제테스트 구분.
- 원래04 모델/migration 경계와 core interfaces를 준수한다. root main/업무서비스·설치·lock 파일은 수정하지 않는다.
- server/requirements.in 작성. root 설치 이후 TDD 실행.

## 초기 TDD 준비
- core config/db와 빈 모델 registry, 필수도메인 metadata 제약시험·익명 CSRF 세션 API시험 작성.
- 첫 pytest 실행은 pytest 미설치로 NOT_RUN. 환경 오류를 RED로 세지 않음. root 의존성 설치 완료 후 재실행.

## TDD·마이그레이션 진행
- 환경 설치 후 pytest 초기 RED2: 필수 모델 메타데이터가 비어 있음, /auth/csrf=404를 실제 assertion으로 확인.
- 모델27개/동결 Alembic4revision/세션CSRF 구현 후 초기 GREEN2.
- SQLite upgrade 중 자동생성 JSONB Text import 결함 수정, dialect별 now()를 func.now()로 교정. batch순환FK 추가시 named CHECK 보존.
- 모델 정합·활성OFC 부분고유·세션회전/CSRF/비활성/로그아웃 추가 관련검증 SQLite7 PASS.
- PostgreSQL 첫실행은 sandbox TCP거부로 실패. pytest 전체traceback의 연결인자에 로컬DB자격값이 노출되어 root에게 즉시 원문없이 알렸고 root가 PGrole/env값 회전완료 회신. engine hide_parameters, fixture 연결오류 sanitize, 이후 --tb=short 사용. 기록/소스에 원문 없음.
- stores/operations 기능 RED4: 범위목록·운영활성변경·승격차단 API미구현404 확인 후 구현중.
- CONTRACT-DATA-1.0c 표현명확화: AnalysisContextDTO는 schema_version/snapshot_sha256+snapshot 각 필드를 평탄화(context.guidelines/references). root요청수신, DB/요청변경없음.

## G2 자체 검증 결과
- stores/operations RED4(404)를 구현해 GREEN, 이후 관련 경계 확장.
- `server/.venv/bin/python -m pytest server/tests/test_accounts.py server/tests/test_stores.py server/tests/test_operations.py server/tests/test_models.py -m 'not postgres' -q --tb=short`: 17 PASS. 세션 회전/만료/폐기·CSRF/origin, 기존세션 비활성/역할/매핑 반영, 운영자 영업범위 차단, OFC 후보/멱등target, 버전충돌, 무변경/NULL입력, 매핑이력·기준 비활성·공지기간·운영DTO 본문제외 포함.
- 승격된 같은 Python pytest `-m postgres`: 3 PASS. 전용 run schema에서4revision upgrade와metadata차이없음, 두OFC동시claim중1승자, 동일version 운영변경2요청중1승자·감사1건을 실제PostgreSQL로 확인.
- refactor: 공통 Base를 DB접속없는 core/base에 분리, 보안문자열trim/공개DTO helpers, namedcheck와dialect일치, root요청에 따라 require_csrf의 안전메서드 제외. 관련 회귀통과.
- known: FastAPI/Starlette의 httpx 테스트클라이언트 deprecation warning2건. 기능실패 아님, root 의존성소유자에게 알림. 운영retry는 contract_ai.retry_job 구현에연결되어 최종직렬통합이 남음.
- root/AI에게 모델·코어·fixture·라우터 준비와 의존성 전달 완료. 모델/migration을 다른에이전트가 수정하지 않음.

## 모델 경계 결함 수정
- 실제 Issue(version=0) 삽입이성공하는 RED를재현. DB계약>=1 제약누락 확인.
- root가production미적용을확인하여 초기0004와Issue모델에 named ck_issue_version CHECK 추가(기존revision 적용후재작성 아님). 05 명시명보완, 관련upgrade·metadata·실제삽입거절 재검증.
- 06 assignee후보 List page/page_size 문구를root구현과명시정합화.

## 최종 자체 경계 검사 (재처리 연결 전)
- SQLite/HTTP22 PASS: 익명CSRF·세션회전/만료/폐기·현재권한, mutation/감사/연결/후보/공지/status health경계, secret입력 검증오류의 비노출.
- PostgreSQL3 PASS 재검증: 모델27개/4revision차이없음·ck_issue_version 실존, 두OFC 경쟁/계정version경쟁에서1개만commit.
- production 초기마이그레이션 적용가능하다고root에전달. 실제production적용은root담당.
- 미완료는contract_ai 소유retry_job 준비후 운영HTTP통합과독립검토. 계정·기준·현재권한·순환FK·모델스키마 자체검증은완료.
- 이후 같은검사를새변경없이무의미하게반복하지 않고 통합/독립검토를진행한다.

## 최종 인계
- contract_ai의 retry_job 준비수신직후 운영HTTP통합1 PASS: 실패job→202 queued, 동일key의같은시도replay, 기존expired시도불변, 운영응답본문비노출.
- 자체검증 총 SQLite/HTTP23건과 실제PostgreSQL3건 PASS(서로분리명령으로확인). parent가전체백엔드통합·productionupgrade를수행하므로본인슬롯반환.
- 남은독립코드검토/전체API·seed·실제AI·브라우저는프로젝트후속작업이며 본모듈자체검증을프로젝트완료로표현하지않음.
