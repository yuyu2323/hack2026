// Sites 앞단은 앱 세션만 전달하며 호스팅 인증 쿠키는 외부 서버로 보내지 않는다.
const SESSION_COOKIE = 'storeloop_concept_02_session';
export default {
  async fetch(request, env) {
    let backend;
    try {
      backend = new URL(env.BACKEND_ORIGIN);
      if (backend.protocol !== 'https:' || backend.username || backend.password || backend.pathname !== '/' || backend.search || backend.hash) throw new Error();
    } catch {
      return new Response('배포 서버 연결 설정이 필요합니다.', { status: 503 });
    }
    const incoming = new URL(request.url);
    const target = new URL(backend.origin);
    target.pathname = incoming.pathname;
    target.search = incoming.search;
    const headers = new Headers();
    for (const name of ['accept', 'accept-language', 'content-type', 'origin', 'referer', 'sec-fetch-site', 'x-csrf-token', 'idempotency-key', 'range', 'if-none-match']) {
      const value = request.headers.get(name);
      if (value) headers.set(name, value);
    }
    const cookie = (request.headers.get('cookie') || '').split(';').map(value => value.trim()).find(value => value.startsWith(SESSION_COOKIE + '='));
    if (cookie) headers.set('cookie', cookie);
    try {
      const upstream = await fetch(target, {
        method: request.method, headers,
        body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
        redirect: 'manual',
      });
      const responseHeaders = new Headers(upstream.headers);
      // 플랫폼 인증 정보나 upstream 도메인을 캐시·이동 경로로 노출하지 않는다.
      responseHeaders.delete('server');
      if (incoming.pathname.startsWith('/api/')) responseHeaders.set('cache-control', 'no-store');
      const redirect = responseHeaders.get('location');
      if (redirect) {
        const next = new URL(redirect, backend);
        if (next.origin === backend.origin) responseHeaders.set('location', incoming.origin + next.pathname + next.search + next.hash);
      }
      return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
    } catch {
      return new Response('서비스에 연결하지 못했습니다.', { status: 502 });
    }
  },
};
