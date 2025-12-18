import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from db import get_connection
from data import execute, fetch
from helpers import make_form, make_table, _format_cell, _make_edit_dialog, delete_selected, tree_sort


# ------------------- UI SETUP -------------------

root = tk.Tk()
root.title("Bank Management System")
root.geometry("1000x650")

# --- Theming & styling ---
style = ttk.Style()
try:
    style.theme_use('clam')
except Exception:
    pass
DEFAULT_FONT = ('Segoe UI', 10)
style.configure('.', font=DEFAULT_FONT)
style.configure('TButton', padding=6)
style.configure('Treeview', rowheight=24, font=DEFAULT_FONT)
style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

import helpers
helpers.root = root

# =================== DEPARTMENT ===================

dept_tab = ttk.Frame(notebook)
notebook.add(dept_tab, text="Department")

dept_fields = make_form(dept_tab, ["Dept Code", "Description"])

def add_department():
    code = dept_fields["Dept Code"].get().strip()
    desc = dept_fields["Description"].get().strip()
    if not code or not desc:
        messagebox.showerror("Validation error", "Dept Code and Description are required.")
        return
    try:
        execute(
            "INSERT INTO Department (DeptCode, Description) VALUES (?,?)",
            (code, desc)
        )
        load_departments()
        dept_fields["Dept Code"].delete(0, tk.END)
        dept_fields["Description"].delete(0, tk.END)
        messagebox.showinfo("Success", "Department added.")
    except Exception as e:
        messagebox.showerror("Error adding department", str(e))

ttk.Button(dept_tab, text="Add", command=add_department).pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(dept_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))

ttk.Button(btn_frame, text="Edit", command=lambda: edit_department()).pack(side='left')
ttk.Button(btn_frame, text="Delete", command=lambda: delete_department()).pack(side='left', padx=6)
ttk.Button(btn_frame, text="Delete Selected", command=lambda: delete_selected(dept_table, 'DELETE FROM Department WHERE DeptCode = ?', 1, False, load_departments)).pack(side='left', padx=6)

dept_table = make_table(dept_tab, ("Code","Desc"), ("Dept Code","Description"), with_select=True)

def load_departments():
    dept_table.delete(*dept_table.get_children())
    for i, r in enumerate(fetch("SELECT DeptCode, Description FROM Department")):
        vals = tuple(_format_cell(x) for x in r)
        if dept_table['columns'] and dept_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        dept_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_department():
    sel = dept_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a department to delete.')
        return
    vals_full = dept_table.item(sel[0], 'values')
    vals = vals_full[1:]
    code = vals[0]
    if not messagebox.askyesno('Confirm', f'Delete department {code}?'):
        return
    try:
        execute('DELETE FROM Department WHERE DeptCode = ?', (code,))
        load_departments()
        messagebox.showinfo('Deleted', 'Department deleted.')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def edit_department():
    sel = dept_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a department to edit.')
        return
    vals_full = dept_table.item(sel[0], 'values')
    vals = vals_full[1:]
    orig_code = vals[0]
    def _save(data):
        new_code = data['Dept Code']
        desc = data['Description']
        if not new_code or not desc:
            raise ValueError('Both fields required')
        execute('UPDATE Department SET DeptCode=?, Description=? WHERE DeptCode=?', (new_code, desc, orig_code))
        load_departments()
        messagebox.showinfo('Saved', 'Department updated.')
    _make_edit_dialog('Edit Department', ['Dept Code','Description'], vals, _save)

load_departments()

# =================== BRANCH ===================

branch_tab = ttk.Frame(notebook)
notebook.add(branch_tab, text="Branch")

branch_fields = make_form(branch_tab, ["Branch Code", "Email", "Phone"])

def add_branch():
    code = branch_fields["Branch Code"].get().strip()
    email = branch_fields["Email"].get().strip()
    phone = branch_fields["Phone"].get().strip()
    if not code or not email:
        messagebox.showerror("Validation error", "Branch Code and Email are required.")
        return
    try:
        execute(
            "INSERT INTO Branch (BranchCode, Email, Phone) VALUES (?,?,?)",
            (code, email, phone)
        )
        load_branches()
        branch_fields["Branch Code"].delete(0, tk.END)
        branch_fields["Email"].delete(0, tk.END)
        branch_fields["Phone"].delete(0, tk.END)
        messagebox.showinfo("Success", "Branch added.")
    except Exception as e:
        messagebox.showerror("Error adding branch", str(e))

ttk.Button(branch_tab, text="Add", command=add_branch).pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(branch_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
ttk.Button(btn_frame, text='Edit', command=lambda: edit_branch()).pack(side='left')
ttk.Button(btn_frame, text='Delete', command=lambda: delete_branch()).pack(side='left', padx=6)
ttk.Button(btn_frame, text='Delete Selected', command=lambda: delete_selected(branch_table, 'DELETE FROM Branch WHERE BranchId = ?', 1, True, load_branches)).pack(side='left', padx=6)

branch_table = make_table(branch_tab, ("ID","Code","Email","Phone"), ("ID","Code","Email","Phone"), with_select=True)

def load_branches():
    branch_table.delete(*branch_table.get_children())
    for i, r in enumerate(fetch("SELECT BranchId, BranchCode, Email, Phone FROM Branch")):
        vals = tuple(_format_cell(x) for x in r)
        if branch_table['columns'] and branch_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        branch_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_branch():
    sel = branch_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a branch to delete.')
        return
    vals_full = branch_table.item(sel[0], 'values')
    vals = vals_full[1:]
    bid = vals[0]
    if not messagebox.askyesno('Confirm', f'Delete branch {bid}?'):
        return
    try:
        execute('DELETE FROM Branch WHERE BranchId = ?', (int(bid),))
        load_branches()
        messagebox.showinfo('Deleted', 'Branch deleted.')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def edit_branch():
    sel = branch_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a branch to edit.')
        return
    vals_full = branch_table.item(sel[0], 'values')
    vals = vals_full[1:]
    bid = vals[0]
    def _save(data):
        code = data['Branch Code']
        email = data['Email']
        phone = data['Phone']
        if not code or not email:
            raise ValueError('Branch Code and Email required')
        execute('UPDATE Branch SET BranchCode=?, Email=?, Phone=? WHERE BranchId=?', (code, email, phone, int(bid)))
        load_branches()
        messagebox.showinfo('Saved', 'Branch updated.')
    _make_edit_dialog('Edit Branch', ['Branch Code','Email','Phone'], vals[1:], _save)

load_branches()

# =================== EMPLOYEE ===================

emp_tab = ttk.Frame(notebook)
notebook.add(emp_tab, text="Employee")

emp_fields = make_form(emp_tab, ["Dept Code", "Branch ID", "Email"])

def add_employee():
    dept = emp_fields["Dept Code"].get().strip()
    branch = emp_fields["Branch ID"].get().strip()
    email = emp_fields["Email"].get().strip()
    if not dept or not branch or not email:
        messagebox.showerror("Validation error", "Dept Code, Branch ID and Email are required.")
        return
    try:
        branch_id = int(branch)
    except Exception:
        messagebox.showerror("Validation error", "Branch ID must be an integer.")
        return
    try:
        execute(
            "INSERT INTO Employee (DeptCode, BranchId, Email) VALUES (?,?,?)",
            (dept, branch_id, email)
        )
        load_employees()
        emp_fields["Dept Code"].delete(0, tk.END)
        emp_fields["Branch ID"].delete(0, tk.END)
        emp_fields["Email"].delete(0, tk.END)
        messagebox.showinfo("Success", "Employee added.")
    except Exception as e:
        messagebox.showerror("Error adding employee", str(e))

ttk.Button(emp_tab, text="Add", command=add_employee).pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(emp_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
ttk.Button(btn_frame, text='Edit', command=lambda: edit_employee()).pack(side='left')
ttk.Button(btn_frame, text='Delete', command=lambda: delete_employee()).pack(side='left', padx=6)
ttk.Button(btn_frame, text='Delete Selected', command=lambda: delete_selected(emp_table, 'DELETE FROM Employee WHERE EmpId = ?', 1, True, load_employees)).pack(side='left', padx=6)

emp_table = make_table(emp_tab, ("ID","Dept","Branch","Email"), ("ID","Dept","Branch","Email"), with_select=True)

def load_employees():
    emp_table.delete(*emp_table.get_children())
    for i, r in enumerate(fetch("SELECT EmpId, DeptCode, BranchId, Email FROM Employee")):
        vals = tuple(_format_cell(x) for x in r)
        if emp_table['columns'] and emp_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        emp_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_employee():
    sel = emp_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select an employee to delete.')
        return
    vals_full = emp_table.item(sel[0], 'values')
    vals = vals_full[1:]
    eid = vals[0]
    if not messagebox.askyesno('Confirm', f'Delete employee {eid}?'):
        return
    try:
        execute('DELETE FROM Employee WHERE EmpId = ?', (int(eid),))
        load_employees()
        messagebox.showinfo('Deleted', 'Employee deleted.')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def edit_employee():
    sel = emp_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select an employee to edit.')
        return
    vals_full = emp_table.item(sel[0], 'values')
    vals = vals_full[1:]
    eid = vals[0]
    def _save(data):
        dept = data['Dept Code']
        branch = data['Branch ID']
        email = data['Email']
        if not dept or not branch or not email:
            raise ValueError('All fields required')
        try:
            branch_id = int(branch)
        except Exception:
            raise ValueError('Branch ID must be integer')
        execute('UPDATE Employee SET DeptCode=?, BranchId=?, Email=? WHERE EmpId=?', (dept, branch_id, email, int(eid)))
        load_employees()
        messagebox.showinfo('Saved', 'Employee updated.')
    _make_edit_dialog('Edit Employee', ['Dept Code','Branch ID','Email'], vals[1:], _save)

load_employees()

# =================== CUSTOMER ===================

cust_tab = ttk.Frame(notebook)
notebook.add(cust_tab, text="Customer")

cust_fields = make_form(cust_tab, ["SSN", "Job"])

def add_customer():
    ssn = cust_fields["SSN"].get().strip()
    job = cust_fields["Job"].get().strip()
    if not ssn:
        messagebox.showerror("Validation error", "SSN is required.")
        return
    try:
        execute(
            "INSERT INTO Customer (SSN, Job, IsActive) VALUES (?,?,1)",
            (ssn, job)
        )
        load_customers()
        cust_fields["SSN"].delete(0, tk.END)
        cust_fields["Job"].delete(0, tk.END)
        messagebox.showinfo("Success", "Customer added.")
    except Exception as e:
        messagebox.showerror("Error adding customer", str(e))

ttk.Button(cust_tab, text="Add", command=add_customer).pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(cust_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
ttk.Button(btn_frame, text='Edit', command=lambda: edit_customer()).pack(side='left')
ttk.Button(btn_frame, text='Delete', command=lambda: delete_customer()).pack(side='left', padx=6)
ttk.Button(btn_frame, text='Delete Selected', command=lambda: delete_selected(cust_table, 'DELETE FROM Customer WHERE CustomerId = ?', 1, True, load_customers)).pack(side='left', padx=6)

cust_table = make_table(cust_tab, ("ID","SSN","Job"), ("ID","SSN","Job"), with_select=True)

def load_customers():
    cust_table.delete(*cust_table.get_children())
    for i, r in enumerate(fetch("SELECT CustomerId, SSN, Job FROM Customer")):
        vals = tuple(_format_cell(x) for x in r)
        if cust_table['columns'] and cust_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        cust_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_customer():
    sel = cust_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a customer to delete.')
        return
    vals_full = cust_table.item(sel[0], 'values')
    vals = vals_full[1:]
    cid = vals[0]
    if not messagebox.askyesno('Confirm', f'Delete customer {cid}?'):
        return
    try:
        execute('DELETE FROM Customer WHERE CustomerId = ?', (int(cid),))
        load_customers()
        messagebox.showinfo('Deleted', 'Customer deleted.')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def edit_customer():
    sel = cust_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a customer to edit.')
        return
    vals_full = cust_table.item(sel[0], 'values')
    vals = vals_full[1:]
    cid = vals[0]
    def _save(data):
        ssn = data['SSN']
        job = data['Job']
        if not ssn:
            raise ValueError('SSN required')
        execute('UPDATE Customer SET SSN=?, Job=? WHERE CustomerId=?', (ssn, job, int(cid)))
        load_customers()
        messagebox.showinfo('Saved', 'Customer updated.')
    _make_edit_dialog('Edit Customer', ['SSN','Job'], vals[1:], _save)

load_customers()

# =================== ACCOUNT ===================

acc_tab = ttk.Frame(notebook)
notebook.add(acc_tab, text="Account")

acc_fields = make_form(acc_tab, ["IBAN","Customer ID","Branch ID","Balance"])

def add_account():
    iban = acc_fields["IBAN"].get().strip()
    cust = acc_fields["Customer ID"].get().strip()
    branch = acc_fields["Branch ID"].get().strip()
    bal = acc_fields["Balance"].get().strip()
    if not iban or not cust or not branch:
        messagebox.showerror("Validation error", "IBAN, Customer ID and Branch ID are required.")
        return
    try:
        cust_id = int(cust)
        branch_id = int(branch)
    except Exception:
        messagebox.showerror("Validation error", "Customer ID and Branch ID must be integers.")
        return
    try:
        balance = float(bal) if bal else 0.0
    except Exception:
        messagebox.showerror("Validation error", "Balance must be a number.")
        return
    try:
        execute(
            "INSERT INTO Account (IBAN, CustomerId, BranchId, Balance) VALUES (?,?,?,?)",
            (iban, cust_id, branch_id, balance)
        )
        load_accounts()
        acc_fields["IBAN"].delete(0, tk.END)
        acc_fields["Customer ID"].delete(0, tk.END)
        acc_fields["Branch ID"].delete(0, tk.END)
        acc_fields["Balance"].delete(0, tk.END)
        messagebox.showinfo("Success", "Account added.")
    except Exception as e:
        messagebox.showerror("Error adding account", str(e))

ttk.Button(acc_tab, text="Add", command=add_account).pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(acc_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
ttk.Button(btn_frame, text='Edit', command=lambda: edit_account()).pack(side='left')
ttk.Button(btn_frame, text='Delete', command=lambda: delete_account()).pack(side='left', padx=6)
ttk.Button(btn_frame, text='Delete Selected', command=lambda: delete_selected(acc_table, 'DELETE FROM Account WHERE AccountId = ?', 1, True, load_accounts)).pack(side='left', padx=6)

acc_table = make_table(acc_tab, ("ID","IBAN","Cust","Branch","Balance"), ("ID","IBAN","Cust","Branch","Balance"), with_select=True)

def load_accounts():
    acc_table.delete(*acc_table.get_children())
    for i, r in enumerate(fetch("SELECT AccountId, IBAN, CustomerId, BranchId, Balance FROM Account")):
        vals = tuple(_format_cell(x) for x in r)
        if acc_table['columns'] and acc_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        acc_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_account():
    sel = acc_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select an account to delete.')
        return
    vals_full = acc_table.item(sel[0], 'values')
    vals = vals_full[1:]
    aid = vals[0]
    if not messagebox.askyesno('Confirm', f'Delete account {aid}?'):
        return
    try:
        execute('DELETE FROM Account WHERE AccountId = ?', (int(aid),))
        load_accounts()
        messagebox.showinfo('Deleted', 'Account deleted.')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def edit_account():
    sel = acc_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select an account to edit.')
        return
    vals_full = acc_table.item(sel[0], 'values')
    vals = vals_full[1:]
    aid = vals[0]
    def _save(data):
        iban = data['IBAN']
        cust = data['Customer ID']
        branch = data['Branch ID']
        bal = data['Balance']
        if not iban or not cust or not branch:
            raise ValueError('IBAN, Customer ID and Branch ID required')
        try:
            cust_id = int(cust)
            branch_id = int(branch)
            balance = float(bal) if bal else 0.0
        except Exception:
            raise ValueError('IDs must be integers and balance a number')
        execute('UPDATE Account SET IBAN=?, CustomerId=?, BranchId=?, Balance=? WHERE AccountId=?', (iban, cust_id, branch_id, balance, int(aid)))
        load_accounts()
        messagebox.showinfo('Saved', 'Account updated.')
    _make_edit_dialog('Edit Account', ['IBAN','Customer ID','Branch ID','Balance'], vals[1:], _save)

load_accounts()

# =================== TRANSACTION ===================

txn_tab = ttk.Frame(notebook)
notebook.add(txn_tab, text="Transaction")

txn_fields = make_form(txn_tab, ["Account ID","Employee ID","Amount"])

def add_txn():
    acc = txn_fields["Account ID"].get().strip()
    emp = txn_fields["Employee ID"].get().strip()
    amt = txn_fields["Amount"].get().strip()
    if not acc or not emp or not amt:
        messagebox.showerror("Validation error", "Account ID, Employee ID and Amount are required.")
        return
    try:
        acc_id = int(acc)
        emp_id = int(emp)
    except Exception:
        messagebox.showerror("Validation error", "Account ID and Employee ID must be integers.")
        return
    try:
        amount = float(amt)
    except Exception:
        messagebox.showerror("Validation error", "Amount must be a number.")
        return
    try:
        execute(
            "INSERT INTO [Transaction] (AccountId, EmpId, Amount, TransactionDate) VALUES (?,?,?,GETDATE())",
            (acc_id, emp_id, amount)
        )
        load_txns()
        txn_fields["Account ID"].delete(0, tk.END)
        txn_fields["Employee ID"].delete(0, tk.END)
        txn_fields["Amount"].delete(0, tk.END)
        messagebox.showinfo("Success", "Transaction added.")
    except Exception as e:
        messagebox.showerror("Error adding transaction", str(e))

ttk.Button(txn_tab, text="Add", command=add_txn).pack(pady=(0,6), padx=10, anchor='w')
btn_frame = ttk.Frame(txn_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))

ttk.Button(btn_frame, text='Edit', command=lambda: edit_txn()).pack(side='left')
ttk.Button(btn_frame, text='Delete', command=lambda: delete_txn()).pack(side='left', padx=6)
ttk.Button(btn_frame, text='Delete Selected', command=lambda: delete_selected(txn_table, 'DELETE FROM [Transaction] WHERE TransactionId = ?', 1, True, load_txns)).pack(side='left', padx=6)

txn_table = make_table(txn_tab, ("ID","Acc","Emp","Amount","Date"), ("ID","Acc","Emp","Amount","Date"), with_select=True)

def load_txns():
    txn_table.delete(*txn_table.get_children())
    for i, r in enumerate(fetch("SELECT TransactionId, AccountId, EmpId, Amount, TransactionDate FROM [Transaction]")):
        vals = tuple(_format_cell(x) for x in r)
        if txn_table['columns'] and txn_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        txn_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_txn():
    sel = txn_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a transaction to delete.')
        return
    vals_full = txn_table.item(sel[0], 'values')
    vals = vals_full[1:]
    tid = vals[0]
    if not messagebox.askyesno('Confirm', f'Delete transaction {tid}?'):
        return
    try:
        execute('DELETE FROM [Transaction] WHERE TransactionId = ?', (int(tid),))
        load_txns()
        messagebox.showinfo('Deleted', 'Transaction deleted.')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def edit_txn():
    sel = txn_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a transaction to edit.')
        return
    vals_full = txn_table.item(sel[0], 'values')
    vals = vals_full[1:]
    tid = vals[0]
    def _save(data):
        acc = data['Account ID']
        emp = data['Employee ID']
        amt = data['Amount']
        if not acc or not emp or not amt:
            raise ValueError('All fields required')
        try:
            acc_id = int(acc)
            emp_id = int(emp)
            amount = float(amt)
        except Exception:
            raise ValueError('IDs must be integers and amount a number')
        execute('UPDATE [Transaction] SET AccountId=?, EmpId=?, Amount=? WHERE TransactionId=?', (acc_id, emp_id, amount, int(tid)))
        load_txns()
        messagebox.showinfo('Saved', 'Transaction updated.')
    _make_edit_dialog('Edit Transaction', ['Account ID','Employee ID','Amount'], vals[1:4], _save)

load_txns()

# ------------------- RUN -------------------

root.mainloop()
