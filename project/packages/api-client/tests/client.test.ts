import test from 'node:test';
import assert from 'node:assert/strict';
import { createClient, ApiError, queryString } from '../src/index.ts';

test('실패한 변경을 자동 재송신하지 않고 다음 명시 요청에서 CSRF를 갱신한다', async () => {
  const calls: string[] = [];
  let failure = true;
  const api = createClient(async (url, init) => {
    calls.push(String(url));
    if (String(url).endsWith('/csrf')) return Response.json({ csrf_token: 'test-only-csrf', expires_at: '' });
    if (failure) { failure = false; return Response.json({ error: { code: 'CSRF_INVALID', message: '갱신 필요' } }, { status: 403 }); }
    assert.equal((init?.headers as Record<string,string>)['Idempotency-Key'], 'same-test-key');
    return Response.json({ id: 'created' });
  });
  await assert.rejects(api.post('/issues', {}, 'same-test-key'), (error: ApiError) => error.code === 'CSRF_INVALID');
  assert.equal(calls.length, 2);
  assert.deepEqual(await api.post('/issues', {}, 'same-test-key'), { id: 'created' });
  assert.deepEqual(calls, ['/api/auth/csrf','/api/issues','/api/auth/csrf','/api/issues']);
});

test('필터의 false와0을 보존하며 빈 값만 생략한다', () => {
  assert.equal(queryString({ is_active: false, page: 0, q: '', category_id: null }), '?is_active=false&page=0');
});


test('역할별 헤더는 me와 CSRF 및 변경 요청에 적용하고 역할 변경 시 CSRF를 비운다', async () => {
  const calls: { path: string; headers: Record<string,string> }[] = [];
  let role: string | undefined = 'store_owner';
  const client = createClient(async (url, init) => {
    calls.push({ path: String(url), headers: init?.headers as Record<string,string> });
    if (String(url).endsWith('/csrf')) return Response.json({ csrf_token: 'csrf-' + role, expires_at: '' });
    return Response.json({ ok: true });
  });
  client.configureRoleContext(() => role);
  await client.me();
  await client.post('/issues', {});
  role = 'ofc';
  await client.post('/issues', {});
  role = undefined;
  await client.login('operator.demo', 'test-only');
  assert.deepEqual(calls.map(c => c.headers['X-StoreLoop-Role']), ['store_owner','store_owner','store_owner','ofc','ofc',undefined,undefined]);
  assert.equal(calls[2].headers['X-CSRF-Token'], 'csrf-store_owner');
  assert.equal(calls[4].headers['X-CSRF-Token'], 'csrf-ofc');
  assert.equal(calls[5].path, '/api/auth/csrf');
});
