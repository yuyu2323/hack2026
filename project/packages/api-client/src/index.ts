export type Role = 'store_owner' | 'ofc' | 'regional' | 'hq' | 'platform_operator';
export interface AccountMe {
  id: string; login_id: string; display_name: string; role: Role;
  region_id: string | null; is_active: boolean; version: number;
  store_ids: string[]; permissions: string[]; demo_multi_role_enabled?: boolean; demo_public_access_enabled?: boolean;
}
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }
export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string,
              public details: { field: string; message: string }[] = [], public requestId?: string) {
    super(message); this.name = 'ApiError';
  }
}
export const idempotencyKey = (): string => crypto.randomUUID();
export function queryString(values: Record<string, unknown>): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== null && value !== '') query.set(key, String(value));
  }
  return query.size ? '?' + query.toString() : '';
}

// 인증 값은 탭의 메모리에만 두고 변경 요청은 순서대로 전송한다.
export function createClient(fetcher: typeof fetch = (...args) => fetch(...args)) {
  let csrfToken: string | null = null;
  let queue: Promise<unknown> = Promise.resolve();
  let roleContext: () => string | undefined = () => undefined;
  let activeRole: string | undefined;
  function syncRole() {
    const next = roleContext();
    if (next !== activeRole) { csrfToken = null; activeRole = next; }
    return next;
  }
  const url = (path: string) => path.startsWith('/api/') ? path : '/api' + (path.startsWith('/') ? path : '/' + path);
  async function send<T>(path: string, init: RequestInit = {}): Promise<T> {
    let response: Response;
    const role = syncRole();
    const headers = { ...(init.headers instanceof Headers ? Object.fromEntries(init.headers.entries()) : Array.isArray(init.headers) ? Object.fromEntries(init.headers) : init.headers), ...(role ? { 'X-StoreLoop-Role': role } : {}) };
    try { response = await fetcher(url(path), { ...init, headers, credentials: 'same-origin' }); }
    catch { throw new ApiError(0, 'NETWORK_ERROR', '연결을 확인한 뒤 다시 시도해 주세요.'); }
    if (response.status === 204) return undefined as T;
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      if (response.status === 401 || payload?.error?.code === 'CSRF_INVALID') csrfToken = null;
      throw new ApiError(response.status, payload?.error?.code ?? 'SERVICE_UNAVAILABLE',
        payload?.error?.message ?? '요청을 처리하지 못했습니다.', payload?.error?.details ?? [],
        payload?.request_id ?? response.headers.get('X-Request-ID') ?? undefined);
    }
    return payload as T;
  }
  async function refreshCsrf() {
    const result = await send<{ csrf_token: string; expires_at: string }>('/auth/csrf');
    csrfToken = result.csrf_token;
    return result;
  }
  function serial<T>(action: () => Promise<T>): Promise<T> {
    const result = queue.then(action, action);
    queue = result.catch(() => undefined);
    return result;
  }
  function mutate<T>(method: string, path: string, body: unknown, key?: string): Promise<T> {
    return serial(async () => {
      syncRole();
      if (!csrfToken) await refreshCsrf();
      const form = body instanceof FormData;
      const headers: Record<string, string> = { 'X-CSRF-Token': csrfToken! };
      if (!form) headers['Content-Type'] = 'application/json';
      if (key) headers['Idempotency-Key'] = key;
      const result = await send<T>(path, { method, headers, body: form ? body : JSON.stringify(body) });
      // 로그인 성공 응답의 새 CSRF만 교체하고 실패한 변경을 자동 재전송하지 않는다.
      if (path.endsWith('/login') && result && typeof result === 'object' && 'csrf_token' in result) csrfToken = String(result.csrf_token);
      return result;
    });
  }
  return {
    configureRoleContext: (resolver: () => string | undefined) => { roleContext = resolver; syncRole(); },
    get: <T>(path: string) => send<T>(path),
    post: <T>(path: string, body: unknown = {}, key?: string) => mutate<T>('POST', path, body, key),
    patch: <T>(path: string, body: unknown) => mutate<T>('PATCH', path, body),
    put: <T>(path: string, body: unknown) => mutate<T>('PUT', path, body),
    upload: <T>(path: string, metadata: unknown, files: { field: string; file: File }[], key?: string, method: 'POST' | 'PATCH' = 'POST') => {
      const form = new FormData(); form.append('metadata', JSON.stringify(metadata));
      files.forEach(({ field, file }) => form.append(field, file));
      return mutate<T>(method, path, form, key);
    },
    csrf: () => serial(refreshCsrf),
    me: () => send<AccountMe>('/auth/me'),
    login: (login_id: string, password: string) => mutate<{ account: AccountMe; csrf_token: string; expires_at: string }>('POST', '/auth/login', { login_id, password }),
    logout: async () => { await mutate<void>('POST', '/auth/logout', {}); csrfToken = null; },
  };
}
export const api = createClient();
