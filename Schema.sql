CREATE TABLE Department (
    DeptCode     NVARCHAR(50) PRIMARY KEY,
    Description  NVARCHAR(500),
    ManagerId    INT NULL
);

CREATE TABLE Branch (
    BranchId      INT IDENTITY PRIMARY KEY,
    BranchCode    NVARCHAR(50),
    OpeningHours  NVARCHAR(100),
    Email         NVARCHAR(100),
    Phone         NVARCHAR(20),
    ManagerId     INT NULL
);

CREATE TABLE Employee (
    EmpId        INT IDENTITY PRIMARY KEY,
    DeptCode     NVARCHAR(50) NOT NULL,
    BranchId     INT NOT NULL,
    ManagerId    INT NULL,
    HireDate     DATE,
    BirthDate    DATE,
    Email        NVARCHAR(100),
    Phone        NVARCHAR(20),
    Address      NVARCHAR(200),
    WorkHours    INT,

    CONSTRAINT FK_Employee_Department
        FOREIGN KEY (DeptCode) REFERENCES Department(DeptCode),

    CONSTRAINT FK_Employee_Branch
        FOREIGN KEY (BranchId) REFERENCES Branch(BranchId),

    CONSTRAINT FK_Employee_Manager
        FOREIGN KEY (ManagerId) REFERENCES Employee(EmpId)
);

CREATE TABLE Customer (
    CustomerId   INT IDENTITY PRIMARY KEY,
    SSN          NVARCHAR(20) UNIQUE NOT NULL,
    Gender       CHAR(1),
    RegDate      DATE,
    IsActive     BIT,
    Job          NVARCHAR(100),
    IncomeLevel  NVARCHAR(50)
);

CREATE TABLE Account (
    AccountId           INT IDENTITY PRIMARY KEY,
    IBAN                NVARCHAR(50) UNIQUE NOT NULL,
    CustomerId          INT NOT NULL,
    BranchId            INT NOT NULL,
    Status              NVARCHAR(20),
    Currency            NVARCHAR(10),
    Balance             DECIMAL(18,2),
    LastTransactionDate DATETIME,

    CONSTRAINT FK_Account_Customer
        FOREIGN KEY (CustomerId) REFERENCES Customer(CustomerId),

    CONSTRAINT FK_Account_Branch
        FOREIGN KEY (BranchId) REFERENCES Branch(BranchId)
);

CREATE TABLE [Transaction] (
    TransactionId   INT IDENTITY PRIMARY KEY,
    AccountId       INT NOT NULL,
    EmpId           INT NOT NULL,
    Amount          DECIMAL(18,2),
    Status          NVARCHAR(20),
    TransactionDate DATE,
    TransactionTime TIME,

    CONSTRAINT FK_Transaction_Account
        FOREIGN KEY (AccountId) REFERENCES Account(AccountId),

    CONSTRAINT FK_Transaction_Employee
        FOREIGN KEY (EmpId) REFERENCES Employee(EmpId)
);