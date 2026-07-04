from pathlib import Path
import sys

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from executor.executor import execute_script


def main():
    output_dir = PROJECT_ROOT / "outputs" / "generated_code"

    if not output_dir.exists():
        print(f"Output directory {output_dir} does not exist.")
        return

    python_files = list(output_dir.glob("*.py"))

    if not python_files:
        print(f"No Python files found in {output_dir}.")
        return

    for python_file in python_files:
        print("=" * 70)
        print(f"Executing {python_file.name}")
        print("=" * 70)

        result = execute_script(python_file)

        print(f"Success: {result['success']}")
        print(f"Return Code: {result['return_code']}")
        print(f"Execution Time: {result['execution_time']} seconds")
        print("Standard Output:")
        print(result["stdout"])
        print("Standard Error:")
        print(result["stderr"])
        print()


if __name__ == "__main__":
    main()
