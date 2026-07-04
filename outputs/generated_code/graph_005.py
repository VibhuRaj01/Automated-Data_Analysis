import pandas as pd
import matplotlib.pyplot as plt
import json

# Hardcode the dataset path
file_path = 'fifa_data.csv'
output_filename = 'outputs/graphs/graph_005.png'

# Load the dataset
df = pd.read_csv(file_path)

# Define the columns for analysis
physical_attributes = ['height_cm', 'weight_kg', 'top_speed_kmh']
performance_metrics = ['aerial_duels_won', 'sprint_distance_km', 'defensive_actions', 'goals']

# Create a figure and a set of subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten() # Flatten the 2x3 array of axes for easy iteration

plot_data = [
    ('height_cm', 'aerial_duels_won'),
    ('weight_kg', 'defensive_actions'),
    ('top_speed_kmh', 'sprint_distance_km'),
    ('height_cm', 'goals'),
    ('weight_kg', 'goals'),
    ('top_speed_kmh', 'goals')
]

correlations = {}

for i, (x_col, y_col) in enumerate(plot_data):
    ax = axes[i]
    ax.scatter(df[x_col], df[y_col], alpha=0.5, s=10)
    ax.set_title(f'{y_col} vs {x_col}')
    ax.set_xlabel(x_col.replace('_', ' ').title())
    ax.set_ylabel(y_col.replace('_', ' ').title())

    # Calculate correlation
    correlation = df[x_col].corr(df[y_col])
    correlations[f'{x_col}_vs_{y_col}_correlation'] = float(correlation)

plt.tight_layout()
plt.suptitle('Relationship between Physical Attributes and On-Field Performance', y=1.02, fontsize=16)

# Save the plot
plt.savefig(output_filename)

# Prepare the summary JSON
summary = {
    "correlations": correlations
}

# Print the summary JSON
print("STATS_JSON:" + json.dumps(summary, default=str))