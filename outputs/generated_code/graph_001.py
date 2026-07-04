import pandas as pd
import matplotlib.pyplot as plt
import json

# Hardcode the dataset path
file_path = 'fifa_data.csv'

# Load the dataset
df = pd.read_csv(file_path)

# Select relevant columns as per the request
columns_of_interest = [
    "market_value_eur",
    "player_rating",
    "goals",
    "assists",
    "age",
    "position"
]
df_filtered = df[columns_of_interest].copy()

# Drop rows with any missing values in the selected columns
df_filtered.dropna(inplace=True)

# Scale goals for marker size for better visualization
# Add 1 to goals to ensure even players with 0 goals have a visible marker, then scale
df_filtered['scaled_goals'] = (df_filtered['goals'] + 1) * 20

# Create the scatter plot
fig, ax = plt.subplots(figsize=(12, 8))

# Get unique positions and assign distinct colors
positions = df_filtered['position'].unique()
colors = plt.cm.get_cmap('tab10', len(positions)) # Using 'tab10' for distinct categorical colors

# Plot each position separately to create a categorical legend
for i, pos in enumerate(positions):
    subset = df_filtered[df_filtered['position'] == pos]
    ax.scatter(
        subset['player_rating'],
        subset['market_value_eur'],
        s=subset['scaled_goals'],
        alpha=0.6,
        edgecolors='w',
        linewidth=0.5,
        label=pos,
        color=colors(i)
    )

ax.set_title('Player Market Value vs. Player Rating, Goals, and Position')
ax.set_xlabel('Player Rating')
ax.set_ylabel('Market Value (EUR)')
ax.ticklabel_format(style='plain', axis='y') # Prevent scientific notation on y-axis
ax.grid(True, linestyle='--', alpha=0.7)

# Create a dummy legend for marker sizes (goals)
handles, labels = ax.get_legend_handles_labels()
goal_levels = [1, 5, 10, 20] # Example goal levels for size legend
for level in goal_levels:
    handles.append(plt.scatter([], [], s=(level + 1) * 20, color='gray', alpha=0.6, label=f'{level} Goals'))
    labels.append(f'{level} Goals')

# Recreate the legend with both position and size
ax.legend(handles, labels, title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()

# Save the plot
output_filename = 'outputs/graphs/graph_001.png'
plt.savefig(output_filename)

# Compute summary statistics (correlations)
summary = {}
numeric_cols_for_corr = ["player_rating", "goals", "assists", "age"]
for col in numeric_cols_for_corr:
    correlation = df_filtered['market_value_eur'].corr(df_filtered[col])
    summary[f'correlation_market_value_eur_vs_{col}'] = float(correlation)

# Print the summary JSON
print("STATS_JSON:" + json.dumps(summary, default=str))