import { api, ApiError, createClient, type AccountMe } from "@storeloop/api-client";
export const publicDemoAccess = import.meta.env.VITE_DEMO_PUBLIC_ACCESS_ENABLED === "true";
export const demoRoleTabs = import.meta.env.VITE_DEMO_MULTI_ROLE_ENABLED === "true";
export function roleForPath(path: string): string | undefined {
  for (const [prefix, role] of [["/store-owner", "store_owner"], ["/ofc-admin", "ofc"], ["/platform-admin", "platform_operator"]]) {
    if (path === prefix || path.startsWith(prefix + "/")) return role;
  }
  return undefined;
}
const baseSessionKey = "storeloop-base-session";
export function requestRole(): string | undefined {
  try { if (sessionStorage.getItem(baseSessionKey) === "true") return undefined; } catch { /* 저장소 제한 시 기본 역할 정책 */ }
  return roleForPath(window.location.pathname);
}
if (demoRoleTabs) api.configureRoleContext(requestRole);
export async function loginWithDemoSessions(id: string, password: string) {
  const result = await api.login(id, password);
  // HQ·지역 관리자는 기존 기본 세션을 사용하며 시연 세션을 선택하지 않는다.
  try {
    if (["hq", "regional"].includes(result.account.role)) sessionStorage.setItem(baseSessionKey, "true");
    else sessionStorage.removeItem(baseSessionKey);
  } catch { /* 저장소 사용 불가 환경에서는 서버 인증이 권한을 검증한다. */ }
  if (demoRoleTabs && result.account.login_id === "operator.demo" && result.account.role === "platform_operator" && result.account.demo_multi_role_enabled) {
    await api.post("/auth/demo-sessions", {});
  }
  return result;
}
export function rolePhotoUrl(url: string): string {
  const role = demoRoleTabs ? requestRole() : undefined;
  if (!role || !url.startsWith("/api/media/")) return url;
  const target = new URL(url, window.location.origin);
  target.searchParams.set("demo_role", role);
  return target.pathname + target.search;
}
export function hasDemoRoleTabs(account: AccountMe) {
  return demoRoleTabs && account.demo_multi_role_enabled === true;
}

let initialAccountRequest: Promise<AccountMe> | undefined;
export function getInitialAccount(): Promise<AccountMe> {
  if (!initialAccountRequest) {
    initialAccountRequest = (async () => {
      try { return await api.me(); }
      catch (error) {
        if (!publicDemoAccess || !demoRoleTabs || !(error instanceof ApiError) || error.status !== 401) throw error;
        // 역할 헤더 없는 클라이언트로 익명 CSRF와 최초 시연 세션을 발급한다.
        const bootstrap = createClient();
        await bootstrap.post("/auth/demo-sessions", {});
        return api.me();
      }
    })();
    void initialAccountRequest.then(() => { initialAccountRequest = undefined; }, () => { initialAccountRequest = undefined; });
  }
  return initialAccountRequest;
}
