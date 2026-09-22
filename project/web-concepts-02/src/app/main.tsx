import { useEffect, useState, type ReactNode, Component } from "react";
import { createRoot, type Root } from "react-dom/client";
import type { AccountMe, Page } from "@storeloop/api-client";
import {
  api,
  ApiError,
  Badge,
  ErrorBox,
  go,
  Link,
  PageTitle,
  prefixFor,
  roles,
  safeReturn,
  type Data,
  useLocation,
  useMutation,
  useResource,
} from "../shared/core";
import { Owner } from "../store-owner/Owner";
import { Business } from "../ofc-admin/Business";
import { Operations } from "../platform-admin/Operations";
import { Issues, Notifications } from "../shared/issues";
import "./style.css";
import { hasDemoRoleTabs, loginWithDemoSessions, getInitialAccount, publicDemoAccess } from "../shared/demo-role";
const ownerMenu = [
  ["", "오늘 할 일"],
  ["/submit", "사진 점검"],
  ["/history", "점검 이력"],
  ["/issues", "확인할 일"],
  ["/notifications", "알림"],
];
const businessMenu = [
  ["", "오늘 할 일"],
  ["/stores", "담당 매장"],
  ["/submissions", "점검 이력"],
  ["/issues", "조치 관리"],
  ["/guidelines", "진열 기준"],
  ["/references", "Reference"],
  ["/analytics", "추이와 분석"],
  ["/notifications", "알림"],
];
const operationsMenu = [
  ["", "복구 할 일"],
  ["/accounts", "계정과 연결"],
  ["/catalogs", "기준 정보"],
  ["/jobs", "처리 작업"],
  ["/audit", "변경 이력"],
  ["/announcements", "운영 공지"],
];
export function App() {
  const { path, search, query } = useLocation();
  const [account, setAccount] = useState<AccountMe | null>(null),
    [checking, setChecking] = useState(true),
    [error, setError] = useState<unknown>(null),
    [epoch, setEpoch] = useState(0);
  useEffect(() => {
    let live = true;
    getInitialAccount()
      .then((a) => {
        if (live) {
          setAccount(a);
          if (path === "/" || path === "/login")
            go(safeReturn(query.get("return"), a.role), true);
        }
      })
      .catch((err) => {
        if (!live) return;
        setAccount(null);
        if (!(err instanceof ApiError && err.status === 401)) setError(err);
        if (path !== "/login")
          go("/login?return=" + encodeURIComponent(path + search), true);
      })
      .finally(() => {
        if (live) setChecking(false);
      });
    return () => {
      live = false;
    };
  }, []);
  useEffect(() => {
    const handle = (event: Event) => {
      const err = (event as CustomEvent<ApiError>).detail;
      setEpoch((x) => x + 1);
      if (err.status === 401) {
        setAccount(null);
        go(
          "/login?return=" +
            encodeURIComponent(location.pathname + location.search),
          true,
        );
      } else if (location.pathname !== "/login") {
        go("/forbidden", true);
      }
    };
    window.addEventListener("storeloop-access", handle);
    return () => window.removeEventListener("storeloop-access", handle);
  }, []);
  useEffect(() => {
    if (!account) return;
    let live = true;
    const refresh = () => {
      if (document.visibilityState === "visible")
        api
          .me()
          .then((a) => {
            if (!live) return;
            if (a.role !== account.role) {
              setEpoch((x) => x + 1);
              go(prefixFor(a.role), true);
            }
            setAccount(a);
          })
          .catch((e) => {
            if (e instanceof ApiError && [401, 403].includes(e.status)) {
              setAccount(null);
              setEpoch((x) => x + 1);
              go("/login", true);
            }
          });
    };
    document.addEventListener("visibilitychange", refresh);
    return () => {
      live = false;
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [account?.id, account?.role]);
  useEffect(() => {
    window.scrollTo({ top: 0 });
    const timer = setTimeout(
      () =>
        document
          .querySelector<HTMLElement>("main h1")
          ?.focus({ preventScroll: true }),
      80,
    );
    return () => clearTimeout(timer);
  }, [path]);
  if (checking)
    return (
      <div className="boot" role="status">
        <div className="brand-mark">↻</div>
        <p>오늘의 업무를 준비하고 있어요…</p>
      </div>
    );
  if (!account || path === "/login")
    return (
      <Login
        onLogin={(a) => {
          setAccount(a);
          setError(null);
          go(safeReturn(query.get("return"), a.role), true);
        }}
        initialError={error}
      />
    );
  const prefix = prefixFor(account.role),
    menu =
      account.role === "store_owner"
        ? ownerMenu
        : account.role === "platform_operator"
          ? operationsMenu
          : businessMenu;
  const known =
    path === prefix ||
    new RegExp(
      "^" +
        prefix +
        "/(submit|history|notifications|issues(?:/[^/]+)?|submissions(?:/[^/]+(?:/compare)?)?|stores(?:/[^/]+)?|guidelines(?:/[^/]+)?|references|analytics|accounts(?:/[^/]+)?|catalogs|jobs(?:/[^/]+)?|audit|announcements)$",
    ).test(path);
  const roleRoutes =
    account.role === "platform_operator"
      ? /^(?:accounts(?:\/[^/]+)?|catalogs|jobs(?:\/[^/]+)?|audit|announcements)$/
      : account.role === "store_owner"
        ? /^(?:submit|history|notifications|issues(?:\/[^/]+)?|submissions\/[^/]+(?:\/compare)?)$/
        : /^(?:notifications|issues(?:\/[^/]+)?|submissions(?:\/[^/]+(?:\/compare)?)?|stores(?:\/[^/]+)?|guidelines(?:\/[^/]+)?|references|analytics)$/;
  const forbidden =
    path === "/forbidden" ||
    (!path.startsWith(prefix + "/") && path !== prefix) ||
    (known &&
      path !== prefix &&
      !roleRoutes.test(path.slice(prefix.length + 1)));
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        본문으로 건너뛰기
      </a>
      <header className="app-header">
        <Link to={prefix} className="brand">
          <span className="brand-mark">↻</span>StoreLoop
          <span className="brand-caption">오늘 할 일</span>
        </Link>
        <div className="account-menu">
          {hasDemoRoleTabs(account) && <nav aria-label="역할별 새 탭">
            <a href="/store-owner" target="_blank" rel="noopener noreferrer">점주 화면</a>{" · "}
            <a href="/ofc-admin" target="_blank" rel="noopener noreferrer">영업 화면</a>{" · "}
            <a href="/platform-admin" target="_blank" rel="noopener noreferrer">운영자 화면</a>
          </nav>}
          <span>
            {account.display_name}{" "}
            <Badge tone="light">{roles[account.role]}</Badge>
          </span>
          <button
            onClick={async () => {
              try {
                await api.logout();
                setAccount(null);
                setEpoch((x) => x + 1);
                go("/login", true);
              } catch (e) {
                setError(e);
              }
            }}
          >
            로그아웃
          </button>
        </div>
      </header>
      {publicDemoAccess && account.demo_public_access_enabled && <p className="demo-public-banner" role="note">공개 시연 · 시연 데이터 사용 · 관리 기능 제한</p>}
      <nav className="primary-nav" aria-label="주요 업무">
        <div>
          {menu.map(([suffix, label]) => (
            <Link
              key={suffix}
              to={prefix + suffix}
              className={
                path === prefix + suffix ||
                (suffix && path.startsWith(prefix + suffix + "/"))
                  ? "active"
                  : ""
              }
              aria-current={path === prefix + suffix ? "page" : undefined}
            >
              {label}
            </Link>
          ))}
        </div>
      </nav>
      <main id="main" key={account.id + "-" + epoch}>
        <ErrorBox error={error} />
        <AnnouncementBar />
        {forbidden ? (
          <>
            <PageTitle
              title="이 업무에 접근할 수 없어요"
              description="현재 역할과 연결 범위를 확인해 주세요. 이전 화면의 데이터는 표시하지 않습니다."
            />
            <Link className="button" to={prefix}>
              내 업무로 돌아가기
            </Link>
          </>
        ) : !known ? (
          <>
            <PageTitle title="페이지를 찾을 수 없어요" />
            <Link to={prefix}>내 업무로 돌아가기</Link>
          </>
        ) : (
          <Boundary key={path}>
            <div key={path}>
              {path.includes("/issues") ? (
                <Issues account={account} />
              ) : path.endsWith("/notifications") ? (
                <Notifications account={account} />
              ) : account.role === "store_owner" ? (
                <Owner account={account} />
              ) : account.role === "platform_operator" ? (
                <Operations account={account} />
              ) : (
                <Business account={account} />
              )}
            </div>
          </Boundary>
        )}
      </main>
      <footer className="app-footer">
        <span>StoreLoop · 오늘 할 일</span>
        <span>작은 점검, 이어지는 개선.</span>
      </footer>
    </div>
  );
}
function Login({
  onLogin,
  initialError,
}: {
  onLogin: (a: AccountMe) => void;
  initialError: unknown;
}) {
  const [id, setId] = useState(""),
    [password, setPassword] = useState("");
  const m = useMutation();
  return (
    <main className="login-layout">
      <section className="login-story">
        <div className="brand">
          <span className="brand-mark">↻</span>StoreLoop
        </div>
        <p className="eyebrow">A LITTLE BETTER, EVERY DAY</p>
        <h2>
          오늘의 작은 점검이
          <br />
          내일의 좋은 매대로.
        </h2>
        <p>
          살펴보고, 함께 개선하고, 변화를 확인해요.
          <br />
          매장과 담당자의 다음 행동을 이어주는 StoreLoop.
        </p>
        <div className="login-flow">
          <span>
            <b>01</b> 살펴보기
          </span>
          <span>
            <b>02</b> 함께 개선
          </span>
          <span>
            <b>03</b> 변화 확인
          </span>
        </div>
        <small>CONCEPT 02 · 오늘 할 일</small>
      </section>
      <section className="login-form">
        <div className="login-card">
          <Badge>반가워요</Badge>
          <h1>오늘의 업무를 시작해요</h1>
          <p>연결된 역할과 매장 범위로 안전하게 로그인합니다.</p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void m.run(
                () => loginWithDemoSessions(id, password),
                (result) => {
                  setPassword("");
                  onLogin(result.account);
                },
              );
            }}
          >
            <label>
              로그인 ID
              <input
                name="username"
                autoComplete="username"
                required
                maxLength={80}
                value={id}
                onChange={(e) => setId(e.target.value)}
              />
            </label>
            <label>
              비밀번호
              <input
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
            <ErrorBox error={m.error || initialError} />
            <button disabled={m.busy}>
              {m.busy ? "로그인하고 있어요…" : "내 업무로 이동 →"}
            </button>
          </form>
          <p className="muted">
            계정이나 매장 연결이 필요하면 플랫폼 운영자에게 요청해 주세요.
          </p>
        </div>
      </section>
    </main>
  );
}
function AnnouncementBar() {
  const value = useResource<Page<Data>>("/announcements");
  const [hidden, setHidden] = useState<string[]>([]);
  useEffect(() => {
    window.addEventListener("announcements-refresh", value.reload);
    return () =>
      window.removeEventListener("announcements-refresh", value.reload);
  }, []);
  return (
    <>
      {value.data?.items
        .filter((a) => !hidden.includes(a.id))
        .map((a) => (
          <aside className="announcement" key={a.id}>
            <div>
              <strong>{a.title}</strong>
              <p>{a.body}</p>
            </div>
            <button
              className="text-button"
              aria-label={`${a.title} 공지 닫기`}
              onClick={() => setHidden([...hidden, a.id])}
            >
              닫기
            </button>
          </aside>
        ))}
    </>
  );
}
class Boundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <div className="notice danger" role="alert">
        <h1>화면을 표시하지 못했습니다</h1>
        <p>잠시 후 다시 불러와 주세요.</p>
        <button onClick={() => location.reload()}>페이지 다시 불러오기</button>
      </div>
    ) : (
      this.props.children
    );
  }
}
// HMR이 진입점을 다시 평가해도 같은 DOM에는 기존 React root를 재사용한다.
const rootKey = Symbol.for("storeloop.concept-02.react-root");
const container = document.getElementById("root") as (HTMLElement & { [rootKey]?: Root }) | null;
if (container) {
  const root = container[rootKey] ?? (container[rootKey] = createRoot(container));
  root.render(<App />);
}
