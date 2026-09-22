import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './index.mjs';

test('앱 쿠키만 전달하고 사이트 출처와 CSRF를 보존한다', async (t) => {
  let sent;
  t.mock.method(globalThis, 'fetch', async (url, init) => {
    sent = { url: String(url), ...init };
    return new Response('{}', { headers: { 'set-cookie': 'storeloop_concept_02_session=rotated; HttpOnly; Secure; Path=/' } });
  });
  const request = new Request('https://site.example/api/auth/login?next=home', {
    method: 'POST', body: '{}', headers: {
      cookie: 'hosting_private=not-for-backend; storeloop_concept_02_session=application',
      authorization: 'Bearer hosting-only', origin: 'https://site.example',
      'sec-fetch-site': 'same-origin', 'x-csrf-token': 'application-csrf', 'content-type': 'application/json',
    },
  });
  const response = await worker.fetch(request, { BACKEND_ORIGIN: 'https://backend.example' });
  assert.equal(sent.url, 'https://backend.example/api/auth/login?next=home');
  assert.equal(sent.headers.get('cookie'), 'storeloop_concept_02_session=application');
  assert.equal(sent.headers.get('authorization'), null);
  assert.equal(sent.headers.get('origin'), 'https://site.example');
  assert.equal(sent.headers.get('x-csrf-token'), 'application-csrf');
  assert.equal(sent.redirect, 'manual');
  assert.equal(response.headers.get('cache-control'), 'no-store');
  assert.match(response.headers.get('set-cookie'), /rotated/);
});

test('API 서버 미설정 시 외부 요청하지 않는다', async (t) => {
  t.mock.method(globalThis, 'fetch', () => assert.fail('외부 호출 금지'));
  for (const origin of ['', 'http://backend.example', 'https://backend.example/path', 'https://user:pass@backend.example']) {
    assert.equal((await worker.fetch(new Request('https://site.example/'), { BACKEND_ORIGIN: origin })).status, 503);
  }
});

test('브라우저가 넘긴 경로로 프록시 대상 호스트를 변경할 수 없다', async (t) => {
  t.mock.method(globalThis, 'fetch', async (url) => {
    assert.equal(url.origin, 'https://backend.example');
    return new Response('ok');
  });
  assert.equal((await worker.fetch(new Request('https://site.example//attacker.example/path'), { BACKEND_ORIGIN: 'https://backend.example' })).status, 200);
});
