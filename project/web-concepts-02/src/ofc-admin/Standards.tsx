import { useRef, useState } from "react";
import type { AccountMe, Page } from "@storeloop/api-client";
import {
  ActionForm,
  accessFailure,
  api,
  ApiError,
  Badge,
  date,
  Empty,
  ErrorBox,
  Fields,
  go,
  Link,
  listQuery,
  PageTitle,
  Pager,
  Panel,
  queryPatch,
  queryString,
  Resource,
  type Data,
  type Field,
  useLocation,
  useMutation,
  useResource,
} from "../shared/core";
import { PhotoPicker, Photos } from "../shared/photos";
const reason: Field = {
  name: "reason",
  label: "변경 사유",
  required: true,
  maxLength: 500,
};
function useScope(account: AccountMe) {
  const stores = useResource<Page<Data>>(
    "/stores?page_size=100&is_active=true",
  );
  const categories = useResource<Page<Data>>(
    "/categories?page_size=100&is_active=true",
  );
  const regions = useResource<Page<Data>>("/regions?page_size=100");
  return {
    stores: stores.data?.items ?? [],
    categories: categories.data?.items ?? [],
    regions: regions.data?.items ?? [],
  };
}
function canEdit(g: Data, account: AccountMe, stores: Data[]) {
  return (
    account.role === "hq" ||
    (account.role === "regional" &&
      (g.level === "REGION"
        ? g.region_id === account.region_id
        : ["STORE", "CATEGORY"].includes(g.level) &&
          stores.some((s) => s.id === g.store_id))) ||
    (account.role === "ofc" &&
      ["STORE", "CATEGORY"].includes(g.level) &&
      stores.some((s) => s.id === g.store_id))
  );
}
export function Guidelines({ account }: { account: AccountMe }) {
  const { path, search, query } = useLocation();
  const id = path.split("/")[3];
  const scope = useScope(account);
  const value = useResource<Data>(
    id
      ? "/guidelines/" + id
      : "/guidelines" +
          listQuery(search, [
            "page",
            "page_size",
            "store_id",
            "region_id",
            "category_id",
            "level",
            "is_active",
          ]),
  );
  const versions = useResource<Page<Data>>(
    id ? `/guidelines/${id}/versions?page_size=100` : null,
  );
  const [show, setShow] = useState(false);
  const levels = (
    account.role === "hq"
      ? ["HQ", "REGION", "STORE", "CATEGORY"]
      : account.role === "regional"
        ? ["REGION", "STORE", "CATEGORY"]
        : ["STORE", "CATEGORY"]
  ).map((id) => ({
    id,
    name: { HQ: "본사", REGION: "지역", STORE: "매장", CATEGORY: "매대" }[id]!,
  }));
  const [filters, setFilters] = useState<Data>(Object.fromEntries(query));
  return (
    <>
      <PageTitle
        title={
          id ? "기준의 내용과 변화를 확인해요" : "좋은 진열의 기준을 만들어요"
        }
        description="본사 → 지역 → 매장 → 매대. 더 구체적인 기준이 같은 항목에 우선 적용됩니다."
        action={
          !id && (
            <button onClick={() => setShow((x) => !x)}>
              {show ? "작성 닫기" : "+ 진열 기준 등록"}
            </button>
          )
        }
      />
      {!id && (
        <form
          className="filters"
          onSubmit={(e) => {
            e.preventDefault();
            queryPatch({ ...filters, page: 1 });
          }}
        >
          <Fields
            fields={[
              {
                name: "level",
                label: "기준 단계",
                type: "select",
                options: [
                  { id: "HQ", name: "본사" },
                  { id: "REGION", name: "지역" },
                  { id: "STORE", name: "매장" },
                  { id: "CATEGORY", name: "매대" },
                ],
              },
              {
                name: "store_id",
                label: "매장",
                type: "select",
                options: scope.stores,
              },
              {
                name: "category_id",
                label: "매대 유형",
                type: "select",
                options: scope.categories,
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
            ]}
            values={filters}
            set={setFilters}
          />
          <button className="secondary">조건 적용</button>
        </form>
      )}
      {show && !id && (
        <Panel title="새 진열 기준">
          <ActionForm
            title="범위와 내용을 입력하세요"
            fields={[
              {
                name: "rule_key",
                label: "기준 식별 이름",
                required: true,
                maxLength: 80,
                hint: "영문 소문자로 시작, 소문자·숫자·밑줄만 사용",
              },
              {
                name: "title",
                label: "기준 제목",
                required: true,
                maxLength: 160,
              },
              {
                name: "level",
                label: "기준 단계",
                type: "select",
                required: true,
                options: levels,
              },
              {
                name: "region_id",
                label: "지역 (지역 기준)",
                type: "select",
                options: scope.regions,
              },
              {
                name: "store_id",
                label: "매장 (매장·매대 기준)",
                type: "select",
                options: scope.stores,
              },
              {
                name: "category_id",
                label: "매대 유형 (매대 기준)",
                type: "select",
                options: scope.categories,
              },
              {
                name: "text",
                label: "관찰 가능한 진열 기준",
                type: "textarea",
                required: true,
                maxLength: 6000,
              },
              reason,
            ]}
            submit={(v) =>
              api.post("/guidelines", {
                ...v,
                region_id: v.level === "REGION" ? v.region_id : null,
                store_id: ["STORE", "CATEGORY"].includes(v.level)
                  ? v.store_id || null
                  : null,
                category_id: v.level === "CATEGORY" ? v.category_id : null,
              })
            }
            onDone={() => {
              setShow(false);
              value.reload();
            }}
            button="기준 등록하기"
          />
        </Panel>
      )}
      <Resource value={value}>
        {(data: Data) =>
          id ? (
            <>
              <Link className="text-link" to={"/ofc-admin/guidelines" + search}>
                ← 기준 목록
              </Link>
              <Panel title={data.title}>
                <div className="tags">
                  <Badge>{data.level}</Badge>
                  <Badge>현재 v{data.current_version}</Badge>
                  <Badge>{data.is_active ? "활성" : "비활성"}</Badge>
                </div>
                <p className="preserve lead">{data.current.text}</p>
                <p>최근 사유: {data.current.change_reason}</p>
                <small>{date(data.current.created_at)}</small>
              </Panel>
              {canEdit(data, account, scope.stores) && (
                <div className="comparison-grid">
                  <Panel>
                    <ActionForm
                      title="다음 버전 작성"
                      initial={{ title: data.title, text: data.current.text }}
                      fields={[
                        {
                          name: "title",
                          label: "제목",
                          required: true,
                          maxLength: 160,
                        },
                        {
                          name: "text",
                          label: "새 기준 내용",
                          type: "textarea",
                          required: true,
                          maxLength: 6000,
                        },
                        reason,
                      ]}
                      submit={(v) =>
                        api.post(`/guidelines/${id}/versions`, {
                          ...v,
                          version: data.version,
                        })
                      }
                      onDone={() => {
                        value.reload();
                        versions.reload();
                      }}
                      button="새 버전 저장"
                    />
                  </Panel>
                  <Panel>
                    <ActionForm
                      title={
                        data.is_active ? "이 기준 비활성화" : "이 기준 활성화"
                      }
                      fields={[reason]}
                      submit={(v) =>
                        api.patch("/guidelines/" + id, {
                          ...v,
                          version: data.version,
                          is_active: !data.is_active,
                        })
                      }
                      onDone={value.reload}
                      button={data.is_active ? "비활성화" : "활성화"}
                    >
                      <p>
                        변경 이후 새 점검에 반영됩니다. 과거 점검의 기준과
                        평가는 보존됩니다.
                      </p>
                    </ActionForm>
                  </Panel>
                </div>
              )}
              <Panel title="버전 이력">
                <Resource value={versions}>
                  {(list: Page<Data>) =>
                    list.items.map((v) => (
                      <details key={v.version_id}>
                        <summary>
                          v{v.version} · {date(v.created_at)} ·{" "}
                          {v.change_reason}
                        </summary>
                        <p className="preserve">{v.text}</p>
                      </details>
                    ))
                  }
                </Resource>
              </Panel>
            </>
          ) : (
            <>
              {data.items.length ? (
                <div className="card-grid">
                  {data.items.map((g: Data) => (
                    <article className="work-card" key={g.id}>
                      <div className="tags">
                        <Badge>{g.level}</Badge>
                        <Badge>{g.is_active ? "활성" : "비활성"}</Badge>
                        <Badge>v{g.current_version}</Badge>
                      </div>
                      <h2>
                        <Link to={"/ofc-admin/guidelines/" + g.id + search}>
                          {g.title}
                        </Link>
                      </h2>
                      <p className="clamp">{g.current.text}</p>
                      <p className="muted">{g.rule_key}</p>
                      <Link
                        className="card-action"
                        to={"/ofc-admin/guidelines/" + g.id + search}
                      >
                        내용과 버전 확인 →
                      </Link>
                    </article>
                  ))}
                </div>
              ) : (
                <Empty>
                  등록된 진열 기준이 없습니다. 사용할 범위에 맞게 첫 기준을
                  등록해 주세요.
                </Empty>
              )}
              <Pager data={data as Page<Data>} />
            </>
          )
        }
      </Resource>
    </>
  );
}
export function References({ account }: { account: AccountMe }) {
  const { search, query } = useLocation();
  const value = useResource<Page<Data>>(
    "/references" +
      listQuery(search, [
        "page",
        "page_size",
        "category_id",
        "store_id",
        "include_inactive",
      ]),
  );
  const scope = useScope(account);
  const [edit, setEdit] = useState<Data | null>(null),
    [show, setShow] = useState(false),
    [values, set] = useState<Data>({
      category_id: "",
      store_id: "",
      caption: "",
      reason: "",
    }),
    [files, setFiles] = useState<File[]>([]);
  const m = useMutation();
  const [validation, setValidation] = useState("");
  const [recovering, setRecovering] = useState(false);
  const [recoveryError, setRecoveryError] = useState<unknown>(null);
  const [recovered, setRecovered] = useState<Data | null>(null);
  const recoveryGeneration = useRef(0);
  const refreshEdit = async () => {
    if (!edit || recovering) return;
    const target = edit;
    const generation = ++recoveryGeneration.current;
    setRecovering(true);
    setRecoveryError(null);
    setRecovered(null);
    try {
      let latest: Data | undefined;
      let currentPage = 1;
      while (true) {
        const list = await api.get<Page<Data>>(
          "/references" +
            queryString({
              category_id: target.category_id,
              store_id: target.store_id,
              include_inactive: true,
              page_size: 100,
              page: currentPage,
            }),
        );
        if (generation !== recoveryGeneration.current) return;
        for (const reference of list.items) {
          if (
            reference.lineage_id === target.lineage_id &&
            (!latest ||
              reference.version > latest.version ||
              (reference.version === latest.version &&
                reference.state_version > latest.state_version))
          )
            latest = reference;
        }
        if (!list.items.length || list.page * list.page_size >= list.total)
          break;
        currentPage = list.page + 1;
      }
      if (!latest)
        throw new Error(
          "최신 Reference를 찾지 못했습니다. 입력을 유지한 채 현재 접근 범위를 확인해 주세요.",
        );
      setEdit(latest);
      setRecovered(latest);
      m.clear();
      value.reload();
    } catch (error) {
      if (generation !== recoveryGeneration.current) return;
      setRecoveryError(error);
      accessFailure(error);
    } finally {
      if (generation === recoveryGeneration.current) setRecovering(false);
    }
  };
  const begin = (r?: Data) => {
    recoveryGeneration.current += 1;
    setRecovering(false);
    setRecoveryError(null);
    setRecovered(null);
    setEdit(r ?? null);
    set({
      category_id: r?.category_id ?? "",
      store_id: r?.store_id ?? "",
      caption: r?.caption ?? "",
      reason: "",
    });
    setFiles([]);
    setShow(true);
    m.clear();
  };
  return (
    <>
      <PageTitle
        title="좋은 매대를 함께 참고해요"
        description="같은 매대 유형에서 매장 전용 Reference를 먼저 적용하고 공통 사진을 이어서 확인합니다."
        action={<button onClick={() => begin()}>+ Reference 등록</button>}
      />
      <form
        className="filters"
        onSubmit={(e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          queryPatch({
            category_id: f.get("category_id"),
            store_id: f.get("store_id"),
            include_inactive: f.get("include_inactive") ? "true" : "false",
            page: 1,
          });
        }}
      >
        <label>
          매대 유형
          <select
            name="category_id"
            defaultValue={query.get("category_id") ?? ""}
          >
            <option value="">전체</option>
            {scope.categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          매장
          <select name="store_id" defaultValue={query.get("store_id") ?? ""}>
            <option value="">전체 허용 범위</option>
            {scope.stores.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            name="include_inactive"
            defaultChecked={query.get("include_inactive") === "true"}
          />
          비활성 이력 포함
        </label>
        <button className="secondary">조건 적용</button>
      </form>
      {show && (
        <form
          className="panel"
          onSubmit={(e) => {
            e.preventDefault();
            if (!edit && !files.length) {
              setValidation("Reference 사진을 선택해 주세요.");
              return;
            }
            setValidation("");
            const metadata = edit
              ? {
                  state_version: edit.state_version,
                  caption: values.caption,
                  reason: values.reason,
                }
              : { ...values, store_id: values.store_id || null };
            void m.run(
              () =>
                api.upload(
                  edit ? "/references/" + edit.id : "/references",
                  metadata,
                  files.map((file) => ({ field: "photo", file })),
                  undefined,
                  edit ? "PATCH" : "POST",
                ),
              () => {
                value.reload();
                setShow(false);
              },
            );
          }}
        >
          <h2>{edit ? "Reference 새 버전으로 교체" : "새 Reference 등록"}</h2>
          <Fields
            fields={[
              ...(!edit
                ? [
                    {
                      name: "category_id",
                      label: "매대 유형",
                      required: true,
                      type: "select",
                      options: scope.categories,
                    },
                    {
                      name: "store_id",
                      label: "매장 (본사는 비우면 공통)",
                      required: account.role !== "hq",
                      type: "select",
                      options: scope.stores,
                    },
                  ]
                : []),
              {
                name: "caption",
                label: "이 사진에서 참고할 점",
                required: true,
                maxLength: 1000,
              },
              reason,
            ]}
            values={values}
            set={set}
          />
          <PhotoPicker files={files} set={setFiles} max={1} />
          {edit && (
            <p>
              새 사진을 선택하지 않으면 기존 사진을 보존한 새 내용 버전으로
              저장합니다.
            </p>
          )}
          {validation && <p role="alert">{validation}</p>}
          <ErrorBox
            error={m.error}
            retry={
              edit && m.error instanceof ApiError && m.error.status === 409
                ? () => void refreshEdit()
                : undefined
            }
          />
          <ErrorBox error={recoveryError} retry={() => void refreshEdit()} />
          {recovering && (
            <p role="status">현재 Reference를 다시 읽고 있어요…</p>
          )}
          {recovered && (
            <div className="notice" role="status">
              <strong>
                최신 Reference v{recovered.version}를 확인했습니다.
              </strong>
              <p>현재 서버 설명: {recovered.caption}</p>
              <p>
                작성한 설명·사유·사진을 유지했습니다. 내용을 확인하고 새 버전
                저장을 다시 눌러 주세요.
              </p>
            </div>
          )}
          <div className="actions">
            <button disabled={m.busy || recovering}>
              {m.busy
                ? "저장 중…"
                : edit
                  ? "새 버전 저장"
                  : "Reference 등록하기"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                recoveryGeneration.current += 1;
                setShow(false);
              }}
            >
              닫기
            </button>
          </div>
        </form>
      )}
      <Resource value={value}>
        {(data: Page<Data>) => (
          <>
            {data.items.length ? (
              <div className="card-grid">
                {data.items.map((r) => (
                  <article className="work-card" key={r.id}>
                    <Photos photos={[r.photo]} label="우수 매대 Reference" />
                    <div className="tags">
                      <Badge>v{r.version}</Badge>
                      <Badge>
                        {r.store_id
                          ? (scope.stores.find((s) => s.id === r.store_id)
                              ?.name ?? "매장 전용")
                          : "전사 공통"}
                      </Badge>
                      <Badge>{r.is_active ? "활성" : "비활성"}</Badge>
                    </div>
                    <h2>{r.caption}</h2>
                    <p>{date(r.created_at)}</p>
                    {(account.role === "hq" ||
                      (r.store_id &&
                        scope.stores.some((s) => s.id === r.store_id))) && (
                      <>
                        <button className="secondary" onClick={() => begin(r)}>
                          사진·설명 교체
                        </button>
                        <details>
                          <summary>
                            {r.is_active ? "비활성화" : "활성화"}
                          </summary>
                          <ActionForm
                            title="Reference 상태 변경"
                            fields={[reason]}
                            submit={(v) =>
                              api.patch(`/references/${r.id}/status`, {
                                ...v,
                                state_version: r.state_version,
                                is_active: !r.is_active,
                              })
                            }
                            onDone={value.reload}
                          />
                        </details>
                      </>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <Empty>비교할 Reference가 아직 없습니다.</Empty>
            )}
            <Pager data={data} />
          </>
        )}
      </Resource>
    </>
  );
}
