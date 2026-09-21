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
