#!/usr/bin/env python

"""
Run the queries in src/sql and load it into CSVs in src/datasets.
"""

import os
import duckdb
import pandas as pd

def query_duckdb(query: str) -> list[tuple]:
    """
    Query duck db and return the result in list of tuples.
    Parameters:
        query: The select query to run against postgres
    """
    duckdb_path = os.environ.get("AIRFLOW_VAR_DUCKDB_PATH")
    with duckdb.connect(duckdb_path) as conn:
        return conn.execute(query).df()

def main():
    """
    Run the queries in src/sql and load it into CSVs in src/datasets.
    """
    queries = [query for query in os.listdir("./src/sql") if query.endswith(".sql")]

    for query in queries:
        name = query.replace(".sql","")
        with open(f"./src/sql/{query}", "r", encoding="UTF-8") as file:
            sql = file.read()
            df = query_duckdb(sql)
            df.to_csv(f"./src/datasets/{name}.csv", index=False)

if __name__ == "__main__":
    main()
