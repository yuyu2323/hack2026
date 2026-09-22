import { cp, mkdir, rm } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const output = new URL('../../public/', import.meta.url);
try {
  // 실패한 빌드에서 이전 배포 산출물을 재사용하지 않는다.
  await rm(output, { recursive: true, force: true });
  const npmArgs = process.env.npm_execpath ? [process.env.npm_execpath, 'run', 'build'] : ['run', 'build'];
  const build = spawnSync(process.env.npm_execpath ? process.execPath : 'npm', npmArgs, {
    cwd: root, stdio: 'inherit', env: { ...process.env, VITE_HOSTED_UPLOAD_LIMIT: 'true',
      VITE_DEMO_MULTI_ROLE_ENABLED: process.env.DEMO_MULTI_ROLE_ENABLED === 'true' ? 'true' : 'false',
      VITE_DEMO_PUBLIC_ACCESS_ENABLED: process.env.DEMO_PUBLIC_ACCESS_ENABLED === 'true' ? 'true' : 'false',
    },
  });
  if (build.error || build.status !== 0) throw new Error('프론트 빌드에 실패했습니다. 위 빌드 오류를 확인하세요.');
  await mkdir(output, { recursive: true });
  await cp(new URL('../../web-concepts-02/dist/', import.meta.url), output, { recursive: true });
  if (process.env.VERCEL_ENV === 'production') {
    const init = spawnSync('uv', ['run', 'python', '-m', 'deploy.vercel.initialize'], {
      cwd: root, stdio: 'inherit', env: process.env,
    });
    if (init.error || init.status !== 0) throw new Error('DB 초기화를 완료하지 못했습니다.');
  }
  console.log('Vercel 프론트 및 Python API 빌드 준비 완료');
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
