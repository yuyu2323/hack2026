"""01과 같은 읽기 전용 검사기를 시안02 대상으로 실행한다."""
import runpy
import sys
from pathlib import Path

sys.argv = [sys.argv[0], '2']
runpy.run_path(str(Path.cwd() / 'execute/workHitory/integration-concept-01/independent-probe.py'), run_name='__main__')
