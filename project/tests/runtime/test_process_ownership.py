"""start가 구성한 API/worker 명령의 macOS 소유권 독립 회귀."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import services


class StartCommandOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='storeloop-owned-command-')
        self.root = Path(self.temporary.name).resolve()
        self.local = self.root / '.local'
        (self.local / 'pids').mkdir(parents=True)
        self.patches = [patch.object(services, 'ROOT', self.root), patch.object(services, 'LOCAL', self.local)]
        for item in self.patches:
            item.start()
        self.commands = {}

        def capture(name, command, marker, port=None, cwd=None):
            self.commands[name] = (command, marker)

        # 기동/건강확인/포트 접근 없이 제품 start의 실제 명령 구성만 수집한다.
        with patch.object(services, 'prepare'), patch.object(services, 'require_available_port'), \
                patch.object(services, 'healthy', return_value=True), patch.object(services, 'launch', side_effect=capture):
            services.start([1], False)

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temporary.cleanup()

    def ps_command(self, name):
        command, _ = self.commands[name]
        # 실제 /tmp 재현에서 확인한 macOS Framework Python의 argv[0] 변환이다.
        interpreter = '/Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/MacOS/Python'
        return interpreter + ' ' + ' '.join(command[1:])

    def assert_owned(self, name):
        _, marker = self.commands[name]
        result = subprocess.CompletedProcess([], 0, stdout=self.ps_command(name), stderr='')
        with patch.object(services.subprocess, 'run', return_value=result):
            self.assertTrue(services.alive(90001, marker), name + ': start 명령의 프로젝트 식별 경로가 사라졌습니다.')

    def test_api_command_survives_framework_interpreter_name(self):
        self.assert_owned('api')

    def test_worker_command_survives_framework_interpreter_name(self):
        self.assert_owned('worker')

    def test_stop_signals_owned_api_and_worker_before_removing_records(self):
        names = {90001: 'api', 90002: 'worker'}
        for pid, name in names.items():
            (_, marker) = self.commands[name]
            (self.local / 'pids' / (name + '.json')).write_text(json.dumps({'pid': pid, 'name': name, 'marker': marker}))

        def result(command, **kwargs):
            return subprocess.CompletedProcess([], 0, stdout=self.ps_command(names[int(command[2])]), stderr='')

        with patch.object(services.subprocess, 'run', side_effect=result), patch.object(services.os, 'killpg') as kill:
            services.stop()
            self.assertEqual({call.args[0] for call in kill.call_args_list}, set(names))
        self.assertEqual(list((self.local / 'pids').glob('*.json')), [])

    def test_same_role_from_another_project_is_not_owned(self):
        (_, marker) = self.commands['api']
        foreign = self.ps_command('api').replace(str(self.root), '/unrelated/other-project')
        result = subprocess.CompletedProcess([], 0, stdout=foreign, stderr='')
        with patch.object(services.subprocess, 'run', return_value=result):
            self.assertFalse(services.alive(90003, marker))


if __name__ == '__main__':
    unittest.main()
