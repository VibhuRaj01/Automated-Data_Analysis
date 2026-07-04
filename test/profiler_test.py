import json
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from profiler.loader import load_dataset
from profiler.profiler import profile_dataset


def main():

    dataset_path = PROJECT_ROOT / "fifa_data.csv"

    print("=" * 70)
    print("Loading Dataset")
    print("=" * 70)

    df = load_dataset(dataset_path)

    print("✓ Dataset Loaded Successfully")
    print(f"Shape : {df.shape}")

    print("\nFirst Five Rows:\n")
    print(df.head())

    print("\n" + "=" * 70)
    print("Profiling Dataset")
    print("=" * 70)

    profile = profile_dataset(df)

    print("✓ Profiling Complete\n")

    print(json.dumps(profile, indent=4))

    print("\n" + "=" * 70)
    print("Dataset Summary")
    print("=" * 70)

    dataset = profile["dataset"]

    print(f"Rows        : {dataset['rows']}")
    print(f"Columns     : {dataset['columns']}")
    print(f"Duplicates  : {dataset['duplicates']}")
    print(f"Memory (MB) : {dataset['memory_mb']}")

    print("\nColumn Summary")
    print("-" * 70)

    for column in profile["columns"]:

        print(
            f"{column['name']:<25}"
            f"{column['semantic_type']:<15}"
            f"Missing: {column['missing']:<5}"
            f"Unique: {column['unique']}"
        )


if __name__ == "__main__":
    main()
