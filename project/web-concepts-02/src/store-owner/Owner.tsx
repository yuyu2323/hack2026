import { rolePhotoUrl, publicDemoAccess } from "../shared/demo-role";
import { useEffect, useRef, useState } from "react";
import {
  idempotencyKey,
  type AccountMe,
  type Page,
} from "@storeloop/api-client";
import {
  ActionForm,
  api,
  Badge,
  businessKeys,
  date,
  Empty,
  ErrorBox,
  Fields,
  FilterBar,
  go,
  Lane,
  Link,
  listQuery,
  PageTitle,
  Pager,
  Panel,
  queryPatch,
  queryString,
  rate,
  Resource,
  Source,
  Status,
  type Data,
  useLocation,
  useMutation,
  useResource,
  useRequestKey,
} from "../shared/core";
import { PhotoPicker, Photos } from "../shared/photos";
import { JobStatus } from "../shared/JobStatus";
export function Owner({ account }: { account: AccountMe }) {
  const { path } = useLocation();
  const match = path.match(/^\/store-owner\/submissions\/([^/]+)(\/compare)?$/);
  if (match)
    return match[2] ? (
      <Comparison id={match[1]} prefix="/store-owner" />
    ) : (
      <SubmissionDetail id={match[1]} account={account} />
    );
  if (path.endsWith("/submit")) return <Submit account={account} />;
  if (path.endsWith("/history")) return <SubmissionList account={account} />;
  return <OwnerHome account={account} />;
}
function OwnerHome({ account }: { account: AccountMe }) {
  const { search, query } = useLocation();
  const stores = useResource<Page<Data>>("/stores?page_size=100");
  const submissions = useResource<Page<Data>>(
    "/submissions" + listQuery(search),
  );
  const selected = query.get("store_id") || "";
  return (
    <>
      <PageTitle
        title={`${account.display_name}님, 오늘도 한 걸음`}
        description="사진 한 장의 점검이 더 좋은 매대로 이어져요."
      />
      <section className="next-action">
        <div>
          <Badge tone="light">다음 행동</Badge>
          <h2>
            오늘의 매대를
            <br />
            함께 살펴볼까요?
          </h2>
          <p>
            사진과 궁금한 점을 보내면 적용 기준을 바탕으로
            <br className="desktop-only" /> 무엇을 유지하고 개선할지 알려
            드려요.
          </p>
          <Link
            className="button cream"
            to={"/store-owner/submit" + queryString({ store_id: selected })}
          >
            사진으로 점검하기 <span>↗</span>
          </Link>
        </div>
        <div className="action-illustration" aria-hidden="true">
          <div className="mini-card">
            <span>01</span>
            <strong>사진 찍고</strong>
            <div className="mini-shelf">
              ▰ ▰ ▰<br />▰ ▰ ▰<br />▰ ▰ ▰
            </div>
          </div>
          <div className="mini-card">
            <span>02</span>
            <strong>한 가지씩 개선</strong>
            <p>
              ✓ 기준 확인
              <br />✓ 개선 행동
              <br />✓ 다시 점검
            </p>
          </div>
        </div>
      </section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">MY WORKFLOW</p>
          <h2>내 매장의 진행 상황</h2>
        </div>
        <label>
          확인할 매장
          <select
            value={selected}
            onChange={(e) => queryPatch({ store_id: e.target.value, page: 1 })}
          >
            <option value="">연결된 전체 매장</option>
            {stores.data?.items.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {stores.data?.total === 0 && (
        <Empty>
          연결된 매장이 없습니다. 플랫폼 운영자에게 매장 연결을 요청해 주세요.
        </Empty>
      )}
      <Resource value={submissions}>
        {(data: Page<Data>) => (
          <div className="lanes">
            {[
              {
                step: "01",
                title: "분석을 기다려요",
                caption: "사진을 안전하게 확인하고 있어요",
                filter: (x: Data) =>
                  ["queued", "running"].includes(x.job.status),
              },
              {
                step: "02",
                title: "확인하고 개선해요",
                caption: "피드백에서 다음 행동을 찾아보세요",
                filter: (x: Data) =>
                  x.job.status === "failed" ||
                  x.review_summary?.needs_ofc_review ||
                  x.open_issue_count > 0,
              },
              {
                step: "03",
                title: "점검을 마쳤어요",
                caption: "지난 결과를 돌아보세요",
                filter: (x: Data) =>
                  x.job.status === "succeeded" &&
                  !x.review_summary?.needs_ofc_review &&
                  !x.open_issue_count,
              },
            ].map((l) => (
              <Lane key={l.step} {...l}>
                {data.items
                  .filter(l.filter)
                  .slice(0, 5)
                  .map((item) => (
                    <SubmissionCard
                      key={item.id}
                      item={item}
                      prefix="/store-owner"
                    />
                  ))}
                {!data.items.some(l.filter) && (
                  <p className="lane-empty">아직 해당 작업이 없어요.</p>
                )}
              </Lane>
            ))}
          </div>
        )}
      </Resource>
      <Link className="text-link" to={"/store-owner/history" + search}>
        모든 점검 이력 확인 →
      </Link>
    </>
  );
}
export function SubmissionCard({
  item,
  prefix,
  search = "",
}: {
  item: Data;
  prefix: string;
  search?: string;
}) {
  return (
    <article className="work-card">
      <div className="card-top">
        <Status value={item.job.status} />
        <small>{date(item.created_at)}</small>
      </div>
      <h3>
        <Link to={`${prefix}/submissions/${item.id}${search}`}>
          {item.store_name} · {item.category_name}
        </Link>
      </h3>
      {item.thumbnail && (
        <img
          className="card-thumb"
          src={rolePhotoUrl(item.thumbnail.thumbnail_url ?? item.thumbnail.url)}
          alt={`${item.category_name} 제출 사진`}
        />
      )}
      <div className="card-metrics">
        <span>
          준수율 <strong>{rate(item.review_summary?.compliance_rate)}</strong>
        </span>
        <span>
          판단 가능{" "}
          <strong>{rate(item.review_summary?.assessable_rate)}</strong>
        </span>
      </div>
      <div className="tags">
        <Source value={item.source_kind} />
        <Source value={item.review_summary?.source_kind} />
        {item.parent_submission_id && <Badge>개선 후 재제출</Badge>}
        {item.open_issue_count > 0 && (
          <Badge tone="warn">미해결 {item.open_issue_count}건</Badge>
        )}
      </div>
      <Link
        className="card-action"
        to={`${prefix}/submissions/${item.id}${search}`}
      >
        {item.job.status === "succeeded" ? "피드백 확인하기" : "처리 상태 확인"}{" "}
        <span>→</span>
      </Link>
    </article>
  );
}
export function SubmissionList({ account }: { account: AccountMe }) {
  const { search } = useLocation();
  const prefix = account.role === "store_owner" ? "/store-owner" : "/ofc-admin";
  const value = useResource<Page<Data>>(
    "/submissions" +
      listQuery(search, [
        ...businessKeys,
        "page",
        "page_size",
        "status",
        "needs_ofc_review",
      ]),
  );
  return (
    <>
      <PageTitle
        title="점검 이력"
        description="한 번의 제출에서 다음 개선까지, 매장의 변화를 이어서 확인하세요."
      />
      <FilterBar
        account={account}
        extra={[
          {
            name: "status",
            label: "처리 상태",
            type: "select",
            options: ["queued", "running", "succeeded", "failed"].map((id) => ({
              id,
              name: {
                queued: "대기",
                running: "분석 중",
                succeeded: "완료",
                failed: "기술 실패",
              }[id]!,
            })),
          },
        ]}
      />
      <Resource value={value}>
        {(data: Page<Data>) => (
          <>
            {data.items.length ? (
              <div className="card-grid">
                {data.items.map((item) => (
                  <SubmissionCard
                    key={item.id}
                    item={item}
                    prefix={prefix}
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
function Submit({ account }: { account: AccountMe }) {
  const { query } = useLocation();
  const parentId = query.get("parent_submission_id");
  const stores = useResource<Page<Data>>(
    "/stores?page_size=100&is_active=true",
  );
  const categories = useResource<Page<Data>>(
    "/categories?page_size=100&is_active=true",
  );
  const parent = useResource<Data>(
    parentId ? "/submissions/" + parentId : null,
  );
  const [values, set] = useState<Data>({
    store_id: query.get("store_id") || "",
    category_id: query.get("category_id") || "",
    question: "",
  });
  const [files, setFiles] = useState<File[]>([]);
  const [photosBusy, setPhotosBusy] = useState(false);
  const m = useMutation();
  const key = useRef(idempotencyKey());
  const [validation, setValidation] = useState("");
  useEffect(() => {
    if (parent.data)
      set((v) => ({
        ...v,
        store_id: parent.data!.store_id,
        category_id: parent.data!.category_id,
      }));
  }, [parent.data]);
  useEffect(() => {
    key.current = idempotencyKey();
  }, [values, files]);
  return (
    <>
      <PageTitle
        title={
          parentId
            ? "개선한 매대를 다시 살펴봐요"
            : "오늘의 매대, 사진으로 점검"
        }
        description="매장과 매대 유형을 확인하고 사진을 보내 주세요."
      />
      <ol className="step-rail">
        <li className="current">1 매장과 매대</li>
        <li>2 사진과 질문</li>
        <li>3 분석 결과 확인</li>
      </ol>
      {parent.data && (
        <Panel title="이전 점검에서 이어집니다">
          <p>
            {parent.data.store_name} · {parent.data.category_name} ·{" "}
            {date(parent.data.created_at)}
          </p>
          {parent.data.review?.result.criteria
            .filter((x: Data) => x.verdict !== "pass")
            .map((x: Data) => (
              <p key={x.rule_key}>
                <Status value={x.verdict} /> {x.reason}
              </p>
            ))}
          <Link to={"/store-owner/submissions/" + parentId}>
            이전 결과 보기 →
          </Link>
        </Panel>
      )}
      <form
        className="panel"
        onSubmit={(e) => {
          e.preventDefault();
          if (photosBusy || m.busy) return;
          if (!files.length) {
            setValidation("사진을 1장 이상 선택해 주세요.");
            return;
          }
          setValidation("");
          void m.run(
            () =>
              api.upload<Data>(
                "/submissions",
                { ...values, parent_submission_id: parentId },
                files.map((file) => ({ field: "photos", file })),
                key.current,
              ),
            (result) => go("/store-owner/submissions/" + result.submission_id),
          );
        }}
      >
        <h2>1. 어디를 점검할까요?</h2>
        <Fields
          fields={[
            {
              name: "store_id",
              label: "매장",
              type: "select",
              required: true,
              options: stores.data?.items.filter((s) => s.can_submit !== false),
              disabled: !!parentId,
            },
            {
              name: "category_id",
              label: "매대 유형",
              type: "select",
              required: true,
              options: categories.data?.items,
              disabled: !!parentId,
            },
          ]}
          values={values}
          set={set}
        />
        {stores.data && !stores.data.items.length && (
          <p className="notice">
            제출 가능한 매장이 없습니다. 운영자에게 연결 상태를 확인해 주세요.
          </p>
        )}
        <h2>2. 사진과 궁금한 점을 알려 주세요</h2>
        <PhotoPicker files={files} set={setFiles} onBusyChange={setPhotosBusy} demoSample={publicDemoAccess && account.demo_public_access_enabled === true} />
        <label>
          질문 또는 현장 상황
          <textarea
            rows={4}
            maxLength={2000}
            value={values.question}
            onChange={(e) => set({ ...values, question: e.target.value })}
            placeholder="예: 앞줄 간격과 음료 배치가 기준에 맞는지 확인해 주세요."
          />
          <small>{values.question.length} / 2,000자</small>
        </label>
        {validation && (
          <p role="alert" className="error-text">
            {validation}
          </p>
        )}
        <ErrorBox error={m.error} />
        <ErrorBox error={stores.error || categories.error || parent.error} />
        <div className="form-footer">
          <p>
            AI는 1차 점검을 도와요. 최종 조치와 예외 판단은 점주·OFC가 함께
            확인해요.
          </p>
          <button
            disabled={
              m.busy ||
              photosBusy ||
              !stores.data?.items.length ||
              !categories.data?.items.length
            }
          >
            {m.busy ? "사진을 전송하고 있어요…" : "사진 제출하기 →"}
          </button>
        </div>
      </form>
    </>
  );
}
export function SubmissionDetail({
  id,
  account,
}: {
  id: string;
  account: AccountMe;
}) {
  const { search } = useLocation();
  const prefix = account.role === "store_owner" ? "/store-owner" : "/ofc-admin";
  const value = useResource<Data>("/submissions/" + id, true);
  const key = useRequestKey();
  return (
    <>
      <Link
        className="text-link"
        to={
          prefix +
          (account.role === "store_owner" ? "/history" : "/submissions") +
          search
        }
      >
        ← 점검 이력으로
      </Link>
      <Resource value={value}>
        {(item: Data) => (
          <>
            <PageTitle
              title={`${item.category_name} 점검 결과`}
              description={`${item.store_name} · ${date(item.created_at)} (한국 시간)`}
              action={<Status value={item.job.status} />}
            />
            <JobStatus job={item.job} />
            <div className="tags">
              <Source value={item.source_kind} />
              {item.review && <Source value={item.review.source_kind} />}
            </div>
            <div className="detail-grid">
              <div>
                <Panel title="제출 사진">
                  <Photos
                    photos={item.photos}
                    label={item.category_name + " 제출 사진"}
                    evidence
                  />
                  {item.question && (
                    <blockquote>
                      <span>점주의 질문</span>
                      <p>{item.question}</p>
                    </blockquote>
                  )}
                </Panel>
                {item.review && (
                  <ReviewContent review={item.review} context={item.context} />
                )}
              </div>
              <aside>
                <Panel title="다음 행동">
                  {account.role === "store_owner" &&
                    item.submitted_by_id === account.id && (
                      <Link
                        className="button"
                        to={
                          "/store-owner/submit" +
                          queryString({ parent_submission_id: id })
                        }
                      >
                        개선 후 다시 제출
                      </Link>
                    )}
                  {item.parent && (
                    <Link
                      className="button secondary"
                      to={`${prefix}/submissions/${id}/compare${search}`}
                    >
                      이전·이후 비교
                    </Link>
                  )}
                  <p>판단하기 어려운 항목은 OFC와 함께 확인해 주세요.</p>
                  {(account.role !== "store_owner" ||
                    item.submitted_by_id === account.id) && (
                    <ActionForm
                      title="OFC에 확인 요청"
                      button="OFC에 확인 요청"
                      fields={[
                        {
                          name: "title",
                          label: "문의 제목",
                          required: true,
                          maxLength: 160,
                        },
                        {
                          name: "description",
                          label: "확인할 내용",
                          type: "textarea",
                          required: true,
                          maxLength: 2000,
                        },
                      ]}
                      submit={(v) =>
                        api.post(
                          "/issues",
                          { ...v, submission_id: id, priority: "normal" },
                          key.get(id, v),
                        )
                      }
                      onDone={() => {
                        key.clear();
                        value.reload();
                      }}
                    />
                  )}
                  {item.issues.map((issue: Data) => (
                    <Link
                      className="issue-link"
                      key={issue.id}
                      to={`${prefix}/issues/${issue.id}`}
                    >
                      <Status value={issue.status} /> {issue.title}
                    </Link>
                  ))}
                </Panel>
                <Panel title="연결된 개선 이력">
                  {item.parent && (
                    <Link to={`${prefix}/submissions/${item.parent.id}`}>
                      이전 제출 · {date(item.parent.created_at)}
                    </Link>
                  )}
                  {item.children.map((child: Data) => (
                    <Link
                      className="issue-link"
                      key={child.id}
                      to={`${prefix}/submissions/${child.id}`}
                    >
                      후속 제출 · {date(child.created_at)} →
                    </Link>
                  ))}
                  {!item.parent && !item.children.length && (
                    <p className="muted">
                      첫 점검 기록이에요. 개선 후 다시 제출하면 변화가 이어져요.
                    </p>
                  )}
                </Panel>
              </aside>
            </div>
            <Panel title="점검에 적용한 기준과 Reference">
              <p className="muted">
                제출 당시 고정한 기준입니다. 이후 기준이 바뀌어도 이 점검의
                근거는 보존됩니다.
              </p>
              {item.context.guidelines.length ? (
                item.context.guidelines.map((g: Data) => (
                  <details key={g.version_id}>
                    <summary>
                      {g.title ?? g.rule_key} · {g.level} · v{g.version}
                    </summary>
                    <p>{g.text}</p>
                    <small>
                      기준 식별자 {g.guideline_id} · 버전 {g.version_id}
                    </small>
                  </details>
                ))
              ) : (
                <p className="notice">
                  적용할 기준이 없어 OFC 확인이 필요해요.
                </p>
              )}
              {item.context.references.length ? (
                <div className="card-grid">
                  {item.context.references.map((r: Data, index: number) => (
                    <SnapshotReference
                      key={r.reference_id}
                      reference={r}
                      position={r.position ?? index + 1}
                      photo={
                        item.reference_photos?.find(
                          (entry: Data) =>
                            entry.reference_id === r.reference_id,
                        )?.photo
                      }
                    />
                  ))}
                </div>
              ) : (
                <p className="notice">비교 Reference가 없습니다.</p>
              )}
            </Panel>
          </>
        )}
      </Resource>
    </>
  );
}
function ReviewContent({ review, context }: { review: Data; context: Data }) {
  const result = review.result;
  return (
    <>
      <Panel title="AI가 제안하는 다음 한 걸음">
        <div className="review-summary">
          <div>
            <span>준수율</span>
            <strong>{rate(review.compliance_rate)}</strong>
          </div>
          <div>
            <span>판단 가능률</span>
            <strong>{rate(review.assessable_rate)}</strong>
          </div>
          <div>
            <span>판단 가능한 기준</span>
            <strong>
              {review.pass_count + review.fail_count} /{" "}
              {review.pass_count + review.fail_count + review.unknown_count}
            </strong>
          </div>
        </div>
        {review.compliance_rate == null && (
          <p className="notice">
            판단 가능한 기준이 없어 준수율을 계산할 수 없습니다.
          </p>
        )}
        <p className="lead">{result.summary}</p>
        <h3>질문에 대한 답변</h3>
        <p>{result.question_answer}</p>
        <p>
          모델 신뢰도 <Status value={result.overall_confidence} />
        </p>
        {review.needs_ofc_review && (
          <p className="notice">
            OFC 확인 필요 · 사진만으로 판단하기 어려운 내용은 함께 확인해
            주세요.
          </p>
        )}
      </Panel>
      <Panel title="기준별 근거와 개선 행동">
        {result.criteria.map((criterion: Data) => (
          <article className="criterion" key={criterion.rule_key}>
            <div className="card-top">
              <h3>
                {context.guidelines.find(
                  (g: Data) => g.rule_key === criterion.rule_key,
                )?.title ?? criterion.rule_key}
              </h3>
              <Status value={criterion.verdict} />
            </div>
            <p>{criterion.reason}</p>
            {criterion.evidence.map((e: Data, i: number) => (
              <p className="evidence" key={i}>
                <a href={"#photo-" + e.photo_position}>
                  사진 {e.photo_position}
                </a>{" "}
                · {e.observation}
              </p>
            ))}
            {criterion.actions.length > 0 && (
              <ul className="action-list">
                {criterion.actions.map((action: string, i: number) => (
                  <li key={i}>{action}</li>
                ))}
              </ul>
            )}
            <small>기준 v{criterion.version}</small>
          </article>
        ))}
      </Panel>
      <Panel title="Reference와 비교">
        {result.reference_comparisons.length ? (
          result.reference_comparisons.map((r: Data) => (
            <article className="criterion" key={r.reference_id}>
              <Status value={r.verdict} />
              <p>{r.observation}</p>
              <small>제출 사진 {r.photo_positions.join(", ")} 기준</small>
            </article>
          ))
        ) : (
          <p>비교 Reference가 없습니다.</p>
        )}
        {result.limitations.length > 0 && (
          <div className="notice">
            <strong>이번 점검의 한계</strong>
            <ul>
              {result.limitations.map((l: string, i: number) => (
                <li key={i}>{l}</li>
              ))}
            </ul>
          </div>
        )}
      </Panel>
    </>
  );
}
export function Comparison({ id, prefix }: { id: string; prefix: string }) {
  const value = useResource<Data>(`/submissions/${id}/comparison`);
  const current = useResource<Data>(`/submissions/${id}`);
  const previous = useResource<Data>(value.data?.parent?.submission_id ? `/submissions/${value.data.parent.submission_id}` : null);
  const versionFor = (detail: Data, key: string) => {
    const applied = detail.context.guidelines.find((rule: Data) => rule.rule_key === key);
    return applied ? `v${applied.version}` : "미적용";
  };
  const submittedAt = (value: string) => new Date(value).toLocaleString("ko-KR", {
    timeZone: "Asia/Seoul", year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit",
  }) + " KST";
  return (
    <>
      <PageTitle title="한 걸음 더 좋아졌을까요?" description="이전과 현재 사진의 같은 기준을 비교해 보세요." />
      <Link className="text-link" to={`${prefix}/submissions/${id}`}>← 현재 점검 결과</Link>
      <Resource value={value}>
        {(data: Data) => !data.parent ? (
          <Empty>이전 제출이 없어 비교할 수 없습니다.</Empty>
        ) : (
          <Resource value={current}>{(currentDetail: Data) => (
            <Resource value={previous}>{(previousDetail: Data) => (
              <>
                <div className="comparison-grid">
                  {[
                    { title: "이전 점검", side: data.parent, detail: previousDetail },
                    { title: "현재 점검", side: data.current, detail: currentDetail },
                  ].map((x) => (
                    <Panel title={x.title} key={x.title}>
                      <p><time dateTime={x.detail.created_at}>{submittedAt(x.detail.created_at)}</time></p>
                      <details>
                        <summary>적용 기준 {x.detail.context.guidelines.length}개</summary>
                        {x.detail.context.guidelines.map((g: Data) => <p key={g.version_id}>기준 v{g.version} · {g.text}</p>)}
                        {!x.detail.context.guidelines.length && <p>적용 기준이 없습니다.</p>}
                      </details>
                      <Photos photos={x.side.photos} label={x.title + " 사진"} />
                      <p>준수율 {rate(x.side.compliance_rate)} · 판단 가능률 {rate(x.side.assessable_rate)}</p>
                      <Link to={`${prefix}/submissions/${x.side.submission_id}`}>상세 결과 보기 →</Link>
                    </Panel>
                  ))}
                </div>
                {data.criteria.some((c: Data) => c.criterion_changed) && (
                  <p className="notice">적용 기준이 달라 단순 점수 비교에 주의가 필요합니다.</p>
                )}
                <Panel title="항목별 변화">
                  {data.criteria.map((c: Data) => (
                    <div className="comparison-row" key={c.rule_key}>
                      <strong>{c.rule_key}</strong>
                      <span>{c.before ? <Status value={c.before} /> : "—"} → {c.after ? <Status value={c.after} /> : "—"}</span>
                      <Badge tone={c.change === "resolved" ? "good" : "neutral"}>
                        {c.change === "resolved" ? "개선됨" : {
                          unchanged: "변화 없음", regressed: "악화", unavailable: "비교 불가",
                        }[c.change as string]}
                      </Badge>
                      {c.criterion_changed && <small>기준 버전 변경</small>}
                      <small>이전 기준 {versionFor(previousDetail, c.rule_key)} → 현재 기준 {versionFor(currentDetail, c.rule_key)}</small>
                    </div>
                  ))}
                  {data.narrative && <p>{data.narrative}</p>}
                </Panel>
              </>
            )}</Resource>
          )}</Resource>
        )}
      </Resource>
    </>
  );
}

function SnapshotReference({
  reference,
  photo,
  position,
}: {
  reference: Data;
  photo?: Data;
  position: number;
}) {
  const resolvedPhoto = {
    ...(photo ?? {
      id: reference.reference_id,
      media_id: reference.photo_id,
      url: "/api/media/" + reference.photo_id,
    }),
    position,
  };
  return (
    <div>
      <Photos photos={[resolvedPhoto]} label="비교 Reference" />
      <p>{reference.caption}</p>
    </div>
  );
}
