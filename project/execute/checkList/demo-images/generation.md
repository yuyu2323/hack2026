# generation: 실제 매대 시연 이미지 10개

- 담당: demo-images / product_design
- 상태: REVIEW
- 입력: DATA-001 docs/08-data.md, 00~02, G1 ACCEPTED 등록부, imagegen SKILL.md
- 선행: G1 확정 수신·이미지 담당 배정 완료.
- 소유: scripts/seed/assets/shelves/*, scripts/seed/manifest.json 및 demo-images 작업기록.
- 도구: 내장 image_gen, 편집도 동일 도구만. Python은 파일 해시·크기·차원 메타데이터 계산만 사용.
- 완료 조건: 음료/스낵 각 reference2+before1+같은구도after1+uncertain1, 총10 실제파일; 모두 직접시각검수; manifest의 경로/hash/역할/프롬프트/관찰사실/계보 기록.
- 이력: [generation](../../workHitory/demo-images/generation.md)

- [x] imagegen 스킬 읽기·사용 알림, 문서08 및 소유권 확인
- [x] beverage-reference-01 및 beverage-before-01 우선 생성·검수·공유
- [x] 나머지 Reference2+before/after/uncertain 총10장 생성
- [x] before를 직접 열어 확인하고 동일 이미지 참조 after 편집
- [x] 이미지별 실제 관찰사실 기록, 프롬프트 의도를 정답으로 간주하지 않음
- [x] 프로젝트 경로에 원본 복사, metadata/hash/중복·경로 검증
- [x] manifest 한국어 본문·source_kind·Reference/제출 분리·DB seed code 연결
- [x] root/contract_ai/데이터 담당 인계 및 독립 Golden Case 검수 요청

## 범위·보존

이미지는 기존 자료를 대체하지 않는 신규 합성 자산이다. 외부 브랜드·사람·개인정보·인증값을 넣지 않는다. 이미지 파일의 픽셀 편집·변환은 image_gen만 수행한다. 최종 golden_approved는 독립 검토자 승인 전 부여하지 않는다.
