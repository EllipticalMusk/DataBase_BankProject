
# Database Documentation

This document summarizes the database schema and how the application
connects to and uses the database. The canonical schema is in
[Schema.sql](Schema.sql).

## Overview

- Database name: `Bank` (see `db.get_connection()` in `db.py`)
- Access: Windows (trusted) authentication via ODBC Driver 17 for SQL Server

See `db.py` for the connection string used by the application.

## Connection (how the app connects)

- The app opens connections using `pyodbc` and the helper function
	`get_connection()` defined in `db.py`.
- The connection string uses `DRIVER={ODBC Driver 17 for SQL Server}`,
	`SERVER=localhost`, `DATABASE=Bank`, and `Trusted_Connection=yes`.

Callers obtain a connection and must close it when finished; the
application's `data.py` helper functions (`execute`, `fetch`) wrap that
pattern for convenience.

## Tables and key columns

Below are the tables defined in [Schema.sql](Schema.sql) with the most
important columns and notes about relationships.

### Department

- `DeptCode` NVARCHAR(50) PRIMARY KEY — business key for a department
- `Description` NVARCHAR(500)
- `ManagerId` INT NULL — optional FK to `Employee.EmpId` (manager)

Notes: departments are referenced by `Employee.DeptCode`.

### Branch

- `BranchId` INT IDENTITY PRIMARY KEY — surrogate integer id
- `BranchCode` NVARCHAR(50)
- `OpeningHours` NVARCHAR(100)
- `Email` NVARCHAR(100)
- `Phone` NVARCHAR(20)
- `ManagerId` INT NULL — optional FK to `Employee.EmpId`

Notes: branches are referenced by `Employee.BranchId` and `Account.BranchId`.

### Employee

- `EmpId` INT IDENTITY PRIMARY KEY
- `DeptCode` NVARCHAR(50) NOT NULL — FK -> `Department(DeptCode)`
- `BranchId` INT NOT NULL — FK -> `Branch(BranchId)`
- `ManagerId` INT NULL — FK -> `Employee(EmpId)` (self-relationship)
- `HireDate`, `BirthDate`, `Email`, `Phone`, `Address`, `WorkHours`

Notes: employees belong to a department and branch; there is a
recursive manager relationship allowing hierarchical staff structures.

### Customer

- `CustomerId` INT IDENTITY PRIMARY KEY
- `SSN` NVARCHAR(20) UNIQUE NOT NULL — unique identifier for customers
- `Gender` CHAR(1), `RegDate` DATE, `IsActive` BIT
- `Job`, `IncomeLevel`

Notes: customers are referenced by `Account.CustomerId`.

### Account

- `AccountId` INT IDENTITY PRIMARY KEY
- `IBAN` NVARCHAR(50) UNIQUE NOT NULL
- `CustomerId` INT NOT NULL — FK -> `Customer(CustomerId)`
- `BranchId` INT NOT NULL — FK -> `Branch(BranchId)`
- `Status`, `Currency`, `Balance` DECIMAL(18,2)
- `LastTransactionDate` DATETIME

Notes: balances use DECIMAL(18,2). Account operations in the app use
`AccountId` to reference accounts. Ensure `IBAN` uniqueness is kept.

### Transaction (table name: `[Transaction]`)

- `TransactionId` INT IDENTITY PRIMARY KEY
- `AccountId` INT NOT NULL — FK -> `Account(AccountId)`
- `EmpId` INT NOT NULL — FK -> `Employee(EmpId)`
- `Amount` DECIMAL(18,2)
- `Status` NVARCHAR(20)
- `TransactionDate` DATE, `TransactionTime` TIME

Notes: the app inserts transactions using SQL Server's `GETDATE()` to
set the transaction timestamp. Keep in mind the table name is a SQL
keyword, hence the use of square brackets: `[Transaction]`.

## Foreign Keys / Relationships Summary

- `Employee.DeptCode` -> `Department.DeptCode`
- `Employee.BranchId` -> `Branch.BranchId`
- `Employee.ManagerId` -> `Employee.EmpId` (self-FK)
- `Branch.ManagerId` -> `Employee.EmpId` (optional)
- `Department.ManagerId` -> `Employee.EmpId` (optional)
- `Account.CustomerId` -> `Customer.CustomerId`
- `Account.BranchId` -> `Branch.BranchId`
- `Transaction.AccountId` -> `Account.AccountId`
- `Transaction.EmpId` -> `Employee.EmpId`

## Common example queries

- Select all accounts with customer SSN and branch code:

```sql
SELECT a.AccountId, a.IBAN, c.SSN, b.BranchCode, a.Balance
FROM Account a
JOIN Customer c ON a.CustomerId = c.CustomerId
JOIN Branch b ON a.BranchId = b.BranchId;
```

- Insert a transaction (application uses parameterized statements):

```sql
INSERT INTO [Transaction] (AccountId, EmpId, Amount, TransactionDate)
VALUES (?, ?, ?, GETDATE());
```

- Update an account balance (do this inside a transaction in real apps):

```sql
UPDATE Account
SET Balance = Balance + ?
WHERE AccountId = ?;
```

## Operational notes and recommendations

- Use parameterized queries from the application (the code uses `?`
	placeholders with `pyodbc`) to protect against SQL injection.
- Consider adding indexes on frequently queried columns such as
	`Customer.SSN`, `Account.IBAN`, `Transaction.TransactionDate`.
- When performing multi-step operations (e.g., creating a transaction
	and updating an account balance) use explicit DB transactions to
	ensure atomicity.
- The schema uses identity columns for numeric primary keys and
	NVARCHAR for textual keys; be consistent when joining and casting.

## Seed data

Seed data is available in `SeedData.sql` (if present) and can be used
to populate the database for development/testing.

## Where to find code that uses the DB

- Connection helper: `db.py` (`get_connection()`)
- Simple data helpers: `data.py` (`execute`, `fetch`)
- GUI usage and example queries: `app.py` — the UI code calls
	`execute()` and `fetch()` for CRUD operations on these tables.


