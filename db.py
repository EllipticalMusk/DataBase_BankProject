"""Database helper utilities.

This module provides a small helper to obtain a connection to the
local SQL Server database used by the application.
"""

import pyodbc


def get_connection():
    """Return a new pyodbc connection to the Bank database.

    The function creates and returns a live connection object. Callers
    are responsible for closing the connection when finished.

    Returns:
        pyodbc.Connection: active DB connection to the `Bank` database.
    """
    # Use ODBC Driver 17 for SQL Server with Windows authentication
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=Bank;"
        "Trusted_Connection=yes;"
    )
    return conn
