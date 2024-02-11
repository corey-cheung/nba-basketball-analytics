#!/usr/bin/env python

import pandas as pd
import streamlit as st
import duckdb
import os

ball_dont_lie_url = "https://www.balldontlie.io/#introduction"

def query_duckdb(query: str) -> list[tuple]:
    """
    Query duck db and return the result in list of tuples.

    Parameters:
        query: The select query to run against postgres
    """
    duckdb_path = os.environ.get("AIRFLOW_VAR_DUCKDB_PATH")
    with duckdb.connect(duckdb_path) as conn:

        return conn.execute(query).df()

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

test_game = query_duckdb(
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

test_game_styled = test_game.style.apply(winning_color_df, axis=None)
df = winning_color_df(test_game)
print(df)

print(test_game)
st.header("Latest games", divider="red")
st.write("Data only gets updated at 6pm AEST, cause it ain't that serious!")
st.table(test_game_styled)
