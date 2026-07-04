from pathlib import Path
import sys

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from profiler.loader import load_dataset
from profiler.profiler import profile_dataset

from debugger import repair_code


def main():

    dataset_path = PROJECT_ROOT / "fifa_data.csv"

    df = load_dataset(dataset_path)

    profile = profile_dataset(df)

    analysis = {
        "priority": 1,
        "title": "Distribution of Player Market Values",
        "analysis_type": "distribution",
        "chart": "histogram",
        "columns": ["market_value_eur"],
        "reason": "Analyze the distribution of player market values.",
    }

    broken_code = f"""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"{dataset_path}")

plt.figure(figsize=(10,6))

# Wrong column name
plt.hist(df["market_value_eurrrrr"], bins=20)

plt.title("Distribution of Player Market Values")
plt.xlabel("Market Value")
plt.ylabel("Frequency")

plt.tight_layout()
plt.savefig("outputs/graphs/graph_001.png")
plt.close()
"""

    execution_result = {
        "success": False,
        "return_code": 1,
        "stdout": "",
        "stderr": """
KeyError: 'market_value_eurrrrr'
""",
    }

    repaired_code = repair_code(
        original_code=broken_code,
        profile=profile,
        analysis=analysis,
        execution_result=execution_result,
    )

    print("=" * 80)
    print("REPAIRED CODE")
    print("=" * 80)
    print(repaired_code)


if __name__ == "__main__":
    main()
