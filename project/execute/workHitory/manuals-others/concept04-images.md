# MAN-IMG04 실제 화면 반영

상태: REVIEW · 문서 동결 · 담당 product_design

## 범위
`deliverables/manuals/concept-04/index.html`과 로컬 assets, 본인 문서 생성/검증/추적 파일만 수정했다. 다른 매뉴얼 본문·제품 소스·root 원본 증거·DB·브라우저·공유 서버·패키지는 변경하지 않았다.

## 원본 선별과 직접 검수
정상 원본 11장을 직접 열람한 뒤 10장을 선택했다. 점주 홈390, 사진 선택360 수정본, 지연 안내390, 첫 실제 결과390, 개선 후 결과360, 전후 날짜·사진1440, 기준 버전 변화1440, OFC 조건 조회1440, 지역 관리자 상세 근거1440 수정본, 운영 재처리 완료1440을 사용했다. 본사 첫 화면 후보는 OFC 조건 적용으로 교체해 역할별 작업을 더 직접 설명했다.

삭제 버튼 돌출이 있는 resubmit-preview/upload-preview, 사진이 질문을 가리는 ofc-evidence, 축소된 unmapped-empty는 정상 예시로 사용하지 않았다. D04-V01/V02 최신 수정본은 작성자가 직접 열람하고 contract_ai의 시각 PASS 인계를 확인했다. `ofc-evidence-fixed`의 실제 계정은 지역 관리자라 캡션도 그 역할로 표시했다.

360 미리보기 캡션은 사진·파일명·순서/삭제 제어에 한정하고 화면 아래 다음 버튼이 모두 보인다고 하지 않았다. 전후 비교 사진은 상단 구간이라 전체 사진/하단은 스크롤 안내로 구분했다. 운영 retry-success는 작업 완료와 첫 실패 보존까지만 화면 근거로 설명하고, 화면 밖 둘째 시도 반영 정보는 아래에서 확인하도록 안내했다. 사진 원본은 변형 없이 복사했다.

## 내용
- 실제 봄빛역점·스낵 시연: 첫 before1장 및 child after1장, 각각5기준/3Reference. 4단계 제출과 미리보기·지연·결과·비교에 연결했다.
- 준수0→100% 및 판단 가능률100%를 함께 표시했다. qa04_labels v1→v2는 직접 비교 불가이며 나머지 동일버전 개선과 구분했다. 합성 사진의 모델 판정을 정확도의 정답으로 간주하지 않는다.
- 모델70.973/64.762초, 접수→DB72.692/65.635초. 브라우저 첫관찰74.827/74.371초는 직전 대기74.721/66.229초와의 관찰창0.106/8.142초를 함께 표시했다. 정확한 paint 시간과 다르며 둘 다30초 목표 미달이라고 명시했다.
- 모델은 이전 고정 평가 기록을 사용하며 이전 사진을 다시 입력받는 비교는 아니라는 한계를 설명했다. 실제 AI와 Mock 장애/가상 매출·이미지 출처 구분, Reference 권한과 비밀 비노출 설명은 유지했다.
- 실제 기능/디자인 일부 검증과 전체 최종 인수·문서 렌더/오프라인 확인을 분리했다.

## 재현과 정적 결과
`python3 execute/workHitory/manuals-others/generate_drafts.py 04` → `server/.venv/bin/python execute/workHitory/manuals-others/add_concept04_images.py`로 다시 만든다. 다른 시안 번호를 인자로 주지 않으며 이미지 추가 스크립트는 base04 초안에서만 실행한다.

`server/.venv/bin/python execute/workHitory/manuals-others/validate_drafts.py`: 4개 정적 PASS. 04는 이미지10개, 앵커22개, 로컬 링크35개, 외부 리소스0개. 원본/복사본 SHA와 byte 일치, 실제 decoded 해상도·형식과 HTML width/height·alt 대응, 파일/앵커 존재 및 비밀 값 비포함을 검증했다. 01/03/05 본문 해시는 이전 값과 동일하다.

04 HTML 47272bytes, SHA-256 `436dbbe7c2da87e259cc843157bacc32af84c50bb9c80516cc6d008cc9d716e6`. 각 원본·복사본·해상도·실제 포맷·alt·캡션은 `concept04-image-manifest.json`, 전체 검사 증거는 `static-validation.json`에 기록했다.

## 인계
root의 실제 HTML 브라우저/모바일·오프라인 렌더 및 contract_ai 독립 내용·이미지 대조 대기다. 문서와 제품의 전체 PASS를 선언하지 않았다. 04 제품 CSS는 앞선 D04-V01/V02 동결 상태이며 이 작업에서 추가 편집하지 않았다.
