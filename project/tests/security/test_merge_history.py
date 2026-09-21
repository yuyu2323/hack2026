"""merge에서만 도입·제거된 금지자료도 전체 전송 이력 검사에 포함한다."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
GUARD=ROOT/'scripts/security_guard.py'

class MergeHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='storeloop-merge-review-')
        self.repo=Path(self.temp.name)/'repo'
        self.repo.mkdir()
        self.git('init','-q','-b','main')
        self.git('config','user.name','Independent Security Fixture')
        self.git('config','user.email','fixture@example.invalid')
        self.git('config','commit.gpgsign','false')
        self.env=dict(os.environ,GITLEAKS_BIN=str(ROOT/'.local/bin/gitleaks'))

    def tearDown(self):
        self.temp.cleanup()

    def git(self,*args):
        return subprocess.run(['git','-C',str(self.repo),*args],capture_output=True,check=True)

    def commit_file(self,path,text):
        (self.repo/path).write_text(text)
        self.git('add',path)
        self.git('commit','-qm','test: 합성 분기 기록')

    def merge_only_history(self,path,content):
        self.commit_file('base.txt','base\n')
        self.git('checkout','-qb','side-one')
        self.commit_file('side-one.txt','side\n')
        self.git('checkout','-q','main')
        self.commit_file('main-one.txt','main\n')
        self.git('merge','--no-commit','--no-ff','side-one')
        (self.repo/path).write_text(content)
        self.git('add',path)
        self.git('commit','-qm','test: merge에만 합성 표본 도입')
        self.git('checkout','-qb','side-two')
        self.commit_file('side-two.txt','side two\n')
        self.git('checkout','-q','main')
        self.commit_file('main-two.txt','main two\n')
        self.git('merge','--no-commit','--no-ff','side-two')
        self.git('rm',path)
        self.git('commit','-qm','test: merge에서 합성 표본 제거')
        self.assertFalse((self.repo/path).exists())
        sha=self.git('rev-parse','HEAD').stdout.decode().strip()
        return subprocess.run([sys.executable,str(GUARD),'push','--repo',str(self.repo)],
            input=f'refs/heads/demo {sha} refs/heads/demo {"0"*40}\n',
            text=True,capture_output=True,env=self.env)

    def test_forbidden_path_introduced_and_removed_only_by_merges_blocks(self):
        result=self.merge_only_history('.env','LOCAL_SETTING=external-invalid-synthetic\n')
        self.assertNotEqual(result.returncode,0,'merge 금지 경로 검사가 전송을 차단해야 합니다.')

    def test_secret_introduced_and_removed_only_by_merges_blocks(self):
        # 외부 서비스에서 유효하지 않은 합성 탐지 표본만 사용한다.
        fixture='token = "'+'ghp_'+'aB3dE6gH9jK2mN5pQ8sT1vW4yZ7cF0iL3oR6'+'"\n'
        result=self.merge_only_history('fixture.txt',fixture)
        self.assertNotEqual(result.returncode,0,'merge의 합성 비밀 검사가 전송을 차단해야 합니다.')

if __name__=='__main__':
    unittest.main()
