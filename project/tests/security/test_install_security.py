"""설치 시 인증서 검증과 배포본 무결성 검증을 유지한다."""
import hashlib
import io
from pathlib import Path
import ssl
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import install_security


class SecurityInstallerTests(unittest.TestCase):
    def test_download_requires_verified_tls_and_installs_checked_archive(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
            entry = tarfile.TarInfo('gitleaks')
            entry.size = 7
            archive.addfile(entry, io.BytesIO(b'fixture'))
        data = buffer.getvalue()

        def download(url, *, timeout, context=None):
            self.assertIsInstance(context, ssl.SSLContext)
            self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
            self.assertTrue(context.check_hostname)
            self.assertGreater(len(context.get_ca_certs()), 0)
            return io.BytesIO(data)

        with tempfile.TemporaryDirectory() as folder:
            with patch.object(install_security, 'ROOT', Path(folder)), \
                 patch.object(install_security, 'DIGESTS', {('Test', 'arch'): ('test', hashlib.sha256(data).hexdigest())}), \
                 patch.object(install_security.platform, 'system', return_value='Test'), \
                 patch.object(install_security.platform, 'machine', return_value='arch'), \
                 patch.object(install_security.urllib.request, 'urlopen', side_effect=download):
                install_security.main()
            self.assertEqual((Path(folder) / '.local/bin/gitleaks').read_bytes(), b'fixture')

    def test_checksum_mismatch_never_replaces_installed_binary(self):
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / '.local/bin/gitleaks'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'existing')
            with patch.object(install_security, 'ROOT', Path(folder)), \
                 patch.object(install_security.urllib.request, 'urlopen', return_value=io.BytesIO(b'corrupted')):
                with self.assertRaisesRegex(SystemExit, '체크섬 불일치'):
                    install_security.main()
            self.assertEqual(binary.read_bytes(), b'existing')


if __name__ == '__main__':
    unittest.main()
