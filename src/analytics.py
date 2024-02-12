#!/usr/bin/env python

import pandas as pd
import streamlit as st
import duckdb
import os


def query_duckdb(query: str) -> list[tuple]:
    """
    Query duck db and return the result in list of tuples.

    Parameters:
        query: The select query to run against postgres
    """
    duckdb_path = os.environ.get("AIRFLOW_VAR_DUCKDB_PATH")
    with duckdb.connect(duckdb_path) as conn:
        return conn.execute(query).df()


def title_and_overview():
    ball_dont_lie_url = "https://www.balldontlie.io/#introduction"
    st.title("NBA Basketball Analytics")
    st.write("Using data from the [Ball Don't Lie API](%s)" % ball_dont_lie_url)


def winning_color_df(data: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns styling information to a DataFrame based on the 'home_team_win' column.
    Return a DataFrame of the same shape, with the styling info corresponding to the
    same cell of the original DataFrame.

    Parameters:
        data: The DataFrame to be styled, containing game data.
    """
    df = pd.DataFrame('', index=data.index, columns=data.columns)
    conditions = data['home_team_win']
    df['home_team'] = conditions.apply(lambda x: "background-color:green" if x else "background-color:red")
    df['home_team_score'] = conditions.apply(lambda x: "color:green" if x else "color:red")
    df['visitor_team'] = conditions.apply(lambda x: "background-color:green" if not x else "background-color:red")
    df['visitor_team_score'] = conditions.apply(lambda x: "color:green" if not x else "color:red")
    return df


def most_recent_games():
    latest_games = query_duckdb(
        """
        SELECT
            (game_date::DATE)::TEXT AS game_date,
            home_team,
            home_team_score,
            visitor_team_score,
            visitor_team,
            season,
            status,
            home_team_win
        FROM main_mart.fct_game
        WHERE game_date = (
            SELECT MAX(game_date)
            FROM main_mart.fct_game
            WHERE status = 'Final'
        );
        """
        )

    latest_games_styled = latest_games.style.apply(winning_color_df, axis=None)  # apply to both index and columns axis
    df = winning_color_df(latest_games)
    st.header("Most recent games", divider="red")
    st.write("Dates are in US timezones and data only gets updated at 6pm AEST, cause it ain't that serious!")
    st.table(latest_games_styled)

def team_info():

    st.header("Last 10 games", divider="red")

    teams = query_duckdb(
        """
        SELECT
            team_name_abbreviation AS team
        FROM main_mart.dim_team
        WHERE city <> ''
        ;
        """
    )
    selected_team = st.selectbox("Team", teams)

    lastest_team_games = query_duckdb(
        f"""
        SELECT
            (game_date::DATE)::TEXT AS game_date,
            home_team,
            home_team_score,
            visitor_team,
            visitor_team_score,
            home_team_win
        FROM main_mart.fct_game
        WHERE '{selected_team}' = home_team OR '{selected_team}' = visitor_team
        ORDER BY game_date DESC
        LIMIT 10
        ;
        """
    )

    games_won = query_duckdb(
        f"""
        WITH last_10 AS (
            SELECT
                (game_date::DATE)::TEXT AS game_date,
                home_team,
                home_team_score,
                visitor_team,
                visitor_team_score,
                home_team_win
            FROM main_mart.fct_game
            WHERE '{selected_team}' = home_team OR '{selected_team}' = visitor_team
            ORDER BY game_date DESC
            LIMIT 10
        )
        SELECT SUM(CASE WHEN ('{selected_team}' = CASE WHEN home_team_win THEN home_team ELSE visitor_team END) THEN 1 ELSE 0 END) games_won
        from last_10
        """
    )
    games_won = int(games_won["games_won"][0])

    st.write(f"{selected_team} has won {games_won} out of the last 10 games.")
    lastest_team_games_styled = lastest_team_games.style.apply(winning_color_df, axis=None)
    st.table(lastest_team_games_styled)

if __name__ == "__main__":
    title_and_overview()
    most_recent_games()
    team_info()