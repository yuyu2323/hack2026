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
  date,
  Empty,
  ErrorBox,
  Fields,
  go,
  Lane,
  Link,
  listQuery,
  PageTitle,
  Pager,
  Panel,
  queryPatch,
  Resource,
  roles,
  Status,
  type Data,
  type Field,
  useLocation,
  useMutation,
  useResource,
  useRequestKey,
} from "../shared/core";
const reason: Field = {
  name: "reason",
  label: "변경 사유",
  required: true,
  maxLength: 500,
};
const roleOptions = ["store_owner", "ofc", "regional", "hq"].map((id) => ({
  id,
  name: roles[id],
}));
export function Operations({ account }: { account: AccountMe }) {
  const { path } = useLocation();
  if (path.includes("/accounts")) return <Accounts />;
  if (path.includes("/catalogs")) return <Catalogs />;
  if (path.includes("/jobs")) return <Jobs />;
  if (path.endsWith("/audit")) return <Audit />;
  if (path.endsWith("/announcements")) return <Announcements />;
  return <OperationsHome />;
}
function OperationsHome() {
  const value = useResource<Data>("/operations/status");
  useEffect(() => {
    const interval = setInterval(value.reload, 15000);
    return () => clearInterval(interval);
  }, []);
  return (
    <>
      <PageTitle
        eyebrow="SERVICE WORKFLOW"
        title="서비스가 잘 이어지도록"
        description="복구할 작업과 연결할 계정을 먼저 확인하세요. 기술 상태는 15초마다 갱신됩니다."
        action={
          <button className="secondary" onClick={value.reload}>
            상태 새로고침
          </button>
        }
      />
      <Resource value={value}>
        {(data: Data) => (
          <>
            <div className="lanes">
              <Lane
                step="01"
                title="실패 작업 복구"
                caption="종료된 실패부터 확인하세요"
              >
                <article className="work-card priority">
                  <Badge tone="warn">실제 작업</Badge>
                  <h3>복구 검토 {data.jobs.failed}건</h3>
                  <p>
                    실패 분류와 시도 이력을 확인한 뒤 사유를 기록하고
                    재처리하세요.
                  </p>
                  <Link
                    className="card-action"
                    to="/platform-admin/jobs?status=failed&is_fixture=false"
                  >
                    실패 작업 확인 →
                  </Link>
                </article>
                <article className="work-card">
                  <Badge tone="mock">Mock 장애 사례</Badge>
                  <h3>시연 실패 {data.fixture_jobs.failed}건</h3>
                  <Link to="/platform-admin/jobs?is_fixture=true">
                    시연 작업 보기 →
                  </Link>
                </article>
              </Lane>
              <Lane
                step="02"
                title="이용 연결 정정"
                caption="업무 시작을 막는 누락을 해결해요"
              >
                <article className="work-card">
                  <h3>
                    연결 없는 점주 {data.data_quality.unmapped_owner_accounts}명
                  </h3>
                  <p>계정의 역할·지역·매장 연결을 확인해 주세요.</p>
                  <Link
                    className="card-action"
                    to="/platform-admin/accounts?role=store_owner&mapping_status=missing"
                  >
                    점주 연결 확인 →
                  </Link>
                </article>
                <article className="work-card">
                  <h3>
                    연결 없는 OFC {data.data_quality.unmapped_ofc_accounts}명
                  </h3>
                  <p>
                    담당 미배정 매장 {data.data_quality.unassigned_stores}곳
                  </p>
                  <Link
                    className="card-action"
                    to="/platform-admin/accounts?role=ofc&mapping_status=missing"
                  >
                    OFC 연결 확인 →
                  </Link>
                </article>
              </Lane>
              <Lane
                step="03"
                title="서비스 확인"
                caption="프로세스와 모델 실행을 구분해요"
              >
                {data.services.map((s: Data) => (
                  <article className="work-card" key={s.name}>
                    <div className="card-top">
                      <h3>{s.name}</h3>
                      <ServiceState value={s.status} />
                    </div>
                    <p>확인 {date(s.checked_at)}</p>
                    {s.heartbeat_at && <p>Heartbeat {date(s.heartbeat_at)}</p>}
                    {s.error_code && <p>오류 분류 {s.error_code}</p>}
                  </article>
                ))}
              </Lane>
            </div>
            <Panel title="처리 흐름">
              <div className="summary-line">
                {Object.entries(data.jobs).map(([key, count]) => (
                  <Link key={key} to={"/platform-admin/jobs?status=" + key}>
                    <Status value={key} /> {String(count)}건
                  </Link>
                ))}
              </div>
              <p>
                worker heartbeat 경과{" "}
                {data.worker_heartbeat_age_seconds == null
                  ? "미확인"
                  : Math.round(data.worker_heartbeat_age_seconds) + "초"}
              </p>
              <p>
                최근 실제 모델 실행{" "}
                <ServiceState value={data.model.readiness} /> · 성공{" "}
                {date(data.model.last_success_at)} · 실패{" "}
                {date(data.model.last_failure_at)}
              </p>
              {data.model.last_error_code && (
                <p>최근 모델 오류 분류 {data.model.last_error_code}</p>
              )}
              <p className="muted">
                프로세스가 살아 있는 것과 실제 모델이 분석을 수행할 수 있는지는
                다릅니다. 상태 조회로 모델 분석을 다시 실행하지 않습니다.
              </p>
            </Panel>
          </>
        )}
      </Resource>
    </>
  );
}
function OperationFilters({ fields }: { fields: Field[] }) {
  const { query } = useLocation();
  const [v, set] = useState<Data>(Object.fromEntries(query));
  useEffect(() => set(Object.fromEntries(query)), [query.toString()]);
  return (
    <form
      className="filters"
      onSubmit={(e) => {
        e.preventDefault();
        queryPatch({ ...v, page: 1 });
      }}
    >
      <Fields fields={fields} values={v} set={set} />
      <button className="secondary">조건 적용</button>
    </form>
  );
}
function Impact({ value }: { value: Data | null }) {
  return value ? (
    <div className="notice" role="status">
      <strong>변경을 저장했습니다.</strong>
      <p>
        영향 매장 {value.affected_store_ids.length}곳 · 종료된 연결{" "}
        {value.ended_mapping_ids.length}개 · 활성 세션{" "}
        {value.active_session_count}개
      </p>
      <p>
        {value.new_business_blocked
          ? "신규 업무 접근이 차단됩니다."
          : "다음 요청부터 변경된 접근 범위를 적용합니다."}
      </p>
    </div>
  ) : null;
}
function Accounts() {
  const { path, search } = useLocation();
  const id = path.split("/")[3];
  const value = useResource<Data>(
    id
      ? "/operations/accounts/" + id
      : "/operations/accounts" +
          listQuery(search, [
            "page",
            "page_size",
            "q",
            "role",
            "is_active",
            "mapping_status",
          ]),
  );
  const regions = useResource<Page<Data>>("/operations/regions?page_size=100");
  const stores = useResource<Page<Data>>("/operations/stores?page_size=100");
  const [show, setShow] = useState(false),
    [impact, setImpact] = useState<Data | null>(null);
  const fields: Field[] = [
    {
      name: "display_name",
      label: "표시 이름",
      required: true,
      maxLength: 100,
    },
    {
      name: "role",
      label: "역할",
      required: true,
      type: "select",
      options: roleOptions,
    },
    {
      name: "region_id",
      label: "소속 지역 (OFC·지역 관리자 필수)",
      type: "select",
      options: regions.data?.items,
    },
    reason,
  ];
  return (
    <>
      <PageTitle
        title={id ? "계정의 이용 범위를 확인해요" : "사람과 매장을 연결해요"}
        description="일반 계정의 활성 상태와 현재 역할·담당 범위를 관리합니다."
        action={
          !id && (
            <button onClick={() => setShow((x) => !x)}>
              {show ? "작성 닫기" : "+ 계정 만들기"}
            </button>
          )
        }
      />
      {!id && (
        <OperationFilters
          fields={[
            { name: "q", label: "계정 검색" },
            {
              name: "role",
              label: "역할",
              type: "select",
              options: roleOptions,
            },
            {
              name: "is_active",
              label: "활성 상태",
              type: "select",
              options: [
                { id: "true", name: "활성" },
                { id: "false", name: "비활성" },
              ],
            },
            {
              name: "mapping_status",
              label: "연결 상태",
              type: "select",
              options: [
                { id: "ready", name: "정상" },
                { id: "missing", name: "누락" },
                { id: "invalid", name: "확인 필요" },
              ],
            },
          ]}
        />
      )}
      <Impact value={impact} />
      {show && !id && (
        <Panel title="새 일반 계정">
          <ActionForm
            title="로그인 및 소속 정보"
            fields={[
              {
                name: "login_id",
                label: "로그인 ID",
                required: true,
                minLength: 3,
                maxLength: 80,
                hint: "영문 소문자·숫자·점·밑줄·하이픈",
              },
              {
                name: "password",
                label: "초기 비밀번호",
                type: "password",
                required: true,
                minLength: 12,
                maxLength: 128,
                hint: "12~128자. 저장 후 다시 표시하지 않습니다.",
              },
              ...fields,
            ]}
            submit={(v) =>
              api.post<Data>("/operations/accounts", {
                ...v,
                region_id: v.region_id || null,
              })
            }
            onDone={(r) => {
              setShow(false);
              go("/platform-admin/accounts/" + r.id);
            }}
            button="계정 만들기"
          />
        </Panel>
      )}
      <Resource value={value}>
        {(data: Data) =>
          id ? (
            <>
              <Link
                className="text-link"
                to={"/platform-admin/accounts" + search}
              >
                ← 계정 목록
              </Link>
              <Panel title={data.display_name}>
                <div className="tags">
                  <Badge>{roles[data.role]}</Badge>
                  <Badge>{data.is_active ? "활성" : "비활성"}</Badge>
                  <Status value={data.mapping_status} />
                </div>
                <p>로그인 ID {data.login_id}</p>
                <p>
                  연결 매장{" "}
                  {data.store_ids
                    .map(
                      (sid: string) =>
                        stores.data?.items.find((s) => s.id === sid)?.name ??
                        sid,
                    )
                    .join(", ") || "없음"}
                </p>
              </Panel>
              {data.role === "platform_operator" ? (
                <p className="notice">
                  플랫폼 운영자 계정 변경은 초기 설정 절차에서만 가능합니다.
                </p>
              ) : (
                <>
                  <div className="comparison-grid">
                    <Panel>
                      <ActionForm
                        title="역할·소속·활성 상태 변경"
                        initial={{
                          display_name: data.display_name,
                          role: data.role,
                          region_id: data.region_id ?? "",
                          is_active: String(data.is_active),
                          password: "",
                        }}
                        fields={[
                          ...fields.slice(0, 3),
                          {
                            name: "is_active",
                            label: "활성 상태",
                            required: true,
                            type: "select",
                            options: [
                              { id: "true", name: "활성" },
                              { id: "false", name: "비활성" },
                            ],
                          },
                          {
                            name: "password",
                            label: "새 비밀번호 (변경할 때만)",
                            type: "password",
                            minLength: 12,
                            maxLength: 128,
                          },
                          reason,
                        ]}
                        submit={(v) => {
                          const { password, ...rest } = v;
                          return api.patch<Data>("/operations/accounts/" + id, {
                            ...rest,
                            region_id: v.region_id || null,
                            is_active: v.is_active === "true",
                            version: data.version,
                            ...(password ? { password } : {}),
                          });
                        }}
                        onDone={(r) => {
                          setImpact(r.impact);
                          value.reload();
                        }}
                      >
                        <p>
                          역할·지역 변경 시 기존 연결이 종료될 수 있습니다.
                          비활성화하면 기존 로그인에서도 접근이 차단됩니다.
                        </p>
                      </ActionForm>
                    </Panel>
                    {["store_owner", "ofc"].includes(data.role) && (
                      <Panel>
                        <MappingForm
                          account={data}
                          stores={stores.data?.items ?? []}
                          done={(r) => {
                            setImpact(r.impact);
                            value.reload();
                          }}
                        />
                      </Panel>
                    )}
                  </div>
                </>
              )}
            </>
          ) : (
            <>
              {data.items.length ? (
                <div className="card-grid">
                  {data.items.map((a: Data) => (
                    <article className="work-card" key={a.id}>
                      <div className="tags">
                        <Badge>{roles[a.role]}</Badge>
                        <Status value={a.mapping_status} />
                        <Badge>{a.is_active ? "활성" : "비활성"}</Badge>
                      </div>
                      <h2>
                        <Link to={"/platform-admin/accounts/" + a.id + search}>
                          {a.display_name}
                        </Link>
                      </h2>
                      <p>
                        {a.login_id} · 연결 매장 {a.store_ids.length}곳
                      </p>
                      <Link
                        className="card-action"
                        to={"/platform-admin/accounts/" + a.id + search}
                      >
                        계정과 연결 확인 →
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
    </>
  );
}
function MappingForm({
  account,
  stores,
  done,
}: {
  account: Data;
  stores: Data[];
  done: (r: Data) => void;
}) {
  const [selected, set] = useState<string[]>(account.store_ids);
  const [reasonValue, setReason] = useState("");
  const m = useMutation();
  const allowed = stores.filter(
    (s) =>
      s.is_active &&
      (account.role !== "ofc" || s.region_id === account.region_id),
  );
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void m.run(
          () =>
            api.put<Data>(`/operations/accounts/${account.id}/mappings`, {
              version: account.version,
              store_ids: selected,
              reason: reasonValue,
            }),
          done,
        );
      }}
    >
      <h3>매장 연결 전체 변경</h3>
      <p>
        선택된 매장만 활성 연결로 남습니다. 해제한 매장의 과거 기록은
        보존됩니다.
      </p>
      <div className="check-list">
        {allowed.map((s) => (
          <label className="checkbox" key={s.id}>
            <input
              type="checkbox"
              checked={selected.includes(s.id)}
              onChange={(e) =>
                set(
                  e.target.checked
                    ? [...selected, s.id]
                    : selected.filter((id) => id !== s.id),
                )
              }
            />
            <span>
              {s.name} · {s.region_name}
            </span>
          </label>
        ))}
      </div>
      <label>
        변경 사유 *
        <textarea
          required
          maxLength={500}
          value={reasonValue}
          onChange={(e) => setReason(e.target.value)}
        />
      </label>
      <ErrorBox error={m.error} />
      <button disabled={m.busy}>
        {m.busy ? "저장 중…" : "선택한 연결 저장"}
      </button>
    </form>
  );
}
function Catalogs() {
  const { search, query } = useLocation();
  const kind = ["regions", "stores", "categories"].includes(
    query.get("kind") ?? "",
  )
    ? query.get("kind")!
    : "regions";
  const names: Record<string, string> = {
    regions: "지역",
    stores: "매장",
    categories: "카테고리",
  };
  const value = useResource<Page<Data>>(
    "/operations/" +
      kind +
      listQuery(search, ["page", "page_size", "q", "region_id", "is_active"]),
  );
  const regions = useResource<Page<Data>>("/operations/regions?page_size=100");
  const [edit, setEdit] = useState<Data | null>(null),
    [show, setShow] = useState(false),
    [impact, setImpact] = useState<Data | null>(null);
  const fields: Field[] = [
    ...(!edit
      ? [{ name: "code", label: "코드", required: true, maxLength: 32 }]
      : []),
    { name: "name", label: "이름", required: true, maxLength: 120 },
    ...(kind === "stores"
      ? [
          {
            name: "region_id",
            label: "지역",
            type: "select",
            required: true,
            options: regions.data?.items,
          },
          {
            name: "store_type",
            label: "매장 유형",
            required: true,
            maxLength: 60,
          },
          { name: "address", label: "주소", maxLength: 500 },
        ]
      : kind === "categories"
        ? [
            {
              name: "description",
              label: "설명",
              type: "textarea",
              maxLength: 2000,
            },
          ]
        : []),
    ...(edit
      ? [
          {
            name: "is_active",
            label: "활성 상태",
            required: true,
            type: "select",
            options: [
              { id: "true", name: "활성" },
              { id: "false", name: "비활성" },
            ],
          },
        ]
      : []),
    reason,
  ];
  return (
    <>
      <PageTitle
        title="업무의 기본 연결을 정리해요"
        description="지역·매장·카테고리 기준 정보. 비활성화해도 과거 이력을 보존합니다."
      />
      <nav className="tabs" aria-label="기준 정보 종류">
        {Object.entries(names).map(([key, name]) => (
          <button
            className={kind === key ? "active" : "secondary"}
            key={key}
            onClick={() => {
              setShow(false);
              setEdit(null);
              queryPatch({ kind: key, page: 1 });
            }}
          >
            {name}
          </button>
        ))}
      </nav>
      <OperationFilters
        fields={[
          { name: "q", label: "이름·코드 검색" },
          {
            name: "is_active",
            label: "활성 상태",
            type: "select",
            options: [
              { id: "true", name: "활성" },
              { id: "false", name: "비활성" },
            ],
          },
        ]}
      />
      <button
        onClick={() => {
          setEdit(null);
          setShow(true);
        }}
      >
        + {names[kind]} 등록
      </button>
      <Impact value={impact} />
      {show && (
        <Panel>
          <ActionForm
            key={kind + "-" + (edit?.id ?? "new")}
            title={names[kind] + (edit ? " 변경" : " 등록")}
            initial={
              edit
                ? {
                    name: edit.name,
                    region_id: edit.region_id,
                    store_type: edit.store_type,
                    address: edit.address,
                    description: edit.description,
                    is_active: String(edit.is_active),
                  }
                : {}
            }
            fields={fields}
            submit={(v) => {
              const body: Data = {};
              for (const f of fields)
                if (v[f.name] !== undefined && v[f.name] !== "")
                  body[f.name] = v[f.name];
              if (edit) {
                body.is_active = v.is_active === "true";
                body.version = edit.version;
                return api.patch<Data>(`/operations/${kind}/${edit.id}`, body);
              }
              return api.post<Data>("/operations/" + kind, body);
            }}
            onDone={(r) => {
              setShow(false);
              setEdit(null);
              setImpact(r.impact ?? null);
              value.reload();
              regions.reload();
            }}
            button={edit ? "변경 저장" : "등록하기"}
          >
            <p>
              소속·활성 상태 변경은 새 업무의 접근 가능 여부에 영향을 줍니다.
            </p>
          </ActionForm>
        </Panel>
      )}
      <Resource value={value}>
        {(data: Page<Data>) => (
          <>
            {data.items.length ? (
              <div className="card-grid">
                {data.items.map((item) => (
                  <article className="work-card" key={item.id}>
                    <Badge>{item.is_active ? "활성" : "비활성"}</Badge>
                    <h2>{item.name}</h2>
                    <p>
                      {item.code}
                      {item.region_name ? " · " + item.region_name : ""}
                    </p>
                    {kind === "stores" && (
                      <p>
                        OFC {item.ofc?.display_name ?? "미배정"} · 점주{" "}
                        {item.owner_count}명
                      </p>
                    )}
                    <p>{item.description ?? item.address}</p>
                    <button
                      className="secondary"
                      onClick={() => {
                        setEdit(item);
                        setShow(true);
                      }}
                    >
                      정보 변경
                    </button>
                    {kind === "stores" && (
                      <Link className="text-link" to="/platform-admin/accounts">
                        계정 연결 정정 →
                      </Link>
                    )}
                  </article>
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
function Jobs() {
  const { path, search } = useLocation();
  const id = path.split("/")[3];
  const value = useResource<Data>(
    id
      ? "/operations/jobs/" + id
      : "/operations/jobs" +
          listQuery(search, [
            "page",
            "page_size",
            "status",
            "error_code",
            "is_fixture",
          ]),
  );
  const key = useRequestKey();
  return (
    <>
      <PageTitle
        title={id ? "실패 원인에서 복구까지" : "처리 작업을 확인해요"}
        description="작업의 기술 상태와 시도 이력을 확인합니다. 영업 사진과 평가 본문은 포함하지 않습니다."
      />
      {!id && (
        <OperationFilters
          fields={[
            {
              name: "status",
              label: "처리 상태",
              type: "select",
              options: [
                { id: "queued", name: "대기" },
                { id: "running", name: "분석 중" },
                { id: "succeeded", name: "성공" },
                { id: "failed", name: "실패" },
              ],
            },
            { name: "error_code", label: "오류 분류" },
            {
              name: "is_fixture",
              label: "작업 출처",
              type: "select",
              options: [
                { id: "false", name: "실제 작업" },
                { id: "true", name: "Mock 장애 사례" },
              ],
            },
          ]}
        />
      )}
      <Resource value={value}>
        {(data: Data) =>
          id ? (
            <>
              <Link to={"/platform-admin/jobs" + search}>← 처리 작업 목록</Link>
              <Panel title="현재 작업 상태">
                <div className="tags">
                  <Status value={data.status} />
                  {data.is_fixture && <Badge tone="mock">Mock 장애 사례</Badge>}
                </div>
                <p className="identifier">작업 {data.id}</p>
                <p>
                  접수 {date(data.created_at)} · 종료 {date(data.finished_at)} ·
                  시도 {data.attempt_count}회
                </p>
                {data.error_code && (
                  <p>
                    {data.error_code} · {data.error_message}
                  </p>
                )}
                {data.can_retry ? (
                  <ActionForm
                    title="동일 입력으로 실패 작업 재처리"
                    fields={[reason]}
                    submit={(v) =>
                      api.post(
                        "/operations/jobs/" + id + "/retry",
                        v,
                        key.get(id!, v),
                      )
                    }
                    onDone={() => {
                      key.clear();
                      value.reload();
                    }}
                    button="실패 작업 재처리"
                  >
                    <p>
                      종료된 실패만 재처리합니다. 기존 시도 이력은 보존하고
                      새로운 시도를 만듭니다.
                    </p>
                  </ActionForm>
                ) : (
                  <p className="notice">
                    현재 상태에서는 재처리할 수 없습니다. 진행 중이거나 성공한
                    작업은 중복 실행하지 않습니다.
                  </p>
                )}
                <button className="secondary" onClick={value.reload}>
                  현재 상태 새로고침
                </button>
              </Panel>
              <Panel title="시도 이력">
                {data.attempts.map((a: Data) => (
                  <article className="timeline-entry" key={a.id}>
                    <div className="card-top">
                      <h3>{a.attempt_number}번째 시도</h3>
                      <Status value={a.status} />
                    </div>
                    <p>
                      대기 {date(a.queued_at)} → 시작 {date(a.started_at)} →
                      종료 {date(a.finished_at)}
                    </p>
                    <p>
                      처리 기한 {date(a.deadline_at)} · 점유 만료{" "}
                      {date(a.lease_expires_at)}
                    </p>
                    <p>결과 반영 {a.result_applied ? "반영됨" : "미반영"}</p>
                    {a.error_code && (
                      <p>
                        {a.error_code} · {a.error_message}
                      </p>
                    )}
                  </article>
                ))}
              </Panel>
            </>
          ) : (
            <>
              {data.items.length ? (
                <div className="card-grid">
                  {data.items.map((job: Data) => (
                    <article className="work-card" key={job.id}>
                      <div className="tags">
                        <Status value={job.status} />
                        {job.is_fixture && (
                          <Badge tone="mock">Mock 장애 사례</Badge>
                        )}
                      </div>
                      <h2>{job.error_code ?? "처리 작업"}</h2>
                      <p>
                        {job.error_message ??
                          "작업의 현재 상태와 이력을 확인하세요."}
                      </p>
                      <p>
                        {date(job.created_at)} · 시도 {job.attempt_count}회
                      </p>
                      <Link
                        className="card-action"
                        to={"/platform-admin/jobs/" + job.id + search}
                      >
                        시도 이력과 복구 확인 →
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
    </>
  );
}
function Audit() {
  const { search } = useLocation();
  const value = useResource<Page<Data>>(
    "/operations/audit" +
      listQuery(search, [
        "page",
        "page_size",
        "actor_id",
        "target_type",
        "target_id",
        "date_from",
        "date_to",
      ]),
  );
  return (
    <>
      <PageTitle
        title="변경의 이유를 남겨요"
        description="누가, 언제, 무엇을 바꾸었는지 확인하는 운영 이력입니다."
      />
      <OperationFilters
        fields={[
          { name: "actor_id", label: "수행자 ID" },
          { name: "target_type", label: "대상 유형" },
          { name: "target_id", label: "대상 ID" },
          { name: "date_from", label: "시작일 (UTC)", type: "date" },
          { name: "date_to", label: "종료일 (UTC)", type: "date" },
        ]}
      />
      <Resource value={value}>
        {(data: Page<Data>) => (
          <>
            {data.items.length ? (
              data.items.map((event) => (
                <article className="panel" key={event.id}>
                  <div className="card-top">
                    <h2>{event.action}</h2>
                    <Badge>{event.outcome}</Badge>
                  </div>
                  <p>
                    {event.actor_name} · {date(event.created_at)} ·{" "}
                    {event.target_type}
                  </p>
                  <p className="identifier">대상 {event.target_id}</p>
                  <blockquote>{event.reason}</blockquote>
                  <details>
                    <summary>변경 전·후 확인</summary>
                    <div className="comparison-grid">
                      <SafeSummary title="변경 전" data={event.before_data} />
                      <SafeSummary title="변경 후" data={event.after_data} />
                    </div>
                    <small>요청 번호 {event.request_id}</small>
                  </details>
                </article>
              ))
            ) : (
              <Empty>아직 기록된 운영 변경이 없습니다.</Empty>
            )}
            <Pager data={data} />
          </>
        )}
      </Resource>
    </>
  );
}
function SafeSummary({ title, data }: { title: string; data: Data | null }) {
  return (
    <div>
      <h3>{title}</h3>
      <dl>
        {Object.entries(data ?? {}).map(([key, val]) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>
              {typeof val === "object"
                ? Array.isArray(val)
                  ? val.join(", ")
                  : JSON.stringify(val)
                : String(val ?? "—")}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
function Announcements() {
  const value = useResource<Page<Data>>(
    "/operations/announcements" +
      listQuery(location.search, ["page", "page_size", "is_active"]),
  );
  const [edit, setEdit] = useState<Data | null>(null),
    [show, setShow] = useState(false);
  return (
    <>
      <PageTitle
        title="필요한 안내를 전해요"
        description="게시 기간 동안 모든 로그인 사용자에게 일반 텍스트 공지를 표시합니다."
        action={
          <button
            onClick={() => {
              setEdit(null);
              setShow(true);
            }}
          >
            + 공지 작성
          </button>
        }
      />
      {show && (
        <Panel>
          <ActionForm
            key={edit?.id ?? "new"}
            title={edit ? "공지 수정" : "새 공지"}
            initial={
              edit
                ? {
                    title: edit.title,
                    body: edit.body,
                    severity: edit.severity,
                    starts_at: toLocal(edit.starts_at),
                    ends_at: edit.ends_at ? toLocal(edit.ends_at) : "",
                    is_active: String(edit.is_active),
                  }
                : {
                    severity: "info",
                    starts_at: toLocal(new Date().toISOString()),
                  }
            }
            fields={[
              {
                name: "title",
                label: "공지 제목",
                required: true,
                maxLength: 160,
              },
              {
                name: "body",
                label: "안내 내용",
                type: "textarea",
                required: true,
                maxLength: 4000,
              },
              {
                name: "severity",
                label: "안내 종류",
                type: "select",
                required: true,
                options: [
                  { id: "info", name: "일반 안내" },
                  { id: "maintenance", name: "점검 안내" },
                ],
              },
              {
                name: "starts_at",
                label: "게시 시작 (한국 시간)",
                type: "datetime-local",
                required: true,
              },
              {
                name: "ends_at",
                label: "게시 종료 (한국 시간)",
                type: "datetime-local",
              },
              ...(edit
                ? [
                    {
                      name: "is_active",
                      label: "활성 상태",
                      type: "select",
                      required: true,
                      options: [
                        { id: "true", name: "활성" },
                        { id: "false", name: "비활성" },
                      ],
                    },
                  ]
                : []),
              reason,
            ]}
            submit={(v) => {
              const body = {
                ...v,
                starts_at: new Date(v.starts_at).toISOString(),
                ends_at: v.ends_at ? new Date(v.ends_at).toISOString() : null,
                ...(edit
                  ? { version: edit.version, is_active: v.is_active === "true" }
                  : {}),
              };
              return edit
                ? api.patch("/operations/announcements/" + edit.id, body)
                : api.post("/operations/announcements", body);
            }}
            onDone={() => {
              setShow(false);
              value.reload();
              window.dispatchEvent(new Event("announcements-refresh"));
            }}
            button={edit ? "변경 저장" : "공지 등록"}
          />
        </Panel>
      )}
      <Resource value={value}>
        {(data: Page<Data>) => (
          <>
            {data.items.length ? (
              data.items.map((a) => (
                <article className="panel" key={a.id}>
                  <div className="tags">
                    <Badge>{a.is_active ? "활성" : "비활성"}</Badge>
                    <Badge>{a.severity}</Badge>
                  </div>
                  <h2>{a.title}</h2>
                  <p className="preserve">{a.body}</p>
                  <p>
                    {date(a.starts_at)} ~{" "}
                    {a.ends_at ? date(a.ends_at) : "종료일 없음"}
                  </p>
                  <button
                    className="secondary"
                    onClick={() => {
                      setEdit(a);
                      setShow(true);
                    }}
                  >
                    공지 수정
                  </button>
                </article>
              ))
            ) : (
              <Empty>등록된 공지가 없습니다.</Empty>
            )}
            <Pager data={data} />
          </>
        )}
      </Resource>
    </>
  );
}
function toLocal(iso: string) {
  const d = new Date(iso);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}

function ServiceState({ value }: { value: string }) {
  const labels: Record<string, string> = {
    available: "사용 가능",
    unavailable: "사용 불가",
    unknown: "미확인",
    healthy: "정상",
    up: "정상",
    down: "응답 없음",
    stale: "응답 지연",
    degraded: "성능 저하",
  };
  return (
    <Badge
      tone={
        ["available", "healthy", "up"].includes(value)
          ? "good"
          : ["unavailable", "down", "stale", "degraded"].includes(value)
            ? "warn"
            : "neutral"
      }
    >
      {labels[value] ?? value}
    </Badge>
  );
}
