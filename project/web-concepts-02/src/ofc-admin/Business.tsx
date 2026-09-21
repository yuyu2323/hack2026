import { useRef, useState } from "react";
import {
  idempotencyKey,
  type AccountMe,
  type Page,
} from "@storeloop/api-client";
import {
  ActionForm,
  api,
  Badge,
  businessQuery,
  date,
  Empty,
  FilterBar,
  Lane,
  Link,
  listQuery,
  PageTitle,
  Pager,
  Panel,
  queryString,
  rate,
  Resource,
  Status,
  type Data,
  useLocation,
  useResource,
  useRequestKey,
} from "../shared/core";
import { IssueCard } from "../shared/issues";
import {
  Comparison,
  SubmissionDetail,
  SubmissionList,
} from "../store-owner/Owner";
import { Guidelines, References } from "./Standards";
import { Analytics } from "./Analytics";
export function Business({ account }: { account: AccountMe }) {
  const { path } = useLocation();
  const match = path.match(/^\/ofc-admin\/submissions\/([^/]+)(\/compare)?$/);
  if (match)
    return match[2] ? (
      <Comparison id={match[1]} prefix="/ofc-admin" />
    ) : (
      <SubmissionDetail id={match[1]} account={account} />
    );
  if (path.includes("/guidelines")) return <Guidelines account={account} />;
  if (path.endsWith("/references")) return <References account={account} />;
  if (path.includes("/stores")) return <Stores account={account} />;
  if (path.endsWith("/submissions"))
    return <SubmissionList account={account} />;
  if (path.endsWith("/analytics")) return <Analytics account={account} />;
  return <BusinessHome account={account} />;
}
function BusinessHome({ account }: { account: AccountMe }) {
  const { search } = useLocation();
  const query = businessQuery(search);
  const board = useResource<Data>("/dashboard" + query);
  const issues = useResource<Page<Data>>(
    "/issues" + query + (query ? "&" : "?") + "page_size=100&unresolved=true",
  );
  return (
    <>
      <PageTitle
        title="오늘, 이 일부터 시작해요"
        description={
          (account.role === "hq"
            ? "전체 매장"
            : account.role === "regional"
              ? "우리 지역"
              : "담당 매장") + "의 확인할 일과 후속 조치를 순서대로 살펴보세요."
        }
        action={
          <Link
            className="button secondary"
            to={"/ofc-admin/analytics" + query}
          >
            추이와 분석 ↗
          </Link>
        }
      />
      <FilterBar account={account} />
      <Resource value={board}>
        {(data: Data) => (
          <>
            <div className="board-note">
              <span className="sun-symbol" aria-hidden="true">
                ☼
              </span>
              <div>
                <strong>
                  {data.kpis.store_count}개 매장에서{" "}
                  {data.kpis.open_issue_count}건의 확인할 일이 있어요.
                </strong>
                <p>
                  미제출과 판단 불가를 구분하고, 사진 근거에서 다음 행동을 정해
                  주세요.
                </p>
              </div>
            </div>
            <div className="lanes">
              <Lane
                step="01"
                title="먼저 검토해요"
                caption="기준과 사진을 확인할 차례"
              >
                {data.stores
                  .filter((s: Data) =>
                    [
                      "needs_attention",
                      "unassessable",
                      "technical_failure",
                      "not_submitted",
                    ].includes(s.status),
                  )
                  .map((s: Data) => (
                    <StoreTask key={s.store_id} store={s} />
                  ))}
                {!data.stores.some((s: Data) =>
                  [
                    "needs_attention",
                    "unassessable",
                    "technical_failure",
                    "not_submitted",
                  ].includes(s.status),
                ) && <p className="lane-empty">새 검토 작업이 없습니다.</p>}
              </Lane>
              <Lane
                step="02"
                title="함께 조치해요"
                caption="담당자와 해결 방법을 연결해요"
              >
                {issues.data?.items
                  .filter((i) => i.status !== "resolved")
                  .map((issue) => (
                    <IssueCard
                      key={issue.id}
                      issue={issue}
                      prefix="/ofc-admin"
                      search={query}
                    />
                  ))}
                {issues.data && !issues.data.items.length && (
                  <p className="lane-empty">미해결 조치가 없습니다.</p>
                )}
              </Lane>
              <Lane
                step="03"
                title="변화를 확인해요"
                caption="개선 이후 결과를 돌아보세요"
              >
                {data.stores
                  .filter((s: Data) =>
                    ["evaluated", "processing"].includes(s.status),
                  )
                  .map((s: Data) => (
                    <StoreTask key={s.store_id} store={s} />
                  ))}
                {!data.stores.some((s: Data) =>
                  ["evaluated", "processing"].includes(s.status),
                ) && (
                  <p className="lane-empty">
                    후속 결과가 도착하면 여기에서 확인해요.
                  </p>
                )}
              </Lane>
            </div>
            <div className="summary-line">
              <Link
                to={"/ofc-admin/submissions" + queryString({ ...data.filters })}
              >
                제출 {data.kpis.submission_count}건 →
              </Link>
              <Link
                to={
                  "/ofc-admin/submissions" +
                  queryString({ ...data.filters, status: "failed" })
                }
              >
                기술 실패 {data.kpis.failed_count}건 →
              </Link>
              <Link
                to={
                  "/ofc-admin/issues" +
                  queryString({ ...data.filters, unresolved: true })
                }
              >
                미해결 {data.kpis.open_issue_count}건 →
              </Link>
              <span>
                준수율 {rate(data.kpis.compliance_rate)} · 판단 가능률{" "}
                {rate(data.kpis.assessable_rate)}
              </span>
              <span>
                평가 표본 {data.sample_count}건 / Mock {data.mock_review_count}
                건
              </span>
            </div>
          </>
        )}
      </Resource>
    </>
  );
}
function StoreTask({ store }: { store: Data }) {
  return (
    <article className="work-card">
      <div className="card-top">
        <Status value={store.status} />
        {store.open_issue_count > 0 && (
          <Badge tone="warn">미해결 {store.open_issue_count}</Badge>
        )}
      </div>
      <h3>{store.store_name}</h3>
      <p>
        {store.status === "not_submitted"
          ? "선택한 기간에 제출한 사진이 없습니다."
          : store.status === "technical_failure"
            ? "사진 분석을 완료하지 못했습니다."
            : store.status === "unassessable"
              ? "사진과 적용 기준을 함께 확인해 주세요."
              : "사진 근거와 후속 조치를 확인해 주세요."}
      </p>
      <div className="card-metrics">
        <span>
          준수율 <strong>{rate(store.compliance_rate)}</strong>
        </span>
        <span>
          평가 <strong>{store.review_count}건</strong>
        </span>
      </div>
      <Link
        className="card-action"
        to={
          store.latest_submission_id
            ? "/ofc-admin/submissions/" +
              store.latest_submission_id +
              queryString(store.drilldown)
            : "/ofc-admin/stores/" +
              store.store_id +
              queryString(store.drilldown)
        }
      >
        {store.latest_submission_id ? "사진 근거 확인" : "매장 확인"}{" "}
        <span>→</span>
      </Link>
    </article>
  );
}
function Stores({ account }: { account: AccountMe }) {
  const { path, search } = useLocation();
  const id = path.split("/")[3];
  const value = useResource<Data>(
    id
      ? "/stores/" + id
      : "/stores" +
          listQuery(search, [
            "page",
            "page_size",
            "q",
            "region_id",
            "is_active",
          ]),
  );
  const candidates = useResource<Page<Data>>(
    account.role === "ofc" && !id ? "/stores/candidates?page_size=100" : null,
  );
  const key = useRequestKey();
  return (
    <>
      <PageTitle
        title={id ? "매장에서 이어지는 업무" : "함께 관리하는 매장"}
        description="현재 담당 범위와 연결 상태를 확인하세요."
      />
      {!id && (
        <FilterBar
          account={account}
          extra={[{ name: "q", label: "매장 이름·코드 검색" }]}
        />
      )}
      <Resource value={value}>
        {(data: Data) =>
          id ? (
            <Panel title={data.name}>
              <div className="tags">
                <Badge>{data.region_name}</Badge>
                <Badge>{data.is_active ? "활성 매장" : "비활성 매장"}</Badge>
              </div>
              <p>{data.address || "주소 정보 없음"}</p>
              <p>
                유형 {data.store_type} · OFC{" "}
                {data.ofc?.display_name ?? "미배정"} · 연결 점주{" "}
                {data.owner_count}명
              </p>
              <div className="actions">
                <Link
                  className="button"
                  to={"/ofc-admin/submissions" + queryString({ store_id: id })}
                >
                  점검 이력
                </Link>
                <Link
                  className="button secondary"
                  to={"/ofc-admin/issues" + queryString({ store_id: id })}
                >
                  조치 이력
                </Link>
                <Link
                  className="button secondary"
                  to={"/ofc-admin/guidelines" + queryString({ store_id: id })}
                >
                  적용 범위 기준
                </Link>
              </div>
            </Panel>
          ) : (
            <>
              {data.items.length ? (
                <div className="card-grid">
                  {data.items.map((s: Data) => (
                    <article className="work-card" key={s.id}>
                      <Badge>{s.region_name}</Badge>
                      <h2>
                        <Link to={"/ofc-admin/stores/" + s.id + search}>
                          {s.name}
                        </Link>
                      </h2>
                      <p>
                        {s.store_type} · {s.is_active ? "활성" : "비활성"}
                      </p>
                      <p>
                        OFC {s.ofc?.display_name ?? "미배정"} · 점주{" "}
                        {s.owner_count}명
                      </p>
                      <Link
                        className="card-action"
                        to={"/ofc-admin/stores/" + s.id + search}
                      >
                        매장 업무 확인 →
                      </Link>
                    </article>
                  ))}
                </div>
              ) : (
                <Empty />
              )}
              <Pager data={data as Page<Data>} />
            </>
          )
        }
      </Resource>
      {account.role === "ofc" && !id && (
        <Panel title="새로 담당할 수 있는 매장">
          <p>
            같은 지역의 미배정 매장만 표시됩니다. 담당 등록 후 사진과 업무
            이력을 볼 수 있어요.
          </p>
          <Resource value={candidates}>
            {(data: Page<Data>) =>
              data.items.length ? (
                <div className="card-grid">
                  {data.items.map((s) => (
                    <article className="work-card" key={s.id}>
                      <h3>{s.name}</h3>
                      <p>
                        {s.region_name} · {s.store_type}
                      </p>
                      <ActionForm
                        title="내 관리 매장 등록"
                        button="담당 등록하기"
                        fields={[
                          {
                            name: "reason",
                            label: "담당 등록 사유",
                            required: true,
                            maxLength: 500,
                          },
                        ]}
                        submit={(v) =>
                          api.post(`/stores/${s.id}/claim`, v, key.get(s.id,v))
                        }
                        onDone={() => {
                          key.clear();
                          value.reload();
                          candidates.reload();
                        }}
                      />
                    </article>
                  ))}
                </div>
              ) : (
                <p>등록 가능한 미배정 매장이 없습니다.</p>
              )
            }
          </Resource>
        </Panel>
      )}
    </>
  );
}
