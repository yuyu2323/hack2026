import { useState } from "react";
import type { AccountMe, Page } from "@storeloop/api-client";
import {
  ActionForm,
  api,
  Badge,
  businessKeys,
  date,
  Empty,
  FilterBar,
  Link,
  listQuery,
  PageTitle,
  Pager,
  Panel,
  prefixFor,
  Resource,
  Status,
  type Data,
  useLocation,
  useResource,
} from "./core";
export function Issues({ account }: { account: AccountMe }) {
  const { path, search } = useLocation();
  const id = path.split("/")[3];
  if (id) return <IssueDetail id={id} account={account} />;
  const value = useResource<Page<Data>>(
    "/issues" +
      listQuery(search, [
        ...businessKeys,
        "page",
        "page_size",
        "status",
        "unresolved",
        "priority",
        "assignee_id",
      ]),
  );
  return (
    <>
      <PageTitle
        title={
          account.role === "store_owner"
            ? "함께 확인할 일"
            : "검토부터 조치까지"
        }
        description="미해결 항목을 확인하고, 담당자와 다음 행동을 이어가세요."
      />
      <FilterBar
        account={account}
        extra={[
          {
            name: "status",
            label: "조치 단계",
            type: "select",
            options: [
              { id: "open", name: "검토 대기" },
              { id: "in_progress", name: "조치 중" },
              { id: "resolved", name: "완료" },
            ],
          },
          {
            name: "priority",
            label: "우선순위",
            type: "select",
            options: [
              { id: "normal", name: "보통" },
              { id: "high", name: "높음" },
            ],
          },
        ]}
      />
      <Resource value={value}>
        {(data: Page<Data>) => (
          <>
            {data.items.length ? (
              <div className="card-grid">
                {data.items.map((issue) => (
                  <IssueCard
                    key={issue.id}
                    issue={issue}
                    prefix={prefixFor(account.role)}
                    search={search}
                  />
                ))}
              </div>
            ) : (
              <Empty />
            )}
            <Pager data={data} />
          </>
        )}
      </Resource>
    </>
  );
}
export function IssueCard({
  issue,
  prefix,
  search = "",
}: {
  issue: Data;
  prefix: string;
  search?: string;
}) {
  return (
    <article className="work-card">
      <div className="card-top">
        <Status value={issue.status} />
        <Status value={issue.priority} />
      </div>
      <p className="eyebrow">
        {issue.store_name} · {issue.category_name}
      </p>
      <h3>
        <Link to={`${prefix}/issues/${issue.id}${search}`}>{issue.title}</Link>
      </h3>
      <p className="muted">담당 {issue.assignee_name || "미배정"}</p>
      {issue.next_check_at && <p>다음 확인 {date(issue.next_check_at)}</p>}
      <Link
        className="card-action"
        to={`${prefix}/issues/${issue.id}${search}`}
      >
        조치 내용 확인 <span>→</span>
      </Link>
    </article>
  );
}
function IssueDetail({ id, account }: { id: string; account: AccountMe }) {
  const value = useResource<Data>("/issues/" + id);
  const assignees = useResource<Page<Data>>(
    account.role !== "store_owner"
      ? `/issues/${id}/assignees?page_size=100`
      : null,
  );
  const prefix = prefixFor(account.role);
  return (
    <>
      <Link className="text-link" to={prefix + "/issues" + location.search}>
        ← 확인할 일 목록
      </Link>
      <Resource value={value}>
        {(issue: Data) => (
          <>
            <PageTitle
              title={issue.title}
              description={`${issue.store_name} · ${issue.category_name} · ${date(issue.created_at)}`}
              action={<Status value={issue.status} />}
            />
            <div className="detail-grid">
              <div>
                <Panel title="확인할 내용">
                  <p className="preserve">{issue.description}</p>
                  <div className="tags">
                    <Status value={issue.priority} />
                    <Badge>담당 {issue.assignee_name || "미배정"}</Badge>
                  </div>
                  <Link
                    className="button secondary"
                    to={`${prefix}/submissions/${issue.submission_id}`}
                  >
                    사진과 평가 근거 확인 →
                  </Link>
                  {issue.resolution && (
                    <div className="notice">
                      <strong>해결 내용</strong>
                      <p>{issue.resolution}</p>
                    </div>
                  )}
                </Panel>
                <Panel title="조치 이력">
                  {issue.actions.length ? (
                    issue.actions.map((a: Data) => (
                      <article className="timeline-entry" key={a.id}>
                        <div className="card-top">
                          <strong>{a.actor_name}</strong>
                          <small>{date(a.created_at)}</small>
                        </div>
                        <p>{a.body}</p>
                        {a.to_status && (
                          <p>
                            {a.from_status && <Status value={a.from_status} />}{" "}
                            → <Status value={a.to_status} />
                          </p>
                        )}
                      </article>
                    ))
                  ) : (
                    <p className="muted">아직 기록된 조치가 없습니다.</p>
                  )}
                </Panel>
              </div>
              {account.role !== "store_owner" && (
                <aside>
                  <Panel title="다음 단계로 이동">
                    <ActionForm

                      title="담당·진행 단계 변경"
                      initial={{
                        status: issue.status,
                        assignee_id: issue.assignee_id || "",
                        priority: issue.priority,
                        resolution: issue.resolution || "",
                        next_check_at: issue.next_check_at?.slice(0, 16) || "",
                      }}
                      fields={[
                        {
                          name: "status",
                          label: "진행 단계",
                          required: true,
                          type: "select",
                          options: [
                            { id: "open", name: "검토 대기" },
                            { id: "in_progress", name: "조치 중" },
                            { id: "resolved", name: "완료" },
                          ],
                        },
                        {
                          name: "assignee_id",
                          label: "담당자",
                          type: "select",
                          options: assignees.data?.items.map((a) => ({
                            id: a.id,
                            name: a.display_name,
                          })),
                        },
                        {
                          name: "priority",
                          label: "우선순위",
                          required: true,
                          type: "select",
                          options: [
                            { id: "normal", name: "보통" },
                            { id: "high", name: "높음" },
                          ],
                        },
                        {
                          name: "resolution",
                          label: "해결 내용 (완료 시 필수)",
                          type: "textarea",
                          maxLength: 2000,
                        },
                        {
                          name: "next_check_at",
                          label: "다음 확인 시각 (한국 시간)",
                          type: "datetime-local",
                        },
                      ]}
                      submit={(v) =>
                        api.patch("/issues/" + id, {
                          ...v,
                          version: issue.version,
                          resolution: v.resolution || null,
                          assignee_id: v.assignee_id || null,
                          next_check_at: v.next_check_at
                            ? new Date(v.next_check_at).toISOString()
                            : null,
                        })
                      }
                      onDone={value.reload}
                    />
                    <ActionForm
                      title="조치 코멘트 추가"
                      fields={[
                        {
                          name: "body",
                          label: "수행한 조치와 다음 행동",
                          required: true,
                          type: "textarea",
                          maxLength: 2000,
                        },
                      ]}
                      submit={(v) => api.post(`/issues/${id}/actions`, v)}
                      onDone={value.reload}
                      button="조치 기록하기"
                    />
                  </Panel>
                </aside>
              )}
            </div>
          </>
        )}
      </Resource>
    </>
  );
}
export function Notifications({ account }: { account: AccountMe }) {
  const { search } = useLocation();
  const value = useResource<Data>(
    account.role === "platform_operator"
      ? null
      : "/notifications" +
          listQuery(search, ["page", "page_size", "unread_only"]),
  );
  const [error, setError] = useState("");
  return (
    <>
      <PageTitle
        title="새 소식을 확인해요"
        description="점검 결과와 조치 변경을 한곳에서 확인하세요."
      />
      {account.role === "platform_operator" ? (
        <Empty>운영자에게는 영업 업무 알림이 제공되지 않습니다.</Empty>
      ) : (
        <>
          <p>
            {value.data ? `읽지 않은 알림 ${value.data.unread_count}건` : ""}
          </p>
          {error && <p role="alert">{error}</p>}
          <Resource value={value}>
            {(data: Data) => (
              <>
                {data.items.length ? (
                  data.items.map((n: Data) => (
                    <article
                      className={"notification " + (n.read_at ? "read" : "")}
                      key={n.id}
                    >
                      <div>
                        <Badge tone={n.read_at ? "neutral" : "good"}>
                          {n.read_at ? "읽음" : "새 알림"}
                        </Badge>
                        <h2>{n.title}</h2>
                        <small>{date(n.created_at)}</small>
                      </div>
                      <button
                        className="secondary"
                        onClick={async () => {
                          try {
                            await api.post(`/notifications/${n.id}/read`);
                            const destination =
                              n.target.type === "submission"
                                ? "submissions"
                                : "issues";
                            const to = `${prefixFor(account.role)}/${destination}/${n.target.id}`;
                            history.pushState({}, "", to);
                            window.dispatchEvent(new PopStateEvent("popstate"));
                          } catch {
                            setError(
                              "현재 접근 권한을 확인한 뒤 다시 시도해 주세요.",
                            );
                            value.reload();
                          }
                        }}
                      >
                        내용 확인 →
                      </button>
                    </article>
                  ))
                ) : (
                  <Empty>아직 도착한 알림이 없습니다.</Empty>
                )}
                <Pager data={data as Page<Data>} />
              </>
            )}
          </Resource>
        </>
      )}
    </>
  );
}
