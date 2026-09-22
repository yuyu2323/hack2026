import { cp, mkdir, rm, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { deploymentConfig } from './config.mjs';

const root = fileURLToPath(new URL('../../', import.meta.url));
const output = new URL('../../.vercel/output/', import.meta.url);
try {
  // 실패한 빌드에서 이전 배포 산출물을 재사용하지 않는다.
  await rm(output, { recursive: true, force: true });
  const config = deploymentConfig(process.env.BACKEND_ORIGIN);
  const build = spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['run', 'build'], {
    cwd: root, stdio: 'inherit', env: process.env,
  });
  if (build.error || build.status !== 0) throw new Error('프론트 빌드에 실패했습니다. 위 빌드 오류를 확인하세요.');
  await mkdir(output, { recursive: true });
  await cp(new URL('../../web-concepts-02/dist/', import.meta.url), new URL('static/', output), { recursive: true });
  await writeFile(new URL('config.json', output), JSON.stringify(config, null, 2) + '\n');
  console.log('Vercel 배포 산출물 생성 완료: .vercel/output');
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
