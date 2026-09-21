"""같은 권한 검사기를 시안02의 로컬 프록시와 증거에 적용한다."""
import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], '2']
runpy.run_path(str(Path.cwd() / 'execute/workHitory/integration-concept-01/independent-http-probe.py'), run_name='__main__')
