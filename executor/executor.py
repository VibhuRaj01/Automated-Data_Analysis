from pathlib import Path
import subprocess
import sys
import time


def execute_script(script_path: str | Path) -> dict:

    script_path = Path(script_path)

    if not script_path.exists():
        raise FileNotFoundError(f"{script_path} does not exist.")

    start = time.perf_counter()

    try:

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "execution_time": round(
                time.perf_counter() - start,
                3,
            ),
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out.",
            "return_code": -1,
            "execution_time": round(
                time.perf_counter() - start,
                3,
            ),
        }
