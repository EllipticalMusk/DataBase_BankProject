# DataBase_BankProject — Documentation

## Project Overview

A small desktop banking management example written in Python using `tkinter` for the UI and ODBC (`pyodbc`) to connect to a SQL Server database. The app provides CRUD operations for Department, Branch, Employee, Customer, Account, and Transaction entities and supports multi-row selection with bulk delete and basic column sorting in the tables.

## Files (workspace)

- [app.py](app.py) — main application and UI wiring. Creates the Tk root, tabs, form handlers and calls into helpers and data modules.
- [db.py](db.py) — low-level DB connection factory using `pyodbc`.
- [data.py](data.py) — simple helpers: `execute(query, params=())` and `fetch(query)` which use `db.get_connection()`.
- [helpers.py](helpers.py) — UI helper functions: `make_form`, `make_table`, selection handling, `tree_sort`, `delete_selected`, `_make_edit_dialog`, and `_format_cell`.
- [Schema.sql](Schema.sql) — SQL schema to create the database tables (not modified by this change).
- [SeedData.sql](SeedData.sql) — optional seed data for the schema.
- [requirements.txt](requirements.txt) — external dependency list (includes `pyodbc`).
- [README.md](README.md) — project README.

## Prerequisites

- Python 3.8+ (the repo was authored/tested on Windows).
- Install `pyodbc`:

```bash
pip install -r requirements.txt
```

- Install an appropriate ODBC driver for SQL Server (e.g., ODBC Driver 17/18 for SQL Server) or change `db.py` to match your database vendor.

## Quick Setup

1. Create the database and apply the schema and seed data. Example using `sqlcmd` or SSMS for SQL Server, or using `sqlite3` if you adapt `db.py`.
2. Update `db.py` connection string if necessary (server, database, auth).
3. Run the app:

```bash
python app.py
```

## Design & Module Responsibilities

- `db.py` — only responsibility: return a DB connection. Swap driver or connection info here to target a different server.

- `data.py` — thin wrapper around `db.get_connection()`:
  - `execute(query, params=())` — executes a parameterized statement and commits.
  - `fetch(query)` — executes a read-only query and returns rows.

- `helpers.py` — central UI utilities to keep `app.py` smaller:
  - `make_form(parent, fields)` — builds a simple label+entry vertical form and returns a dict of Entry widgets.
  - `make_table(parent, columns, headings, with_select=False)` — returns a `ttk.Treeview` configured as a table. If `with_select=True` a selection column (`_sel`) is added which displays a checkbox glyph (`☐`/`☑`).
  - Selection handling: clicking the first column toggles the checkbox; the checkbox state is stored in the `_sel` column value.
  - `tree_sort(tree, col, reverse=False)` — sorts rows by the given column (skips the `_sel` column). Numeric values are coerced to float for numeric sorting.
  - `delete_selected(tree, delete_sql, id_pos_with_select=1, id_is_int=False, reload_callback=None)` — deletes all rows that have `_sel` set to `☑`. It calls `data.execute()` for each selected ID and reloads the table via `reload_callback` when provided.
  - `_make_edit_dialog` — small modal dialog builder for editing a single-row record.
  - `_format_cell` — utility to format cell values (dates, bytes, lists).

- `app.py` — UI wiring and business logic per-tab. Each tab follows the same pattern:
  1. Create a tab and form fields with `make_form`.
  2. Create a table via `make_table(..., with_select=True)`.
  3. Implement `load_<entity>()` which calls `fetch()` and inserts rows into the tree; when `with_select` is enabled the code prepends the `☐` checkbox cell to each row inserted.
  4. Implement `add_<entity>()`, `edit_<entity>()`, `delete_<entity>()`, and a "Delete Selected" button that calls `delete_selected` with a delete SQL statement.

## How Bulk Delete Works

- Tables created with `with_select=True` have a `_sel` column as the first column. Clicking in that column toggles the checkbox glyph.
- The "Delete Selected" button calls `delete_selected(tree, delete_sql, id_pos_with_select=1, id_is_int=<bool>, reload_callback=load_fn)` where `id_pos_with_select=1` indicates the ID column is at position 1 in the `values` tuple because `_sel` is at position 0.

## Sorting Behavior

- Column headers (except the selection column) are wired to call `tree_sort` which will reorder the rows in the tree.

## Extending / Changing Database Backend

- To use SQLite instead of SQL Server, update `db.py` to return an `sqlite3.Connection` and adjust SQL date functions (the app uses `GETDATE()` in transaction inserts for SQL Server).
- To use MySQL, install `mysql-connector-python` and change `db.get_connection()` accordingly.

## Troubleshooting

- If the UI hangs or errors while connecting, confirm the ODBC driver is installed and the `db.py` connection string is correct.
- If `tkinter` widgets appear incorrectly, verify you are running on a supported platform and Python distribution (Windows typically bundles `tkinter`).

## Notes & TODOs

- Consider centralizing SQL for each entity (e.g., `sql/` folder or constants in `data.py`).
- Add unit tests for `data.py` using a test database or an in-memory SQLite alternative.
- Consider using parameterized batch deletes instead of row-by-row deletes for improved performance on large selections.

---

If you want, I can also:

- Add inline docstrings to `helpers.py` and `data.py`.
- Generate an API-style reference of all functions with parameter/return details.
- Add a `requirements-dev.txt` for development tools.
