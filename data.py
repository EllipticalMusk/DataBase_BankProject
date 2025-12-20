"""Lightweight data access helpers.

This module exposes two convenience functions used throughout the
application: `execute` for commands that modify data, and `fetch` for
retrieving query results. Both functions obtain a connection from
`db.get_connection()` and ensure the connection is closed after use.
"""

from db import get_connection


def execute(query, params=()):
    """Execute a write/update/delete SQL statement.

    Opens a connection, executes the provided parameterized query,
    commits the transaction and closes the connection. Exceptions are
    propagated to the caller.

    Args:
        query (str): SQL statement with placeholders (e.g. ? for pyodbc).
        params (tuple): parameters to bind to the query.
    """
    conn = get_connection()
    cur = conn.cursor()
    # perform the operation and persist changes
    cur.execute(query, params)
    conn.commit()
    # ensure we always close the connection to release resources
    conn.close()


def fetch(query):
    """Execute a read-only SQL query and return all rows.

    Args:
        query (str): SQL select statement to execute.

    Returns:
        list: sequence of rows returned by the query (pyodbc.Row objects).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    # close the connection before returning results
    conn.close()
    return rows
