import test from 'node:test';
import assert from 'node:assert/strict';
import { deploymentConfig } from './config.mjs';

test('잘못된 origin과 인증정보를 거부하며 입력 비밀을 오류에 노출하지 않는다', () => {
  for (const value of [undefined, '', 'http://backend.example.com', 'https://backend.example.com/api',
    'https://name:secret@backend.example.com', 'https://backend.example.com/?token=secret',
    'https://backend.example.com/#secret', 'https://localhost', 'https://127.0.0.1']) {
    assert.throws(() => deploymentConfig(value), error => !error.message.includes('secret') && error.message.includes('BACKEND_ORIGIN'));
  }
});
test('API 경로와 캡처값을 고정 upstream으로 전달하고 모든 메서드를 허용한다', () => {
  const api = deploymentConfig('https://backend.example.com/').routes[0];
  for (const path of ['/api/auth/login', '/api/submissions', '/api/media/123']) {
    assert.equal(path.replace(new RegExp(api.src), api.dest), 'https://backend.example.com' + path);
  }
  assert.equal(new RegExp(api.src).test('/apiary'), false);
  assert.equal(new RegExp(api.src).test('/store-owner'), false);
  assert.equal(api.methods, undefined);
  assert.equal(api.headers['Vercel-CDN-Cache-Control'], 'no-store');
});
test('정적 파일 확인 후 누락된 asset은 404, 역할 화면은 SPA로 연결한다', () => {
  const routes = deploymentConfig('https://backend.example.com').routes;
  assert.deepEqual(routes[1], { handle: 'filesystem' });
  assert.equal(routes[2].status, 404);
  for (const path of ['/login', '/store-owner', '/ofc-admin/guidelines/123', '/platform-admin']) {
    assert.equal(new RegExp(routes[2].src).test(path), false);
    assert.equal(path.replace(new RegExp(routes[3].src), routes[3].dest), '/index.html');
  }
  assert.deepEqual(routes[3].methods, ['GET', 'HEAD']);
});
