import { afterEach, expect, test, vi } from "vitest";
import { api, type AccountMe } from "@storeloop/api-client";

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllEnvs(); sessionStorage.clear(); api.configureRoleContext(() => undefined); });
async function demoModule(enabled = true) {
  vi.stubEnv("VITE_DEMO_MULTI_ROLE_ENABLED", enabled ? "true" : "false");
  vi.resetModules();
  return import("../src/shared/demo-role");
}
test("path matching is bounded and photo variants retain role selector", async () => {
  const module = await demoModule();
  history.replaceState({}, "", "/store-owner/history");
  expect(module.roleForPath("/store-owner/history")).toBe("store_owner");
  expect(module.roleForPath("/store-ownerevil")).toBeUndefined();
  expect(module.roleForPath("/login")).toBeUndefined();
  expect(module.rolePhotoUrl("/api/media/test?variant=thumbnail")).toBe("/api/media/test?variant=thumbnail&demo_role=store_owner");
  expect(module.rolePhotoUrl("https://outside.example/image")).toBe("https://outside.example/image");
});
test("role links require server and build opt-in", async () => {
  let module = await demoModule();
  expect(module.hasDemoRoleTabs({ demo_multi_role_enabled: true } as AccountMe)).toBe(true);
  expect(module.hasDemoRoleTabs({} as AccountMe)).toBe(false);
  module = await demoModule(false);
  expect(module.hasDemoRoleTabs({ demo_multi_role_enabled: true } as AccountMe)).toBe(false);
});
test("operator demo login alone bootstraps extra sessions", async () => {
  const module = await demoModule();
  const { api: currentApi } = await import("@storeloop/api-client");
  const login = vi.spyOn(currentApi, "login").mockResolvedValue({ account: { login_id: "operator.demo", role: "platform_operator", demo_multi_role_enabled: true } as AccountMe, csrf_token: "test", expires_at: "" });
  const post = vi.spyOn(currentApi, "post").mockResolvedValue({});
  await module.loginWithDemoSessions("operator.demo", "test");
  expect(post).toHaveBeenCalledWith("/auth/demo-sessions", {});
  post.mockClear();
  login.mockResolvedValue({ account: { login_id: "owner.north", role: "store_owner", demo_multi_role_enabled: true } as AccountMe, csrf_token: "test", expires_at: "" });
  await module.loginWithDemoSessions("owner.north", "test");
  expect(post).not.toHaveBeenCalled();
});


test("public startup only bootstraps after 401 and uses an unscoped client", async () => {
  vi.stubEnv("VITE_DEMO_PUBLIC_ACCESS_ENABLED", "true");
  const module = await demoModule();
  const { api: currentApi, ApiError } = await import("@storeloop/api-client");
  const account = { role: "store_owner" } as AccountMe;
  const me = vi.spyOn(currentApi, "me").mockRejectedValueOnce(new ApiError(401, "UNAUTHENTICATED", "test")).mockResolvedValue(account);
  const fetcher = vi.spyOn(globalThis, "fetch").mockImplementation(async (url, init) => {
    expect(new Headers(init?.headers).has("X-StoreLoop-Role")).toBe(false);
    if (String(url).endsWith("/csrf")) return Response.json({ csrf_token: "anonymous-test", expires_at: "" });
    expect(new Headers(init?.headers).get("X-CSRF-Token")).toBe("anonymous-test");
    return Response.json({});
  });
  expect(await module.getInitialAccount()).toBe(account);
  expect(me).toHaveBeenCalledTimes(2);
  expect(fetcher).toHaveBeenCalledTimes(2);
  fetcher.mockClear();
  expect(await module.getInitialAccount()).toBe(account);
  expect(fetcher).not.toHaveBeenCalled();
});
test("public startup does not bootstrap forbidden or unavailable accounts", async () => {
  vi.stubEnv("VITE_DEMO_PUBLIC_ACCESS_ENABLED", "true");
  const module = await demoModule();
  const { api: currentApi, ApiError } = await import("@storeloop/api-client");
  vi.spyOn(currentApi, "me").mockRejectedValue(new ApiError(403, "FORBIDDEN", "test"));
  const fetcher = vi.spyOn(globalThis, "fetch");
  await expect(module.getInitialAccount()).rejects.toMatchObject({ status: 403 });
  expect(fetcher).not.toHaveBeenCalled();
});


test("HQ and regional logins retain the base session in their tab", async () => {
  const module = await demoModule();
  const { api: currentApi } = await import("@storeloop/api-client");
  const login = vi.spyOn(currentApi, "login").mockResolvedValue({ account: { login_id: "hq.demo", role: "hq" } as AccountMe, csrf_token: "test", expires_at: "" });
  await module.loginWithDemoSessions("hq.demo", "test");
  history.replaceState({}, "", "/ofc-admin");
  expect(module.requestRole()).toBeUndefined();
  expect(module.rolePhotoUrl("/api/media/test")).toBe("/api/media/test");
  login.mockResolvedValue({ account: { login_id: "ofc.north", role: "ofc" } as AccountMe, csrf_token: "test", expires_at: "" });
  await module.loginWithDemoSessions("ofc.north", "test");
  expect(module.requestRole()).toBe("ofc");
});
