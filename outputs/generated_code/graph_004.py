import pandas as pd
import matplotlib.pyplot as plt
import json

# Hardcode the dataset path
file_path = 'fifa_data.csv'

# Load the dataset
df = pd.read_csv(file_path)

# Convert 'match_date' to datetime objects
df['match_date'] = pd.to_datetime(df['match_date'])

# Sort by player_name and match_date to ensure correct trend plotting
df = df.sort_values(by=['player_name', 'match_date'])

# Select relevant columns for the analysis
df_filtered = df[['player_name', 'match_date', 'player_rating', 'goals', 'assists', 'minutes_played']]

# Identify top players based on their average player_rating across all their matches
player_avg_rating = df_filtered.groupby('player_name')['player_rating'].mean().sort_values(ascending=False)

# Select the top 5 players for detailed trend analysis
top_players = player_avg_rating.head(5).index.tolist()

# Filter the DataFrame to include only data for these top players
df_top_players = df_filtered[df_filtered['player_name'].isin(top_players)]

# Create the plot: a 2x2 grid of subplots, each showing a different performance metric
fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True)
axes = axes.flatten() # Flatten the 2x2 array of axes for easier iteration

metrics = ['player_rating', 'goals', 'assists', 'minutes_played']
titles = ['Player Rating Trend', 'Goals Trend', 'Assists Trend', 'Minutes Played Trend']
y_labels = ['Player Rating', 'Goals', 'Assists', 'Minutes Played']

# Plot each metric for the top players
for i, metric in enumerate(metrics):
    ax = axes[i]
    for player in top_players:
        player_data = df_top_players[df_top_players['player_name'] == player]
        ax.plot(player_data['match_date'], player_data[metric], label=player, marker='o', markersize=3, linestyle='-')
    ax.set_title(titles[i])
    ax.set_ylabel(y_labels[i])
    ax.grid(True, linestyle='--', alpha=0.6)
    if i == 0: # Add legend only to the first subplot to avoid redundancy
        ax.legend(title='Player Name', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add a main title for the entire figure
fig.suptitle('Individual Player Performance Trends Over Tournament (Top 5 Players)', fontsize=16)

# Adjust layout to prevent labels/titles from overlapping and make space for the legend
plt.tight_layout(rect=[0, 0.03, 0.85, 0.95])

# Save the plot to a file
output_filename = 'outputs/graphs/graph_004.png'
plt.savefig(output_filename)

# Compute summary statistics for the selected top players
summary = {}
for player in top_players:
    player_summary_data = df_top_players[df_top_players['player_name'] == player]
    summary[player] = {
        'average_player_rating': float(player_summary_data['player_rating'].mean()),
        'total_goals': int(player_summary_data['goals'].sum()),
        'total_assists': int(player_summary_data['assists'].sum()),
        'average_minutes_played': float(player_summary_data['minutes_played'].mean())
    }

# Print the summary statistics as a JSON string
print("STATS_JSON:" + json.dumps(summary, default=str))