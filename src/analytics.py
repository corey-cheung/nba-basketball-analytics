#!/usr/bin/env python

import pandas as pd
import streamlit as st
import duckdb


def title_and_overview() -> None:
    """
    Set up title and overview for the data app.
    """
    st.title("NBA Basketball Analytics")
    st.write(
        "Using data from the [Ball Don't Lie API](%s), for now data is uploaded daily"
        % "https://www.balldontlie.io/#introduction"
        + " at 6pm AEST."
    )
    st.write(
        "For the full data pipelines see the nba-basketball repos in on my"
        + " [Github](%s)." % "https://github.com/corey-cheung"
    )


def winning_color_df(data: pd.DataFrame, team: str = None) -> pd.DataFrame:
    """
    Assigns styling information to a DataFrame based on the 'home_team_win' column.
    Return a DataFrame of the same shape, with the styling info corresponding to the
    same cell of the original DataFrame.

    Parameters:
        data: The DataFrame to be styled, containing game data.
    """
    style_df = pd.DataFrame("", index=data.index, columns=data.columns)
    conditions = data["home_team_win"]
    style_df["home_team"] = conditions.apply(
        lambda x: "background-color:green" if x else "background-color:red"
    )
    style_df["home_team_score"] = conditions.apply(
        lambda x: "color:green" if x else "color:red"
    )
    style_df["visitor_team"] = conditions.apply(
        lambda x: "background-color:green" if not x else "background-color:red"
    )
    style_df["visitor_team_score"] = conditions.apply(
        lambda x: "color:green" if not x else "color:red"
    )

    if team:  # keep formatting for only specific team if provided
        home_team_selected = data["home_team"].apply(lambda x: x == team)
        visitor_team_selected = data["visitor_team"].apply(lambda x: x == team)
        style_df["home_team"] = style_df.apply(
            lambda x: x["home_team"] if home_team_selected.iloc[x.name] else None,
            axis=1,
        )
        style_df["visitor_team"] = style_df.apply(
            lambda x: x["visitor_team"] if visitor_team_selected.iloc[x.name] else None,
            axis=1,
        )
    return style_df


def most_recent_games() -> None:
    """
    Get the most recent games and present as a table in the data app. Format the table
    so that winning teams are green and losing teams are red.
    """

    latest_games = pd.read_csv("src/datasets/latest_games.csv")
    latest_games_styled = latest_games.style.apply(
        winning_color_df, axis=None
    )  # apply to both index and columns axis
    st.header("Most recent games", divider="grey")
    st.write("Dates are in US timezones.")
    st.dataframe(latest_games_styled, hide_index=True)


def last_10_games() -> None:
    """
    Get the last 10 games for a given team that the user can select through a drop down
    button. Present as a table highlight the winning team, and text describing their
    current win streak.
    """

    st.header("Last 10 games by team", divider="grey")
    df_last_10_games = pd.read_csv("./src/datasets/last_10_games.csv")

    teams = duckdb.sql(
        "SELECT DISTINCT team_name FROM df_last_10_games ORDER BY team_name;"
    ).to_df()
    selected_team = st.selectbox("Team", teams)

    last_10_by_team = duckdb.sql(
        f"""
        SELECT * FROM df_last_10_games
        WHERE team_name = '{selected_team}';
        """
    ).to_df()
    wins = int(last_10_by_team["total_wins_last_10"][0])
    last_10_by_team = last_10_by_team[
        [
            "game_date",
            "home_team",
            "home_team_score",
            "visitor_team_score",
            "visitor_team",
            "season",
            "status",
            "home_team_win",
        ]
    ]
    last_10_by_team_styled = last_10_by_team.style.apply(
        winning_color_df, team=selected_team, axis=None
    )
    st.write(f"{selected_team} has won {wins} out of the last 10 games.")
    st.dataframe(last_10_by_team_styled, hide_index=True)


def select_player() -> tuple[str, pd.DataFrame]:
    """
    Create a drop down to select a player as well as an image for the selected player.
    """
    st.header("Player Stats", divider="grey")
    st.write(
        "Pick your favourite player below! A highly advanced artificial neural network "
        + "will generate a picture using just their name!"
    )
    df_player_averages = pd.read_csv("./src/datasets/season_stats.csv")
    players = duckdb.sql(
        """
        SELECT
            DISTINCT
            first_name || ' ' || last_name || ' ID: ' || player_id::INT AS player_name
        FROM df_player_averages
        WHERE player_name IS NOT NULL
        ORDER BY player_name;
        """
    ).to_df()
    players = pd.concat(
        [  # put LeGoat first as drop down example
            players[players["player_name"] == "LeBron James ID: 237"],
            players[players["player_name"] != "LeBron James ID: 237"],
        ]
    ).reset_index(drop=True)
    selected_player = st.selectbox("Player", players, index=0)
    selected_player_id = selected_player.split("ID: ")[-1]
    if selected_player == "LeBron James ID: 237":
        st.image("./assets/lebron.png", caption="LeBron James")
    else:
        st.image("./assets/not_lebron.jpeg", caption="NOT LeBron James")

    return selected_player_id, players


def player_stats(selected_player_id) -> None:
    """
    Show the chosen player's career statistics.
    """
    df_player_averages = pd.read_csv("./src/datasets/season_stats.csv")
    career_totals = duckdb.sql(
        f"""
        SELECT
            season_number,
            career_pts,
            career_reb,
            career_ast,
            career_blk,
            career_stl
        FROM df_player_averages
        WHERE player_id = {selected_player_id}
        ORDER BY season_number
        """
    ).to_df()
    left, middle, right = st.columns(3)
    with left:
        choose_pts = st.checkbox("Points", True)
    with middle:
        choose_reb = st.checkbox("Rebounds")
    with right:
        choose_ast = st.checkbox("Assists")
    left, middle, nothing = st.columns(3)
    with left:
        choose_blk = st.checkbox("Blocks")
    with middle:
        choose_stl = st.checkbox("Steals")

    df = pd.DataFrame()
    df["season_number"] = career_totals["season_number"]
    if choose_pts:
        df["career_pts"] = career_totals["career_pts"]
    if choose_reb:
        df["career_reb"] = career_totals["career_reb"]
    if choose_ast:
        df["career_ast"] = career_totals["career_ast"]
    if choose_blk:
        df["career_blk"] = career_totals["career_blk"]
    if choose_stl:
        df["career_stl"] = career_totals["career_stl"]
    st.area_chart(df, x="season_number")

    season_averages = duckdb.sql(
        f"""
        SELECT
            first_name || ' ' || last_name AS player_name,
            season::TEXT AS season,
            total_games,
            avg_pts,
            avg_reb,
            avg_ast,
            avg_blk,
            avg_stl,
            avg_turnover,
            avg_fg_pct,
            avg_fg3_pct,
            avg_ft_pct,
        FROM df_player_averages
        WHERE player_id = {selected_player_id}
        ORDER BY season;
        """
    ).to_df()
    st.dataframe(season_averages, hide_index=True)


def compare_players(players: pd.DataFrame) -> None:
    """
    Compare the career stats of two players.
    """
    df_player_averages = pd.read_csv("./src/datasets/season_stats.csv")
    st.header("Compare Players", divider="grey")
    st.write("Compare the career stats of two players.")
    left, right = st.columns(2)
    with left:
        player1 = st.selectbox("Player 1", players)
        player1_id = player1.split("ID: ")[-1]
    with right:
        michael_jordan = int(
            players[players["player_name"] == "Michael Jordan ID: 2931"].index[0]
        )
        player2 = st.selectbox("Player 2", players, index=michael_jordan)
        player2_id = player2.split("ID: ")[-1]

    career_comparison = duckdb.sql(
        f"""
        WITH player1 AS (
            SELECT
                season_number,
                career_pts AS player1_pts,
                career_reb AS player1_reb,
                career_ast AS player1_ast,
                career_blk AS player1_blk,
                career_stl AS player1_stl
            FROM df_player_averages
            WHERE player_id = {player1_id}
        ),
        player2 AS (
            SELECT
                season_number,
                career_pts AS player2_pts,
                career_reb AS player2_reb,
                career_ast AS player2_ast,
                career_blk AS player2_blk,
                career_stl AS player2_stl
            FROM df_player_averages
            WHERE player_id = {player2_id}
        )
        SELECT *
        FROM player1
        FULL JOIN player2 USING(season_number)
        ORDER BY season_number
        """
    ).to_df()
    compare_stat = st.selectbox(
        "Game statistic", ["Points", "Rebounds", "Assists", "Blocks", "Steals"]
    )
    mapping = {
        "Points": ["player1_pts", "player2_pts"],
        "Rebounds": ["player1_reb", "player2_reb"],
        "Assists": ["player1_ast", "player2_ast"],
        "Blocks": ["player1_blk", "player2_blk"],
        "Steals": ["player1_stl", "player2_stl"],
    }
    st.line_chart(
        career_comparison,
        x="season_number",
        y=mapping[compare_stat],
        color=["#add2e4", "#f678a7"],
    )


def main():
    title_and_overview()
    most_recent_games()
    last_10_games()
    selected_player_id, players = select_player()
    player_stats(selected_player_id)
    compare_players(players)


if __name__ == "__main__":
    main()
