#!/usr/bin/env python

import streamlit as st
import duckdb
import os

ball_dont_lie_url = "https://www.balldontlie.io/home.html#introduction"

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
st.header("Completed games today", divider="red")
test_game = query_duckdb(
    """
    SELECT
        game_date::DATE AS game_date,
        home_team,
        visitor_team,
        home_team_score,
        visitor_team_score,
        season,
        home_team_win,
        status
    FROM main_mart.fct_game
    WHERE game_date = (
        SELECT MAX(game_date)
        FROM main_mart.fct_game
        WHERE status = 'Final'
    );
    """
    )
print(type(test_game))
st.table(test_game)
