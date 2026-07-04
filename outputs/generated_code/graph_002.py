import pandas as pd
import matplotlib.pyplot as plt
import json

# Hardcode the dataset path
file_path = 'fifa_data.csv'

# Load the dataset
df = pd.read_csv(file_path)

# Define the columns for analysis
performance_cols = [
    'goals', 'assists', 'tackles', 'saves',
    'offensive_contribution', 'defensive_contribution', 'player_rating'
]

# Group by 'position' and calculate the mean for the performance metrics
performance_by_position = df.groupby('position')[performance_cols].mean()

# Create the bar chart
fig, axes = plt.subplots(nrows=len(performance_cols), ncols=1, figsize=(10, 4 * len(performance_cols)), sharex=True)
fig.suptitle('Average Player Performance by Position', y=1.02, fontsize=16)

for i, col in enumerate(performance_cols):
    ax = axes[i]
    performance_by_position[col].plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title(f'Average {col.replace("_", " ").title()}', fontsize=12)
    ax.set_ylabel('Average Value')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()

# Save the plot
output_filename = 'outputs/graphs/graph_002.png'
plt.savefig(output_filename)

# Compute summary statistics
summary = performance_by_position.to_dict(orient='index')
# Convert numpy/pandas scalars to native Python types for JSON serialization
for position, metrics in summary.items():
    for metric, value in metrics.items():
        summary[position][metric] = float(value)

print("STATS_JSON:" + json.dumps(summary, default=str))