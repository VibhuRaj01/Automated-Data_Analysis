import pandas as pd
import matplotlib.pyplot as plt
import json

# Hardcoded dataset path
file_path = 'fifa_data.csv'
output_filename = 'outputs/graphs/graph_003.png'

# Load the dataset
df = pd.read_csv(file_path)

# Columns specified in the request
columns = ["team", "tournament_stage", "match_result", "goals_team", "goals_opponent"]
df_analysis = df[columns].copy()

# Identify top 5 teams based on the total number of matches played
top_teams = df_analysis['team'].value_counts().nlargest(5).index.tolist()

# Filter data for these top teams
df_filtered = df_analysis[df_analysis['team'].isin(top_teams)]

# Aggregate match results: count of Wins, Losses, Draws for each team per tournament stage
match_outcomes = df_filtered.groupby(['team', 'tournament_stage'])['match_result'].value_counts().unstack(fill_value=0)

# Calculate percentages
match_outcomes_pct = match_outcomes.div(match_outcomes.sum(axis=1), axis=0) * 100

# Define a consistent order for tournament stages
stage_order = [
    "Group Stage", "Round of 32", "Round of 16", "Quarter Finals",
    "Semi Finals", "Third Place Play-off", "Final"
]

# Reindex the DataFrame to ensure consistent stage order for plotting
# This creates entries for all combinations of top_teams and stage_order, filling missing with 0
full_index = pd.MultiIndex.from_product([top_teams, stage_order], names=['team', 'tournament_stage'])
match_outcomes_pct = match_outcomes_pct.reindex(full_index, fill_value=0)

# Ensure 'W', 'L', 'D' columns exist, fill with 0 if not present in any stage
for col in ['W', 'L', 'D']:
    if col not in match_outcomes_pct.columns:
        match_outcomes_pct[col] = 0

# Sort columns for consistent stacking order (e.g., L, D, W)
match_outcomes_pct = match_outcomes_pct[['L', 'D', 'W']]

# Plotting
num_teams = len(top_teams)
fig, axes = plt.subplots(num_teams, 1, figsize=(12, 4 * num_teams), sharex=True)
if num_teams == 1: # Handle case where only one team is selected
    axes = [axes]

colors = {'W': 'lightgreen', 'D': 'lightgray', 'L': 'salmon'}

for i, team_name in enumerate(top_teams):
    ax = axes[i]
    team_data = match_outcomes_pct.loc[team_name]
    
    # Filter out stages where the team had no matches (sum of W, L, D is 0)
    # This ensures only stages where the team actually played are shown
    team_data_to_plot = team_data[(team_data['W'] > 0) | (team_data['L'] > 0) | (team_data['D'] > 0)]
    
    if not team_data_to_plot.empty:
        team_data_to_plot.plot(kind='bar', stacked=True, ax=ax, color=[colors[col] for col in team_data_to_plot.columns])
        ax.set_title(f'{team_name} Match Outcomes by Tournament Stage', fontsize=14)
        ax.set_ylabel('Percentage (%)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(title='Result', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        ax.set_title(f'{team_name} Match Outcomes by Tournament Stage (No Data)', fontsize=14)
        ax.text(0.5, 0.5, 'No match data for this team across stages.', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])

axes[-1].set_xlabel('Tournament Stage', fontsize=12)
plt.tight_layout()

# Save the plot
plt.savefig(output_filename)

# Compute summary statistics for JSON output
summary = {}
for team_name in top_teams:
    team_summary = {}
    team_data = match_outcomes_pct.loc[team_name]
    # Filter out stages with no matches for the summary as well
    team_data_for_summary = team_data[(team_data['W'] > 0) | (team_data['L'] > 0) | (team_data['D'] > 0)]
    
    if not team_data_for_summary.empty:
        for stage in team_data_for_summary.index:
            stage_results = team_data_for_summary.loc[stage].to_dict()
            team_summary[stage] = {k: float(v) for k, v in stage_results.items()}
    summary[team_name] = team_summary

print("STATS_JSON:" + json.dumps(summary, default=str))