from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from profiler.loader import load_dataset
from profiler.profiler import profile_dataset

from planner.planner import generate_analysis_plan

df = load_dataset("fifa_data.csv")

profile = profile_dataset(df)

plan = generate_analysis_plan(profile)

print(plan)
