#!/usr/bin/env python

import pandas as pd
import streamlit as st
import duckdb


def title_and_overview():
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


def most_recent_games():
    """
    Get the most recent games and present as a table in the data app. Format the table
    so that winning teams are green and losing teams are red.
    """

    latest_games = pd.read_csv("src/datasets/latest_games.csv")
    latest_games_styled = latest_games.style.apply(
        winning_color_df, axis=None
    )  # apply to both index and columns axis
    st.header("Most recent games", divider="grey")
    st.write("Dates are in US timezones")
    st.table(latest_games_styled)


def last_10_games():
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
    st.table(last_10_by_team_styled)


def player_averages():
    st.header("Player Stats", divider="grey")
    df_player_averages = pd.read_csv("./src/datasets/season_stats.csv")
    players = duckdb.sql(
        """
        SELECT DISTINCT first_name || ' ' || last_name AS player_name
        FROM df_player_averages
        WHERE player_name IS NOT NULL
        ORDER BY player_name;
        """
    ).to_df()
    players = pd.concat(
        [ # put LeGoat first as drop down example
            players[players["player_name"] == "LeBron James"],
            players[players["player_name"] != "LeBron James"],
        ]
    ).reset_index(drop=True)
    selected_player = st.selectbox("Player", players, index=0)


if __name__ == "__main__":
    title_and_overview()
    most_recent_games()
    last_10_games()
    player_averages()
