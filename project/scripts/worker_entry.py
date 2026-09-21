"""macOS에서도 프로세스 명령에 프로젝트 경로를 유지하는 작업자 진입점."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.analysis_jobs.worker import main


if __name__ == '__main__':
    main()
