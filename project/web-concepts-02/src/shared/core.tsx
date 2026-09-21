import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
  type FormEvent,
} from "react";
import {
  api,
  idempotencyKey,
  ApiError,
  queryString,
  type AccountMe,
  type Page,
} from "@storeloop/api-client";
export { api, ApiError, queryString };
export type Data = Record<string, any>;
export const roles: Record<string, string> = {
  store_owner: "점주",
  ofc: "OFC",
  regional: "지역 관리자",
  hq: "본사",
  platform_operator: "플랫폼 운영자",
};
export const prefixFor = (role: string) =>
  role === "store_owner"
    ? "/store-owner"
    : role === "platform_operator"
      ? "/platform-admin"
      : "/ofc-admin";
export function safeReturn(target: string | null, role: string) {
  const fallback = prefixFor(role);
  if (
    !target ||
    !target.startsWith("/") ||
    target.startsWith("//") ||
    target.includes("\\")
  )
    return fallback;
  try {
    const normalized = new URL(target, "http://storeloop.local");
    return normalized.origin === "http://storeloop.local" &&
      (normalized.pathname === fallback ||
        normalized.pathname.startsWith(fallback + "/"))
      ? normalized.pathname + normalized.search
      : fallback;
  } catch {
    return fallback;
  }
}
export const rate = (value: number | null | undefined) =>
  value == null
    ? "—"
    : `${value.toLocaleString("ko-KR", { maximumFractionDigits: 1 })}%`;
export const date = (value?: string | null) =>
  value
    ? new Date(value).toLocaleString("ko-KR", {
        timeZone: "Asia/Seoul",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";
export function go(to: string, replace = false) {
  if (replace) history.replaceState({}, "", to);
  else history.pushState({}, "", to);
  window.dispatchEvent(new PopStateEvent("popstate"));
}
export function Link({
  to,
  children,
  className,
  ...rest
}: {
  to: string;
  children: ReactNode;
  className?: string;
  [key: string]: any;
}) {
  return (
    <a
      href={to}
      className={className}
      {...rest}
      onClick={(e) => {
        if (!e.ctrlKey && !e.metaKey && !e.shiftKey) {
          e.preventDefault();
          go(to);
        }
      }}
    >
      {children}
    </a>
  );
}
export function useLocation() {
  const [location, set] = useState(() => locationValue());
  useEffect(() => {
    const update = () => set(locationValue());
    window.addEventListener("popstate", update);
    return () => window.removeEventListener("popstate", update);
  }, []);
  return location;
}
function locationValue() {
  return {
    path: window.location.pathname,
    search: window.location.search,
    query: new URLSearchParams(window.location.search),
  };
}
export function queryPatch(values: Data) {
  const q = new URLSearchParams(location.search);
  Object.entries(values).forEach(([key, value]) => {
    if (value === "" || value == null) q.delete(key);
    else q.set(key, String(value));
  });
  go(location.pathname + (q.size ? "?" + q : ""));
}
function isAccessRevoked(error: unknown): error is ApiError {
  return (
    error instanceof ApiError &&
    error.code !== "CSRF_INVALID" &&
    [401, 403, 404].includes(error.status)
  );
}
export function accessFailure(error: unknown) {
  if (isAccessRevoked(error))
    window.dispatchEvent(
      new CustomEvent("storeloop-access", { detail: error }),
    );
}
export function useResource<T = Data>(path: string | null, polling = false) {
  const [data, setData] = useState<T | null>(null),
    [error, setError] = useState<unknown>(null),
    [loading, setLoading] = useState(true),
    [revision, setRevision] = useState(0);
  const saved = useRef<string | null>(path);
  const reload = useCallback(() => setRevision((v) => v + 1), []);
  useEffect(() => {
    let live = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    if (saved.current !== path) {
      setData(null);
      saved.current = path;
    }
    if (!path) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const fetchData = async () => {
      try {
        const next = await api.get<T>(path);
        if (!live) return;
        setData(next);
        setError(null);
        if (
          polling &&
          ["queued", "running"].includes(
            (next as Data)?.job?.status ?? (next as Data)?.status,
          )
        )
          timer = setTimeout(fetchData, 2000);
      } catch (err) {
        if (!live) return;
        setError(err);
        if (isAccessRevoked(err)) {
          setData(null);
          accessFailure(err);
        }
      } finally {
        if (live) setLoading(false);
      }
    };
    const visible = () => {
      if (document.visibilityState === "visible") {
        if (timer) clearTimeout(timer);
        void fetchData();
      }
    };
    const refresh = () => {
      if (timer) clearTimeout(timer);
      setLoading(true);
      void fetchData();
    };
    window.addEventListener("storeloop-refresh", refresh);
    void fetchData();
    if (polling) document.addEventListener("visibilitychange", visible);
    return () => {
      live = false;
      window.removeEventListener("storeloop-refresh", refresh);
      if (timer) clearTimeout(timer);
      document.removeEventListener("visibilitychange", visible);
    };
  }, [path, revision, polling]);
  return { data, error, loading, reload };
}
export function ErrorBox({
  error,
  retry,
}: {
  error: unknown;
  retry?: () => void;
}) {
  if (!error) return null;
  const e = error as ApiError;
  return (
    <div className="notice danger" role="alert">
      <strong>{e.message || "요청을 처리하지 못했습니다."}</strong>
      {e.details?.map((x, i) => (
        <p key={i}>
          {x.field}: {x.message}
        </p>
      ))}
      {e.requestId && <small>요청 번호 {e.requestId}</small>}
      {e.code === "CSRF_INVALID" && (
        <p>
          입력한 내용과 사진을 유지했습니다. 저장·제출 버튼을 다시 누르면 보안
          확인을 갱신한 뒤 재전송합니다.
        </p>
      )}
      {e.status === 409 && (
        <p>
          다른 변경이 먼저 저장되었습니다. 입력 내용을 확인한 뒤 최신 정보를
          다시 읽어 주세요.
        </p>
      )}
      {e.status === 409 && !retry && (
        <button
          type="button"
          className="secondary"
          onClick={() => window.dispatchEvent(new Event("storeloop-refresh"))}
        >
          최신 정보 다시 읽기
        </button>
      )}
      {retry && (
        <button type="button" className="secondary" onClick={retry}>
          {e.status === 409 ? "최신 정보 다시 읽기" : "상태를 다시 확인"}
        </button>
      )}
    </div>
  );
}
export function Resource({
  value,
  children,
}: {
  value: ReturnType<typeof useResource<any>>;
  children: (data: any) => ReactNode;
}) {
  return (
    <>
      <ErrorBox error={value.error} retry={value.reload} />
      {value.loading && (
        <p className="loading" role="status">
          {value.data ? "내용을 갱신하고 있어요…" : "불러오고 있어요…"}
        </p>
      )}
      {value.data && children(value.data)}
    </>
  );
}
export function Empty({
  children = "조건에 맞는 항목이 없습니다.",
}: {
  children?: ReactNode;
}) {
  return (
    <div className="empty">
      <span className="empty-icon">✓</span>
      <p>{children}</p>
      <button className="secondary" onClick={() => go(location.pathname)}>
        필터 초기화
      </button>
    </div>
  );
}
export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={"badge " + tone}>{children}</span>;
}
export const statuses: Record<string, string> = {
  queued: "분석 대기",
  running: "분석 중",
  succeeded: "분석 완료",
  failed: "기술 실패",
  pass: "준수",
  fail: "개선 필요",
  unknown: "판단 불가",
  open: "검토 대기",
  in_progress: "조치 중",
  resolved: "완료",
  not_submitted: "미제출",
  needs_attention: "확인 필요",
  processing: "처리 중",
  technical_failure: "기술 실패",
  unassessable: "판단 불가",
  evaluated: "평가 완료",
  high: "높음",
  medium: "보통",
  low: "낮음",
  normal: "보통",
  urgent: "긴급",
  similar: "유사",
  different: "차이 있음",
  resolved_change: "개선됨",
  regressed: "악화",
  unchanged: "변화 없음",
  unavailable: "비교 불가",
  ready: "연결 정상",
  missing: "연결 누락",
  invalid: "연결 확인 필요",
};
export function Status({ value }: { value: string }) {
  return (
    <Badge
      tone={
        [
          "pass",
          "succeeded",
          "resolved",
          "evaluated",
          "ready",
          "available",
          "healthy",
        ].includes(value)
          ? "good"
          : [
                "fail",
                "failed",
                "open",
                "needs_attention",
                "technical_failure",
                "urgent",
                "missing",
                "invalid",
                "unavailable",
              ].includes(value)
            ? "warn"
            : "neutral"
      }
    >
      {statuses[value] ?? value}
    </Badge>
  );
}
export function Source({ value }: { value?: string }) {
  return value === "mock" ? (
    <Badge tone="mock">Mock 데이터</Badge>
  ) : value === "real_ai" ? (
    <Badge tone="good">실제 AI 분석</Badge>
  ) : value === "ai_generated_demo" ? (
    <Badge tone="mock">AI 생성 시연 이미지</Badge>
  ) : null;
}
export function PageTitle({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <header className="page-title">
      <div>
        <p className="eyebrow">{eyebrow || "TODAY’S WORK"}</p>
        <h1 tabIndex={-1}>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </header>
  );
}
export function Panel({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={"panel " + className}>
      {title && <h2>{title}</h2>}
      {children}
    </section>
  );
}
export function Lane({
  step,
  title,
  caption,
  children,
}: {
  step: string;
  title: string;
  caption: string;
  children: ReactNode;
}) {
  return (
    <section className="lane">
      <header>
        <span className="step">{step}</span>
        <div>
          <h2>{title}</h2>
          <p>{caption}</p>
        </div>
      </header>
      <div className="lane-body">{children}</div>
    </section>
  );
}
export function Pager({ data }: { data: Page<any> }) {
  return (
    <nav className="pager" aria-label="목록 페이지">
      <button
        className="secondary"
        disabled={data.page <= 1}
        onClick={() => queryPatch({ page: data.page - 1 })}
      >
        이전
      </button>
      <span>
        {data.page} / {Math.max(1, Math.ceil(data.total / data.page_size))} ·
        전체 {data.total}건
      </span>
      <button
        className="secondary"
        disabled={data.page * data.page_size >= data.total}
        onClick={() => queryPatch({ page: data.page + 1 })}
      >
        다음
      </button>
    </nav>
  );
}
export function useMutation() {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>(null),
    [success, setSuccess] = useState("");
  const run = async <T,>(
    action: () => Promise<T>,
    done?: (result: T) => void,
  ) => {
    if (busy) return;
    setBusy(true);
    setError(null);
    setSuccess("");
    try {
      const result = await action();
      setSuccess("변경을 저장했습니다.");
      done?.(result);
      return result;
    } catch (err) {
      setError(err);
      accessFailure(err);
    } finally {
      setBusy(false);
    }
  };
  return {
    busy,
    error,
    success,
    run,
    clear: () => {
      setError(null);
      setSuccess("");
    },
  };
}
export type Field = {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
  options?: Data[];
  hint?: string;
  maxLength?: number;
  minLength?: number;
  value?: any;
  disabled?: boolean;
};
export function Fields({
  fields,
  values,
  set,
}: {
  fields: Field[];
  values: Data;
  set: (value: Data) => void;
}) {
  return (
    <div className="fields">
      {fields.map((field) => (
        <label
          key={field.name}
          className={field.type === "textarea" ? "wide" : ""}
        >
          <span>
            {field.label}
            {field.required ? " *" : ""}
          </span>
          {field.type === "select" ? (
            <select
              required={field.required}
              disabled={field.disabled}
              value={values[field.name] ?? ""}
              onChange={(e) => set({ ...values, [field.name]: e.target.value })}
            >
              <option value="">선택하세요</option>
              {field.options?.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
            </select>
          ) : field.type === "textarea" ? (
            <textarea
              rows={4}
              required={field.required}
              maxLength={field.maxLength}
              value={values[field.name] ?? ""}
              onChange={(e) => set({ ...values, [field.name]: e.target.value })}
            />
          ) : (
            <input
              type={field.type || "text"}
              required={field.required}
              maxLength={field.maxLength}
              minLength={field.minLength}
              disabled={field.disabled}
              autoComplete={
                field.type === "password" ? "new-password" : undefined
              }
              value={values[field.name] ?? ""}
              onChange={(e) => set({ ...values, [field.name]: e.target.value })}
            />
          )}{" "}
          {field.hint && <small>{field.hint}</small>}
        </label>
      ))}
    </div>
  );
}
export function ActionForm({
  title,
  fields,
  initial = {},
  submit,
  button = "변경 저장",
  onDone,
  children,
}: {
  title: string;
  fields: Field[];
  initial?: Data;
  submit: (values: Data) => Promise<any>;
  button?: string;
  onDone?: (result: any) => void;
  children?: ReactNode;
}) {
  const [values, set] = useState<Data>(initial);
  const m = useMutation();
  return (
    <form
      className="action-form"
      onSubmit={(e: FormEvent) => {
        e.preventDefault();
        void m.run(() => submit(values), onDone);
      }}
    >
      <h3>{title}</h3>
      {children}
      <Fields fields={fields} values={values} set={set} />
      <ErrorBox error={m.error} />
      {m.success && (
        <p role="status" className="success">
          {m.success}
        </p>
      )}
      <button disabled={m.busy}>{m.busy ? "저장 중…" : button}</button>
    </form>
  );
}
export function FilterBar({
  account,
  extra = [],
}: {
  account?: AccountMe;
  extra?: Field[];
}) {
  const { query } = useLocation();
  const queryValues = Object.fromEntries(query.entries());
  const [values, set] = useState<Data>(queryValues);
  useEffect(() => set(Object.fromEntries(query.entries())), [query.toString()]);
  const op = account?.role === "platform_operator";
  const stores = useResource<Page<Data>>(!op ? "/stores?page_size=100" : null);
  const categories = useResource<Page<Data>>(
    !op ? "/categories?page_size=100" : null,
  );
  const regions = useResource<Page<Data>>(
    account && ["hq", "regional", "ofc"].includes(account.role)
      ? "/regions?page_size=100"
      : null,
  );
  const fields: Field[] = op
    ? extra
    : [
        ...(regions.data
          ? [
              {
                name: "region_id",
                label: "지역",
                type: "select",
                options: regions.data.items,
              },
            ]
          : []),
        {
          name: "store_id",
          label: "매장",
          type: "select",
          options: stores.data?.items,
        },
        {
          name: "category_id",
          label: "매대 유형",
          type: "select",
          options: categories.data?.items,
        },
        { name: "date_from", label: "시작일 (UTC)", type: "date" },
        { name: "date_to", label: "종료일 (UTC)", type: "date" },
        ...extra,
      ];
  return (
    <form
      className="filters"
      onSubmit={(e) => {
        e.preventDefault();
        queryPatch({ ...values, page: 1 });
      }}
    >
      <Fields fields={fields} values={values} set={set} />
      <div className="actions">
        <button className="secondary">조건 적용</button>
        <button
          type="button"
          className="text-button"
          onClick={() => go(location.pathname)}
        >
          초기화
        </button>
      </div>
    </form>
  );
}
export function listQuery(search: string, allowed?: string[]) {
  const q = new URLSearchParams(search);
  if (allowed)
    for (const key of [...q.keys()]) if (!allowed.includes(key)) q.delete(key);
  if (!q.has("page_size")) q.set("page_size", "20");
  return "?" + q;
}
export const businessKeys = [
  "region_id",
  "store_id",
  "category_id",
  "date_from",
  "date_to",
  "is_active",
];
export function businessQuery(search: string) {
  const q = new URLSearchParams(search);
  for (const key of [...q.keys()])
    if (!businessKeys.includes(key)) q.delete(key);
  return q.size ? "?" + q : "";
}

// 같은 대상·본문의 명시적 재시도에는 같은 키를 사용한다.
export function useRequestKey() {
  const keys = useRef(new Map<string, string>());
  return {
    get: (target: string, body: unknown) => {
      const signature = target + JSON.stringify(body);
      let key = keys.current.get(signature);
      if (!key) {
        key = idempotencyKey();
        keys.current.set(signature, key);
      }
      return key;
    },
    clear: () => keys.current.clear(),
  };
}
