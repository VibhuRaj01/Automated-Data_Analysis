from pathlib import Path
import ast

from executor.executor import execute_script


def validate_repaired_code(
    repaired_code: str,
    script_path: str | Path,
):
    """
    Validate repaired code by:

    1. Checking Python syntax.
    2. Writing it to disk.
    3. Executing it.
    4. Returning the execution result.
    """

    # -------------------------
    # Syntax validation
    # -------------------------

    try:
        ast.parse(repaired_code)

    except SyntaxError as e:
        return {
            "success": False,
            "stage": "syntax",
            "stderr": str(e),
        }

    script_path = Path(script_path)

    script_path.write_text(
        repaired_code,
        encoding="utf-8",
    )

    result = execute_script(script_path)

    result["stage"] = "execution"

    return result
