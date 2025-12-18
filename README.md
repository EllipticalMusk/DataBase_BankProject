# DataBase Bank Project

Done by: Omar Hamdy Khalil -Seif Sherif Hasan -Ahmed ElSayed Ghoniem
 

## Project Overview

This repository contains a small example banking database project. It includes the database schema, seed data, and a minimal Python app to interact with the database.

## Technologies

- Python 3.8+
- SQL (Schema.sql)
- (Optional) SQLite or MySQL for the database

## Prerequisites

- Python 3.8 or newer installed
- `sqlite3` (optional) or a MySQL server if you prefer

## Setup (Windows)

1. Clone the repository:

	git clone <repo-url>
	cd DataBase_BankProject

2. (Optional) Create and activate a virtual environment:

	python -m venv env
	.\env\Scripts\activate

3. Install dependencies if you have a `requirements.txt` file (none provided by default):

	pip install -r requirements.txt

4. Create the database and apply the schema and seed data.

	- Using SQLite (quick, local):

	  sqlite3 bank.db < Schema.sql
	  sqlite3 bank.db < SeedData.sql

	- Using MySQL (example):

	  mysql -u <user> -p <database_name> < Schema.sql
	  mysql -u <user> -p <database_name> < SeedData.sql

	Replace placeholders with your actual user/database names.

## Usage

Run the minimal app (example):

	python app.py

Adjust the app configuration if it expects a specific database or connection string.
