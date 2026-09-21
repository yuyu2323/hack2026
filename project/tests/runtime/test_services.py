"""실행 도우미가 다른 DB의 미관리 서비스를 섞지 않는지 확인한다."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import services

class ServiceOwnershipTests(unittest.TestCase):
    def test_unmanaged_healthy_port_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'pids').mkdir()
            with patch.object(services, 'LOCAL', root), patch.object(services, 'healthy', return_value=True):
                with self.assertRaises(SystemExit):
                    services.launch('api', ['unused'], 'unused', 8000)

if __name__ == '__main__':
    unittest.main()
