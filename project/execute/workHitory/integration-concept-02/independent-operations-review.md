# QA02 현재 기준·운영 이력 독립 검증

판정: **PASS — 최초 25항목 중 24 PASS, 분류 이름 비교의 검증기 가정 1건을 별도 읽기 재확인하여 해소**. 2026-09-21 21:59:32 KST의 현재 기준을 PostgreSQL READ ONLY·REPEATABLE READ 트랜잭션으로 조회했다. [원시 근거](independent-operations-metadata-20260921T125932Z.json)의 초기 FAIL은 삭제하지 않는다. 해당 검사는 요청에 없던 공백 위치를 제가 임의로 고정한 것이며, [분류 보완 확인](independent-operations-category-correction.json)에서 공백을 제외한 요청 이름·v2·비활성이 일치했다. 제품 데이터는 수정하지 않았다.

## 현재 4단계 우선순위

봄빛역점·음료에 쓰기 없는 `make_snapshot`을 실행한 **메모리 내 현재 시점 결과**이다. 이 snapshot을 저장하거나 AI에 보내지 않았다.

| 단계 | guideline ID | 버전 | 적용 |
| --- | --- | --- | --- |
| HQ | `2d4ea8b1-116c-430e-8e06-e80ba477484b` | 1 | 후보 보존, 미선택 |
| REGION | `2089bf7c-3836-441c-9d00-7a32eb6a0436` | 1 | 후보 보존, 미선택 |
| STORE | `d422d014-58d6-4d90-ae76-d4502709dad7` | 1 | 후보 보존, 미선택 |
| CATEGORY | `871e8d30-b380-4050-b81a-1594f4c1eac1` | 2 | 단일 승자 |

같은 `qa02_labels`의 후보는 정확히 4개이며 CATEGORY v2만 선택됐다. 선택된 version ID는 `bf0785aa-b531-4cc1-9ef4-516cf972bda7`이다. 다른 후보의 미선택 사유도 보존된다. 조회 이후 root가 기준을 비활성화할 수 있으므로 이 표는 관측 시점의 상태이며 영구 현재 상태를 주장하지 않는다.

## 과거 실제 AI 3건과 등록 시점

기존 독립 근거 `independent-ai-metadata-20260921T124410Z.json`의 hash와 현재 DB 본문을 비교했다. 아래 **3건 모두 snapshot/result SHA가 그대로**이며, 새 상위 3기준은 과거 후보에 들어 있지 않다.

| 제출 | 실제 결과 저장 시각(KST) | 당시 qa02_labels |
| --- | --- | --- |
| `8259ce47-90ce-4a85-8496-8ed27edeb375` | 18:29:47 | 없음 |
| `bca082c1-56fe-4bd4-9c0f-9b7ce1ed0ee9` | 18:31:47 | 없음 |
| `e9fd4f27-0d3e-42a1-9e58-9c255f49d703` | 19:07:25 | CATEGORY v2만 존재·선택 |

새 HQ/REGION/STORE 생성 시각은 각각 **21:57:10 / 21:57:25 / 21:57:35 KST**다. 따라서 이번 검증은 실제 AI 3건 이후 등록한 기준의 현재 우선순위 검증이다. **과거 AI 분석 전에 4단계가 모두 등록됐거나 그 분석이 4후보를 사용했다고 주장하지 않는다.** 현재 기준 변경이 저장된 과거 snapshot·결과를 덮어쓰지 않은 사실은 직접 hash 비교로 확인했다.

## 계정·분류

- 계정 `22b4defd-15bf-478c-a23e-613fcf4134eb`는 최종 **v7, 활성 store_owner, region null, 활성 owner/OFC 연결 각 0개**다.
- 이전 봄빛역점 owner 연결 `fe69086f-fc57-4b58-9044-3bede668eac7`은 종료돼 있고 감사에 종료 ID가 남아 있다.
- 북부 OFC v6에서 푸른언덕점을 claim한 연결 `731e73ed-dcec-47fb-9c06-c4e384826fb5`는 생성 21:56:11→종료 21:56:22 KST다. v7 복원 감사의 before는 OFC/북부/해당 매장, after는 점주/region null/빈 매장 목록과 해당 종료 ID다. claim 감사·현재 연결 행이 일치한다.
- `qa02_test_category` (`4f49fc31-ad68-4f63-8bec-0dc9cac0c69d`)는 v1 활성 생성 후 v2 이름 변경·비활성이다. 요청의 `QA02검증완료분류`와 이름이 공백 제외 기준으로 일치한다. 생성/수정 감사와 현재 상태가 맞는다.

## 범위

새로운 실제 AI 호출·HTTP 요청·Browser 조작·서비스 변경·업무 DB 쓰기는 없다. 세션에 추가·변경·삭제된 ORM 객체가 없음을 확인했다. 사유·기준·질문·평가 본문과 비밀은 출력하지 않았다. root `actual-ai.json` 및 다른 담당의 `independent-*`는 수정하지 않았다.

실제 UI 조작 PASS와 이번 DB 메타데이터 PASS는 구분한다. 제품의 계정/운영 서비스 일부는 과거 본인이 구현했으므로 이 기록은 그 소스에 대한 독립 보안 리뷰를 대체하지 않으며 root 수행 UI 사건의 저장 결과 확인이다.

## 후속 정리 확인 — 14 PASS

root가 공지·상위 기준 정리 완료를 전달한 뒤 별도 READ ONLY로 [후속 정리 근거](independent-operations-cleanup-metadata.json)를 기록했다.

- HQ/REGION/STORE 상위 3개는 모두 비활성이고, 본문 버전은 1 및 GuidelineVersion 1개로 그대로다. 각 감사는 active true→false와 동일 본문 버전 1을 기록한다.
- CATEGORY `871e8d30-b380-4050-b81a-1594f4c1eac1`는 활성·본문 v2로 유지된다.
- 공지 `8364b4a5-9704-4fa1-b5e7-300fad961aed`는 요청 제목과 일치하고 최종 v2·비활성이다. 게시 시작은 21:57:00 KST, 실제 등록은 21:58:07 KST다. 활성 v1 생성 감사→21:58:48의 비활성 v2 감사가 현재 상태와 맞는다. 게시 시작을 실제 등록 시각과 혼동하지 않는다.
- 과거 실제 AI 3건은 정리 이후에도 기존 snapshot/result hash가 그대로다.

root가 관측한 공지의 점주 화면 노출→비활성 후 사라짐과 종료 공지 미노출은 별도 UI 근거다. 본인은 저장 상태·기간·감사만 검증했으며 Browser에서 이를 재실행하지 않았다.
