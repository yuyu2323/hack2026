import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / 'scripts/security_guard.py'

class SecurityGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='storeloop-security-')
        self.repo = Path(self.temp.name) / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'StoreLoop Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.env = dict(os.environ, GITLEAKS_BIN=str(ROOT / '.local/bin/gitleaks'))

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args, check=True):
        return subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, check=check)

    def guard(self, mode, data=''):
        return subprocess.run([sys.executable, str(GUARD), mode, '--repo', str(self.repo)], input=data, text=True, capture_output=True, env=self.env)

    def fixture(self):
        # 외부에서 유효하지 않은 합성 탐지 표본만 생성한다.
        return 'token = "' + 'ghp_' + 'aB3dE6gH9jK2mN5pQ8sT1vW4yZ7cF0iL3oR6' + '"\n'

    def test_clean_staged_content_passes(self):
        (self.repo / 'safe.txt').write_text('StoreLoop synthetic documentation\n')
        self.git('add', 'safe.txt')
        self.assertEqual(self.guard('staged').returncode, 0)

    def test_staged_secret_blocks_even_when_worktree_is_clean(self):
        f = self.repo / 'fixture.txt'
        f.write_text(self.fixture())
        self.git('add', 'fixture.txt')
        f.write_text('clean working tree\n')
        self.assertNotEqual(self.guard('staged').returncode, 0)

    def test_forbidden_env_file_blocks(self):
        (self.repo / '.env').write_text('LOCAL_SETTING=not-secret\n')
        self.git('add', '.env')
        self.assertNotEqual(self.guard('staged').returncode, 0)

    def test_new_branch_scan_includes_removed_secret(self):
        (self.repo / 'fixture.txt').write_text(self.fixture())
        self.git('add', 'fixture.txt')
        self.git('commit', '-qm', 'test: 합성 이력 표본')
        (self.repo / 'fixture.txt').write_text('removed synthetic fixture\n')
        self.git('add', 'fixture.txt')
        self.git('commit', '-qm', 'test: 현재 파일 정리 표본')
        sha = self.git('rev-parse', 'HEAD').stdout.decode().strip()
        result = self.guard('push', f'refs/heads/demo {sha} refs/heads/demo {"0" * 40}\n')
        self.assertNotEqual(result.returncode, 0)

    def test_missing_scanner_blocks(self):
        self.env['GITLEAKS_BIN'] = str(self.repo / 'missing')
        self.assertNotEqual(self.guard('staged').returncode, 0)

    def install_hooks(self):
        (self.repo / 'project/scripts').mkdir(parents=True)
        shutil.copy(GUARD, self.repo / 'project/scripts/security_guard.py')
        shutil.copy(ROOT / '.gitleaks.toml', self.repo / 'project/.gitleaks.toml')
        shutil.copytree(ROOT / '.githooks', self.repo / 'project/.githooks')
        self.git('config', 'core.hooksPath', 'project/.githooks')

    def test_real_precommit_hook_blocks_commit(self):
        self.install_hooks()
        (self.repo / 'fixture.txt').write_text(self.fixture())
        self.git('add', 'fixture.txt')
        result = subprocess.run(['git','-C',str(self.repo),'commit','-qm','test: 합성 차단 검증'], capture_output=True, env=self.env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self.git('rev-parse','--verify','HEAD',check=False).returncode, 0)

    def test_real_prepush_hook_blocks_local_bare_destination(self):
        (self.repo / 'fixture.txt').write_text(self.fixture())
        self.git('add','fixture.txt'); self.git('commit','-qm','test: 합성 이력 표본')
        (self.repo / 'fixture.txt').write_text('현재 내용에는 표본 없음')
        self.git('add','fixture.txt'); self.git('commit','-qm','test: 현재 표본 제거')
        self.install_hooks()
        remote = Path(self.temp.name) / 'destination.git'
        subprocess.run(['git','init','--bare','-q',str(remote)], check=True, capture_output=True)
        result = subprocess.run(['git','-C',str(self.repo),'push',str(remote),'HEAD:refs/heads/demo'], capture_output=True, env=self.env)
        self.assertNotEqual(result.returncode, 0)
        result = subprocess.run(['git','--git-dir',str(remote),'show-ref'], capture_output=True)
        self.assertEqual(result.stdout, b'')

if __name__ == '__main__':
    unittest.main()
