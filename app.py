import streamlit as st
import matplotlib.pyplot as plt
from analysis import (
    get_filtered_players,
    get_teams,
    get_best_batsmen,
    get_best_bowlers,
    get_best_allrounders,
    get_player_ranking,
    predict_match_winner
)

st.set_page_config(page_title="Dream11 Predictor", layout="centered")

st.markdown("<h1 style='text-align:center; color:darkred;'>🏏 Dream11 Team Predictor 🏏</h1>", unsafe_allow_html=True)

teams = get_teams()

team1 = st.selectbox("Select Team 1", teams)
team2 = st.selectbox("Select Team 2", teams)

# 🎯 Venue Selection
import pandas as pd
data = pd.read_csv("IPL.csv", low_memory=False)

venue = st.selectbox("🏟️ Select Stadium", sorted(data['venue'].dropna().unique()))

if team1 == team2:
    st.warning("Select different teams")

# =====================
# 🔮 MATCH PREDICTION
# =====================
st.markdown("---")
st.subheader("🔮 Match Winner Prediction")

if team1 != team2:

    winner, prob1, prob2 = predict_match_winner(team1, team2, venue)

    if winner == "Not enough data":
        st.error("❌ Not enough data")

    else:
        st.success(f"🏆 Predicted Winner: {winner}")

        # % display
        st.info(f"{team1}: {prob1:.1f}% chance")
        st.info(f"{team2}: {prob2:.1f}% chance")

        # Progress bars
        st.write(f"{team1} Win Probability")
        st.progress(int(prob1))

        st.write(f"{team2} Win Probability")
        st.progress(int(prob2))

# =====================
# 🏆 BEST 11
# =====================
if st.button("Generate Team", disabled=(team1 == team2)):

    top_players = get_filtered_players(team1, team2)

    if not top_players.empty:
        st.subheader("🏆 Best 11")

        df = top_players[['batter', 'score']].reset_index(drop=True)
        df.columns = ['Player', 'Score']

        st.dataframe(df)

        st.success(f"Captain: {top_players.iloc[0]['batter']}")
        st.info(f"Vice Captain: {top_players.iloc[1]['batter']}")

# =====================
# 📊 ANALYSIS
# =====================
st.markdown("---")
st.header("📊 IPL Player Analysis")

tab1, tab2, tab3 = st.tabs(["Batsmen", "Bowlers", "All-Rounders"])

with tab1:
    batsmen = get_best_batsmen().round(2)
    st.dataframe(batsmen[['player', 'runs', 'strike_rate', 'average', 'matches', 'score']])

    fig, ax = plt.subplots()
    batsmen.plot(kind='bar', x='player', y='strike_rate', ax=ax)
    st.pyplot(fig)

with tab2:
    bowlers = get_best_bowlers().round(2)
    st.dataframe(bowlers[['player', 'wickets', 'economy', 'wickets_per_match', 'matches', 'score']])

    fig, ax = plt.subplots()
    bowlers.plot(kind='bar', x='player', y='wickets', ax=ax)
    st.pyplot(fig)

with tab3:
    allrounders = get_best_allrounders().round(2)
    st.dataframe(allrounders[['player', 'runs', 'wickets', 'matches', 'score']])

# =====================
# 🏆 RANKING
# =====================
st.markdown("---")
st.header("🏆 Top 100 Player Ranking")

ranking = get_player_ranking().round(3)

st.dataframe(
    ranking[['rank', 'player', 'runs', 'wickets', 'strike_rate', 'average', 'matches', 'score']],
    use_container_width=True
)

fig, ax = plt.subplots()
ranking.head(10).plot(kind='bar', x='player', y='score', ax=ax)
st.pyplot(fig)