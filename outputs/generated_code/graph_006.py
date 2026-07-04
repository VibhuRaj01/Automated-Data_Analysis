import pandas as pd
import matplotlib.pyplot as plt
import json

# Hardcoded dataset path
file_path = 'fifa_data.csv'

# Load the dataset
df = pd.read_csv(file_path)

# Columns for the analysis
columns_to_plot = [
    "player_rating",
    "performance_score",
    "offensive_contribution",
    "defensive_contribution",
    "creativity_score",
    "consistency_score"
]

# Create a figure and a set of subplots
fig, axes = plt.subplots(nrows=len(columns_to_plot), ncols=1, figsize=(10, 4 * len(columns_to_plot)))

# Plot histograms for each column
for i, col in enumerate(columns_to_plot):
    axes[i].hist(df[col], bins=30, edgecolor='black', alpha=0.7)
    axes[i].set_title(f'Distribution of {col.replace("_", " ").title()}')
    axes[i].set_xlabel(col.replace("_", " ").title())
    axes[i].set_ylabel('Frequency')
    axes[i].grid(axis='y', alpha=0.75)

plt.tight_layout()

# Save the plot
output_filename = 'outputs/graphs/graph_006.png'
plt.savefig(output_filename)

# Compute summary statistics
summary = {}
for col in columns_to_plot:
    desc = df[col].describe()
    summary[col] = {
        "mean": float(desc['mean']),
        "median": float(df[col].median()),
        "std": float(desc['std']),
        "min": float(desc['min']),
        "max": float(desc['max'])
    }

print("STATS_JSON:" + json.dumps(summary, default=str))