import pandas as pd
import streamlit as st


def normalize_name(name: str) -> str:
    return name.strip().lower()


def display_scores():
    scores_data = []
    for player, score in st.session_state.scores.items():
        team = st.session_state.teams[player]
        scores_data.append({"Player": player, "Team": team, "Score": score})

    df = pd.DataFrame(scores_data)
    df = df.sort_values(by=["Score"], ascending=[False])

    st.table(df)


def check_winner() -> str | None:
    winning_threshold = 41
    while True:
        for player, score in st.session_state.scores.items():
            if score >= winning_threshold:
                team = st.session_state.teams[player]
                teammate = [p for p in st.session_state.players if st.session_state.teams[p] == team and p != player][0]
                teammate_score = st.session_state.scores[teammate]

                if teammate_score >= 0:
                    return player
                else:
                    winning_threshold += 10
                    st.info(
                        f"Player {player} has reached {score} points, but their teammate has a negative score. The winning threshold is now {winning_threshold} points."
                    )
                    break
        else:
            return None
