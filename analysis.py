import pandas as pd

# Load dataset
data = pd.read_csv("IPL.csv", low_memory=False)

# Remove unwanted column
if 'Unnamed: 0' in data.columns:
    data = data.drop(columns=['Unnamed: 0'])


# 🔹 GET TEAMS
def get_teams():
    return sorted(data['batting_team'].dropna().unique())


# 🏏 BEST 11 (TEAM BASED - SIMPLE LOGIC)
def get_filtered_players(team1, team2):

    filtered = data[
        ((data['batting_team'] == team1) & (data['bowling_team'] == team2)) |
        ((data['batting_team'] == team2) & (data['bowling_team'] == team1))
    ]

    if filtered.empty:
        return pd.DataFrame()

    batsman_runs = filtered.groupby('batter')['runs_batter'].sum().reset_index()

    wickets = filtered[filtered['striker_out'] == True]
    bowler_wickets = wickets.groupby('bowler')['striker_out'].count().reset_index()

    player_score = pd.merge(
        batsman_runs,
        bowler_wickets,
        left_on='batter',
        right_on='bowler',
        how='outer'
    )

    player_score = player_score.fillna(0)

    # Simple scoring
    player_score['score'] = player_score['runs_batter'] + (player_score['striker_out'] * 25)

    return player_score.sort_values(by='score', ascending=False).head(11)


# 🔥 BATSMEN (ICC-INSPIRED)
def get_best_batsmen():

    batsman = data.groupby('batter').agg({
        'runs_batter': 'sum',
        'ball': 'count',
        'match_id': 'nunique'
    }).reset_index()

    batsman.columns = ['player', 'runs', 'balls', 'matches']

    # Calculations
    batsman['strike_rate'] = (batsman['runs'] / batsman['balls']) * 100
    batsman['average'] = batsman['runs'] / batsman['matches']

    # Normalization
    batsman['norm_runs'] = batsman['runs'] / batsman['runs'].max()
    batsman['norm_sr'] = batsman['strike_rate'] / batsman['strike_rate'].max()
    batsman['norm_avg'] = batsman['average'] / batsman['average'].max()
    batsman['norm_matches'] = batsman['matches'] / batsman['matches'].max()

    # ICC-inspired scoring
    batsman['score'] = (
        0.4 * batsman['norm_runs'] +
        0.3 * batsman['norm_sr'] +
        0.2 * batsman['norm_avg'] +
        0.1 * batsman['norm_matches']
    ) * 100

    return batsman.sort_values(by='score', ascending=False).head(10)


# ⚡ BOWLERS (ICC-INSPIRED)
def get_best_bowlers():

    runs = data.groupby('bowler')['runs_total'].sum().reset_index()
    balls = data.groupby('bowler')['ball'].count().reset_index()
    matches = data.groupby('bowler')['match_id'].nunique().reset_index()

    wickets = data[data['striker_out'] == True]
    wickets = wickets.groupby('bowler')['striker_out'].count().reset_index()

    bowler = runs.merge(balls, on='bowler').merge(wickets, on='bowler').merge(matches, on='bowler')

    bowler.columns = ['player', 'runs_given', 'balls', 'wickets', 'matches']

    # Calculations
    bowler['overs'] = bowler['balls'] / 6
    bowler['economy'] = bowler['runs_given'] / bowler['overs']

    # ✅ FIXED COLUMN NAME
    bowler['wickets_per_match'] = bowler['wickets'] / bowler['matches']

    # Normalization
    bowler['norm_wickets'] = bowler['wickets'] / bowler['wickets'].max()
    bowler['norm_economy'] = bowler['economy'] / bowler['economy'].max()
    bowler['norm_wpm'] = bowler['wickets_per_match'] / bowler['wickets_per_match'].max()

    # ICC-inspired scoring
    bowler['score'] = (
        0.5 * bowler['norm_wickets'] -
        0.3 * bowler['norm_economy'] +
        0.2 * bowler['norm_wpm']
    ) * 100

    return bowler.sort_values(by='score', ascending=False).head(10)


# 🔥 ALL-ROUNDERS (COMBINED ICC STYLE)
def get_best_allrounders():

    # FULL batsman data
    batsman = data.groupby('batter')['runs_batter'].sum().reset_index()
    batsman.columns = ['player', 'runs']

    # FULL bowler data
    wickets = data[data['striker_out'] == True]
    bowler = wickets.groupby('bowler')['striker_out'].count().reset_index()
    bowler.columns = ['player', 'wickets']

    # Matches
    matches = data.groupby('batter')['match_id'].nunique().reset_index()
    matches.columns = ['player', 'matches']

    # Merge ALL data
    allrounder = batsman.merge(bowler, on='player', how='inner')  # 🔥 INNER here is correct

    allrounder = allrounder.merge(matches, on='player', how='left')

    # Score
    allrounder['score'] = allrounder['runs'] + (allrounder['wickets'] * 25)

    return allrounder.sort_values(by='score', ascending=False).head(10)


# 🏆 PLAYER RANKING (TOP 100)
def get_player_ranking():

    # Batting data
    batsman = data.groupby('batter').agg({
        'runs_batter': 'sum',
        'ball': 'count',
        'match_id': 'nunique'
    }).reset_index()

    batsman.columns = ['player', 'runs', 'balls', 'matches']

    batsman['strike_rate'] = (batsman['runs'] / batsman['balls']) * 100
    batsman['average'] = batsman['runs'] / batsman['matches']

    # Bowling data
    runs_given = data.groupby('bowler')['runs_total'].sum().reset_index()
    balls = data.groupby('bowler')['ball'].count().reset_index()
    matches_bowl = data.groupby('bowler')['match_id'].nunique().reset_index()

    wickets = data[data['striker_out'] == True]
    wickets = wickets.groupby('bowler')['striker_out'].count().reset_index()

    bowler = runs_given.merge(balls, on='bowler') \
                        .merge(wickets, on='bowler') \
                        .merge(matches_bowl, on='bowler')

    bowler.columns = ['player', 'runs_given', 'balls_bowl', 'wickets', 'matches_bowl']

    bowler['overs'] = bowler['balls_bowl'] / 6
    bowler['economy'] = bowler['runs_given'] / bowler['overs']
    bowler['wpm'] = bowler['wickets'] / bowler['matches_bowl']

    # Merge batting + bowling
    players = pd.merge(batsman, bowler, on='player', how='outer')
    players = players.fillna(0)

    # NORMALIZATION
    players['norm_runs'] = players['runs'] / players['runs'].max()
    players['norm_sr'] = players['strike_rate'] / players['strike_rate'].max()
    players['norm_avg'] = players['average'] / players['average'].max()
    players['norm_wickets'] = players['wickets'] / players['wickets'].max()
    players['norm_wpm'] = players['wpm'] / players['wpm'].max()
    players['norm_economy'] = players['economy'] / players['economy'].max()

    # FINAL SCORE
    players['score'] = (
        0.30 * players['norm_runs'] +
        0.15 * players['norm_sr'] +
        0.15 * players['norm_avg'] +
        0.25 * players['norm_wickets'] +
        0.10 * players['norm_wpm'] -
        0.05 * players['norm_economy']
    ) * 100

    # Ranking
    players = players.sort_values(by='score', ascending=False).head(100)
    players['rank'] = range(1, len(players) + 1)

    return players


# 🔮 MATCH WINNER PREDICTION
def predict_match_winner(team1, team2, venue):

    matches = data[
        ((data['batting_team'] == team1) & (data['bowling_team'] == team2)) |
        ((data['batting_team'] == team2) & (data['bowling_team'] == team1))
    ]

    if matches.empty:
        return "Not enough data", 0, 0

    venue_matches = matches[matches['venue'] == venue]

    if venue_matches.empty:
        venue_matches = matches

    wins_team1 = venue_matches[venue_matches['match_won_by'] == team1]['match_id'].nunique()
    wins_team2 = venue_matches[venue_matches['match_won_by'] == team2]['match_id'].nunique()

    total = wins_team1 + wins_team2

    if total == 0:
        return "Equal chances", 50, 50

    prob1 = (wins_team1 / total) * 100
    prob2 = (wins_team2 / total) * 100

    if prob1 > prob2:
        winner = team1
    elif prob2 > prob1:
        winner = team2
    else:
        winner = "Equal chances"

    return winner, prob1, prob2