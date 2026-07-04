from pathlib import Path
import sys

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from profiler.loader import load_dataset
from profiler.profiler import profile_dataset

from planner.planner import generate_analysis_plan

from generator.generator import generate_code
from generator.validator import validate_code


def main():

    dataset_path = PROJECT_ROOT / "fifa_data.csv"

    print("=" * 70)
    print("Loading Dataset")
    print("=" * 70)

    df = load_dataset(dataset_path)

    profile = profile_dataset(df)

    print("✓ Dataset Profile Created")

    print("\nGenerating Analysis Plan...\n")

    plan = generate_analysis_plan(profile)

    print(f"✓ {len(plan)} analyses generated.\n")

    output_dir = PROJECT_ROOT / "outputs" / "generated_code"
    output_dir.mkdir(parents=True, exist_ok=True)

    for analysis in plan:

        print("-" * 70)
        print(analysis["title"])
        print("-" * 70)

        code, filename = generate_code(
            dataset_path=str(dataset_path),
            profile=profile,
            analysis=analysis,
        )

        validate_code(code)

        python_file = output_dir / f"{filename[:-4]}.py"

        with open(python_file, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"✓ Code saved to {python_file.name}")
        print()

    print("=" * 70)
    print("Generator Test Passed")
    print("=" * 70)


if __name__ == "__main__":
    main()
