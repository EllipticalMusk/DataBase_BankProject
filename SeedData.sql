/* Created by GitHub Copilot in SSMS - review carefully before executing */

SET XACT_ABORT ON;
BEGIN TRANSACTION;

-- Insert 10 Department rows and capture their DeptCode values.
DECLARE @InsertedDept TABLE (DeptCode nvarchar(50));
DECLARE @i INT = 1;
WHILE @i <= 10
BEGIN
    DECLARE @dc nvarchar(50) = 'DPT_' + LEFT(CONVERT(varchar(36), NEWID()), 8);
    INSERT INTO dbo.Department (DeptCode, Description, ManagerId)
    VALUES (@dc, 'Department ' + CAST(@i AS varchar(3)), NULL);
    INSERT INTO @InsertedDept (DeptCode) VALUES (@dc);
    SET @i = @i + 1;
END 

-- Branches (capture identity values)
DECLARE @Branch1Id INT, @Branch2Id INT;

INSERT INTO dbo.Branch (BranchCode, OpeningHours, Email, Phone, ManagerId)
VALUES ('BR001', '09:00-17:00', 'branch1@example.com', '555-0101', NULL);
SET @Branch1Id = SCOPE_IDENTITY();

INSERT INTO dbo.Branch (BranchCode, OpeningHours, Email, Phone, ManagerId)
VALUES ('BR002', '10:00-18:00', 'branch2@example.com', '555-0102', NULL);
SET @Branch2Id = SCOPE_IDENTITY();

-- Customers
DECLARE @Cust1 INT, @Cust2 INT;

INSERT INTO dbo.Customer (SSN, Gender, RegDate, IsActive, Job, IncomeLevel)
VALUES ('123-45-6789', 'M', '2022-06-01', 1, 'Engineer', 'Medium');
SET @Cust1 = SCOPE_IDENTITY();

INSERT INTO dbo.Customer (SSN, Gender, RegDate, IsActive, Job, IncomeLevel)
VALUES ('987-65-4321', 'F', '2023-01-15', 1, 'Teacher', 'Low');
SET @Cust2 = SCOPE_IDENTITY();

-- Employees (create managers first)
DECLARE @EmpManager INT, @EmpStaff INT;

INSERT INTO dbo.Employee (DeptCode, BranchId, ManagerId, HireDate, BirthDate, Email, Phone, Address, WorkHours)
VALUES ('HR', @Branch1Id, NULL, '2018-03-12', '1980-07-20', 'alice.manager@example.com', '555-0201', '1 Main St', 40);
SET @EmpManager = SCOPE_IDENTITY();

INSERT INTO dbo.Employee (DeptCode, BranchId, ManagerId, HireDate, BirthDate, Email, Phone, Address, WorkHours)
VALUES ('HR', @Branch1Id, @EmpManager, '2021-09-01', '1992-11-05', 'bob.staff@example.com', '555-0202', '2 Main St', 40);
SET @EmpStaff = SCOPE_IDENTITY();

-- Accounts
DECLARE @Acc1 INT, @Acc2 INT;

INSERT INTO dbo.Account (IBAN, CustomerId, BranchId, Status, Currency, Balance, LastTransactionDate)
VALUES ('GB00BANK0000000001', @Cust1, @Branch1Id, 'Open', 'USD', 2500.00, GETDATE());
SET @Acc1 = SCOPE_IDENTITY();

INSERT INTO dbo.Account (IBAN, CustomerId, BranchId, Status, Currency, Balance, LastTransactionDate)
VALUES ('GB00BANK0000000002', @Cust2, @Branch2Id, 'Open', 'EUR', 150.50, GETDATE());
SET @Acc2 = SCOPE_IDENTITY();

-- Transactions
INSERT INTO dbo.[Transaction] (AccountId, EmpId, Amount, Status, TransactionDate, TransactionTime)
VALUES (@Acc1, @EmpStaff, 100.00, 'Completed', CAST(GETDATE() AS DATE), CAST(GETDATE() AS TIME));

COMMIT TRANSACTION;