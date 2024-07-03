import streamlit as st

from common.db import Game, Round, Session, get_or_create_player
from common.utils import check_winner, display_scores, normalize_name


def initialize_game() -> None:
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if not st.session_state.game_started:
        st.session_state.players = []
        st.session_state.scores = {}
        st.session_state.teams = {}
        st.session_state.round = 1
        st.session_state.game_id = None
        check_winner.__defaults__ = (41,)


def setup_game() -> None:
    st.image("common/logo.png")
    st.markdown(
        """
            <style>
            .team-header {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            </style>
            """,
        unsafe_allow_html=True,
    )

    with st.form("player_setup"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="team-header">Team 1</div>', unsafe_allow_html=True)
            player_1 = st.text_input("Player 1:", key="player_1")
            player_2 = st.text_input("Player 2:", key="player_2")

        with col2:
            st.markdown('<div class="team-header">Team 2</div>', unsafe_allow_html=True)
            player_3 = st.text_input("Player 1:", key="player_3")
            player_4 = st.text_input("Player 2:", key="player_4")

        submit_button = st.form_submit_button("Start Game")

    if submit_button:
        players = [player_1, player_2, player_3, player_4]
        if all(players):
            normalized_players = [normalize_name(p) for p in players]
            if len(set(normalized_players)) != len(players):
                st.error("Please enter unique names for all players.")
                return

            session = Session()
            new_game = Game()
            session.add(new_game)
            session.commit()
            st.session_state.game_id = new_game.id

            st.session_state.players = []
            st.session_state.teams = {}
            for i, player_name in enumerate(players):
                player = get_or_create_player(session, player_name)
                st.session_state.players.append(player.name)
                st.session_state.scores[player.name] = 0
                st.session_state.teams[player.name] = 1 if i < 2 else 2

            session.close()
            st.session_state.game_started = True
            st.experimental_rerun()
        else:
            st.error("Please enter names for all players.")


def play_round() -> None:
    st.subheader(f"Round {st.session_state.round}")

    if st.session_state.round > 1:
        st.subheader("Current Scores")
        display_scores()

    winner = check_winner()
    if winner:
        st.success(f"Team {st.session_state.teams[winner]} wins! {winner} reached the winning score !")
        if st.button("Start New Game"):
            st.session_state.game_started = False
            st.experimental_rerun()
        return

    st.markdown(
        """
            <style>
            [data-testid="stCheckbox"] {
                justify-content: right;
            }
            </style>
            """,
        unsafe_allow_html=True,
    )

    with st.form(key=f"round_{st.session_state.round}"):
        bets = {}
        results = {}
        for player in st.session_state.players:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{player}**")
            with col2:
                bets[player] = st.number_input(
                    f"Bet",
                    min_value=2,
                    max_value=26,
                    step=1,
                    key=f"bet_{player}_{st.session_state.round}",
                    label_visibility="collapsed",
                )
            with col3:
                results[player] = st.checkbox("Won?", key=f"win_{player}_{st.session_state.round}")

        submit_button = st.form_submit_button("Submit Round Results")

    if submit_button:
        session = Session()
        for player, bet in bets.items():
            is_win = results[player]
            player_obj = get_or_create_player(session, player)
            previous_score = st.session_state.scores[player]
            new_score = previous_score + bet if is_win else previous_score - bet

            round = Round(
                game_id=st.session_state.game_id,
                round_number=st.session_state.round,
                player_id=player_obj.id,
                team=st.session_state.teams[player],
                bet=bet,
                is_win=is_win,
                score=new_score,
            )
            session.add(round)
            st.session_state.scores[player] = new_score

        session.commit()
        session.close()

        st.session_state.round += 1
        st.rerun()


def main() -> None:
    initialize_game()

    if not st.session_state.game_started:
        setup_game()
    else:
        play_round()


if __name__ == "__main__":
    main()
