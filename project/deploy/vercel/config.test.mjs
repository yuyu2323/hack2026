import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
const root = new URL('../../', import.meta.url);
const config = JSON.parse(await readFile(new URL('vercel.json', root), 'utf8'));
test('FastAPI 진입점과 분석 제한 시간', async () => {
  assert.equal(config.framework, 'fastapi');
  assert.ok(config.functions['index.py'].maxDuration >= 150);
  assert.equal(config.buildCommand, 'npm run build:vercel');
  assert.equal(config.outputDirectory, undefined);
  const entry = await readFile(new URL('index.py', root), 'utf8');
  assert.match(entry, /from server.main import app/);
  assert.doesNotMatch(entry, /app.main|internal\/analyze/);
});
test('역할 화면만 SPA로 연결하고 API는 Python으로 처리', () => {
  const sources = config.rewrites.map(row => row.source);
  for (const path of ['/', '/login', '/forbidden', '/store-owner/:path*', '/ofc-admin/:path*', '/platform-admin/:path*']) assert.ok(sources.includes(path));
  for (const row of config.rewrites) {
    assert.equal(row.destination, '/index.html');
    assert.ok(!row.source.startsWith('/api') && !row.source.startsWith('/internal'));
  }
});
test('비밀 파일은 제외하고 프론트 출력만 정적 복사', async () => {
  const ignored = await readFile(new URL('.vercelignore', root), 'utf8');
  for (const item of ['.local/', '**/.local/', '.env', '**/.env', '**/.venv/']) assert.ok(ignored.split(/\r?\n/).includes(item));
  const build = await readFile(new URL('deploy/vercel/build.mjs', root), 'utf8');
  assert.match(build, /web-concepts-02\/dist\//);
  assert.match(build, /VERCEL_ENV === 'production'/);
  assert.doesNotMatch(build, /BACKEND_ORIGIN/);
});
