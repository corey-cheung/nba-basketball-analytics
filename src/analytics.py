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
    """
    Set up title and overview for the data app.
    """
    ball_dont_lie_url = "https://www.balldontlie.io/#introduction"
    st.title("NBA Basketball Analytics")
    st.write("Using data from the [Ball Don't Lie API](%s)" % ball_dont_lie_url)


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

    if team:
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
    Get the most recent games from DuckDB and present as a table in the data app. Format
    the table so that winning teams are green and losing teams are red.
    """

    latest_games = pd.read_csv("src/datasets/latest_games.csv")
    latest_games_styled = latest_games.style.apply(
        winning_color_df, axis=None
    )  # apply to both index and columns axis
    st.header("Most recent games", divider="grey")
    st.write(
        "Dates are in US timezones and data only gets updated at 6pm AEST, cause it"
        + " ain't that serious!"
    )
    st.table(latest_games_styled)


if __name__ == "__main__":
    title_and_overview()
    most_recent_games()
