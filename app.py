"""Main Tkinter application for Bank Management System.

This module builds a simple GUI to manage Departments, Branches,
Employees, Customers, Accounts and Transactions. Each entity has
create/read/update/delete handlers that use the `data` helpers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import tkinter.font as tkfont
from db import get_connection
from data import execute, fetch
from helpers import make_form, make_table, _format_cell, _make_edit_dialog, delete_selected, tree_sort


# ------------------- UI SETUP -------------------

root = tk.Tk()
root.title("Bank Management System")
root.geometry("1000x650")

# --- Theming & styling --- 
# Initialize ttkbootstrap style to apply a modern theme across widgets
style = Style('flatly')
DEFAULT_FONT = ('Segoe UI', 10)
style.configure('.', font=DEFAULT_FONT)
style.configure('TButton', padding=6)
style.configure('Treeview', rowheight=24, font=DEFAULT_FONT)
style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

# --- Modernized color palette and styles ---
PRIMARY_COLOR = '#4A90E2'
ACCENT_COLOR = '#50E3C2'
BG_COLOR = '#F7F9FC'
ROW_ALT = '#F1F5FB'

style.configure('.', background=BG_COLOR)
style.configure('TButton', padding=8, relief='flat', background=PRIMARY_COLOR, foreground='white')
style.map('TButton', background=[('active', '#3b7bd8'), ('disabled', '#a0a8b7')])
style.configure('Accent.TButton', background=ACCENT_COLOR, foreground='black')

style.configure('Treeview', fieldbackground='white', background='white', foreground='#222')
style.configure('Treeview.Heading', background=PRIMARY_COLOR, foreground='white')

def _add_button_hover(btn, style_name='TButton'):
    """Add a simple hover cursor and style swap for a ttk button.

    This doesn't attempt complex color changes (ttk backend constraints),
    but it sets the pointer and toggles to an alternate style when
    available to give a responsive feel.
    """
    def on_enter(e):
        try:
            btn.configure(cursor='hand2')
            btn.configure(style='Accent.TButton')
        except Exception:
            pass

    def on_leave(e):
        try:
            btn.configure(cursor='')
            btn.configure(style=style_name)
        except Exception:
            pass

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)


def animate_insert_rows(table, rows, delay=12):
    """Insert rows into a treeview one-by-one to create a subtle animation.

    Args:
        table: ttk.Treeview instance.
        rows: iterable of tuples to insert as `values`.
        delay: milliseconds between inserting rows.
    """
    # ensure table is empty before animation
    table.delete(*table.get_children())

    rows = list(rows)

    def _insert(i=0):
        if i >= len(rows):
            return
        vals = rows[i]
        # preserve existing tag logic (odd/even)
        table.insert('', 'end', values=vals, tags=('odd' if i % 2 else 'even',))
        table.after(delay, _insert, i + 1)

    # kick off animation
    table.after(0, _insert, 0)


def mkbtn(parent, text, command=None, boot='primary'):
    """Create a ttkbootstrap-style button and attach hover behavior.

    Returns the created button; caller should call `.pack()` or `.grid()`.
    """
    try:
        btn = ttk.Button(parent, text=text, command=command, bootstyle=boot)
    except Exception:
        # fallback for environments where bootstyle isn't supported
        btn = ttk.Button(parent, text=text, command=command)
    _add_button_hover(btn)
    return btn


notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

import helpers
helpers.root = root

# =================== DEPARTMENT ===================

dept_tab = ttk.Frame(notebook)
notebook.add(dept_tab, text="Department")

dept_fields = make_form(dept_tab, ["Dept Code", "Description"])

def add_department():
    """Insert a new department using values from the form.

    Validates required fields, executes a parameterized INSERT, then
    refreshes the department listing and clears the form. Any database
    exception is shown to the user.
    """
    code = dept_fields["Dept Code"].get().strip()
    desc = dept_fields["Description"].get().strip()
    # validation: both fields required
    if not code or not desc:
        messagebox.showerror("Validation error", "Dept Code and Description are required.")
        return
    try:
        # execute parameterized insert to avoid SQL injection
        execute(
            "INSERT INTO Department (DeptCode, Description) VALUES (?,?)",
            (code, desc)
        )
        # refresh UI and clear inputs on success
        load_departments()
        dept_fields["Dept Code"].delete(0, tk.END)
        dept_fields["Description"].delete(0, tk.END)
        messagebox.showinfo("Success", "Department added.")
    except Exception as e:
        # show error message returned from DB layer
        messagebox.showerror("Error adding department", str(e))

mkbtn(dept_tab, "Add", command=add_department, boot='success').pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(dept_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))

mkbtn(btn_frame, "Edit", command=lambda: edit_department(), boot='info').pack(side='left')
mkbtn(btn_frame, "Delete", command=lambda: delete_department(), boot='danger').pack(side='left', padx=6)
mkbtn(btn_frame, "Delete Selected", command=lambda: delete_selected(dept_table, 'DELETE FROM Department WHERE DeptCode = ?', 1, False, load_departments), boot='outline-danger').pack(side='left', padx=6)

dept_table = make_table(dept_tab, ("Code","Desc"), ("Dept Code","Description"), with_select=True)

def load_departments():
    """Load department rows from the database into the treeview.

    Clears the table then fetches DeptCode and Description and inserts
    each row. Adds a selection checkbox column indicator if the table
    was created with `with_select=True`.
    """
    dept_table.delete(*dept_table.get_children())
    for i, r in enumerate(fetch("SELECT DeptCode, Description FROM Department")):
        vals = tuple(_format_cell(x) for x in r)
        # if the table has a selection column, prefix a checkbox symbol
        if dept_table['columns'] and dept_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        dept_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_department():
    """Delete the selected department after user confirmation.

    Finds the selected row, extracts the DeptCode and executes a
    parameterized DELETE. Refreshes the list on success.
    """
    sel = dept_table.selection()
    if not sel:
        messagebox.showwarning('Select row', 'Select a department to delete.')
        return
    vals_full = dept_table.item(sel[0], 'values')
    # drop the selection column value, if present
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
    """Open an edit dialog for the selected department and save changes.

    Uses `_make_edit_dialog` from helpers to present a small form to
    the user. The nested `_save` callback validates inputs and runs an
    UPDATE statement, then refreshes the list.
    """
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
        # simple validation
        if not new_code or not desc:
            raise ValueError('Both fields required')
        # perform update and refresh UI
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
    """Insert a new branch from the branch form fields.

    Validates required fields, inserts into DB and refreshes the
    branch list. Errors are shown to the user.
    """
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

mkbtn(branch_tab, "Add", command=add_branch, boot='success').pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(branch_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
mkbtn(btn_frame, 'Edit', command=lambda: edit_branch(), boot='info').pack(side='left')
mkbtn(btn_frame, 'Delete', command=lambda: delete_branch(), boot='danger').pack(side='left', padx=6)
mkbtn(btn_frame, 'Delete Selected', command=lambda: delete_selected(branch_table, 'DELETE FROM Branch WHERE BranchId = ?', 1, True, load_branches), boot='outline-danger').pack(side='left', padx=6)

branch_table = make_table(branch_tab, ("ID","Code","Email","Phone"), ("ID","Code","Email","Phone"), with_select=True)

def load_branches():
    """Populate the branch treeview with rows from the Branch table."""
    branch_table.delete(*branch_table.get_children())
    for i, r in enumerate(fetch("SELECT BranchId, BranchCode, Email, Phone FROM Branch")):
        vals = tuple(_format_cell(x) for x in r)
        if branch_table['columns'] and branch_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        branch_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_branch():
    """Delete selected branch after confirmation."""
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
    """Open edit dialog for branch and apply updates when saved."""
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
    """Add a new employee; validate and insert then refresh table."""
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

mkbtn(emp_tab, "Add", command=add_employee, boot='success').pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(emp_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
mkbtn(btn_frame, 'Edit', command=lambda: edit_employee(), boot='info').pack(side='left')
mkbtn(btn_frame, 'Delete', command=lambda: delete_employee(), boot='danger').pack(side='left', padx=6)
mkbtn(btn_frame, 'Delete Selected', command=lambda: delete_selected(emp_table, 'DELETE FROM Employee WHERE EmpId = ?', 1, True, load_employees), boot='outline-danger').pack(side='left', padx=6)

emp_table = make_table(emp_tab, ("ID","Dept","Branch","Email"), ("ID","Dept","Branch","Email"), with_select=True)

def load_employees():
    """Fetch employees and display them in the employees treeview."""
    emp_table.delete(*emp_table.get_children())
    for i, r in enumerate(fetch("SELECT EmpId, DeptCode, BranchId, Email FROM Employee")):
        vals = tuple(_format_cell(x) for x in r)
        if emp_table['columns'] and emp_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        emp_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_employee():
    """Delete the selected employee record after confirmation."""
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
    """Edit selected employee via dialog and update DB on save."""
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
    """Create a new customer record from the customer form."""
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

mkbtn(cust_tab, "Add", command=add_customer, boot='success').pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(cust_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
mkbtn(btn_frame, 'Edit', command=lambda: edit_customer(), boot='info').pack(side='left')
mkbtn(btn_frame, 'Delete', command=lambda: delete_customer(), boot='danger').pack(side='left', padx=6)
mkbtn(btn_frame, 'Delete Selected', command=lambda: delete_selected(cust_table, 'DELETE FROM Customer WHERE CustomerId = ?', 1, True, load_customers), boot='outline-danger').pack(side='left', padx=6)

cust_table = make_table(cust_tab, ("ID","SSN","Job"), ("ID","SSN","Job"), with_select=True)

def load_customers():
    """Refresh the customers list displayed in the UI."""
    cust_table.delete(*cust_table.get_children())
    for i, r in enumerate(fetch("SELECT CustomerId, SSN, Job FROM Customer")):
        vals = tuple(_format_cell(x) for x in r)
        if cust_table['columns'] and cust_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        cust_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_customer():
    """Delete the selected customer from the database."""
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
    """Edit selected customer using the helper dialog and save updates."""
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
    """Add a new account after validating IDs and balance."""
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

mkbtn(acc_tab, "Add", command=add_account, boot='success').pack(pady=(0,6), padx=10, anchor='w')

btn_frame = ttk.Frame(acc_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))
mkbtn(btn_frame, 'Edit', command=lambda: edit_account(), boot='info').pack(side='left')
mkbtn(btn_frame, 'Delete', command=lambda: delete_account(), boot='danger').pack(side='left', padx=6)
mkbtn(btn_frame, 'Delete Selected', command=lambda: delete_selected(acc_table, 'DELETE FROM Account WHERE AccountId = ?', 1, True, load_accounts), boot='outline-danger').pack(side='left', padx=6)

acc_table = make_table(acc_tab, ("ID","IBAN","Cust","Branch","Balance"), ("ID","IBAN","Cust","Branch","Balance"), with_select=True)

def load_accounts():
    """Load accounts into the account treeview."""
    acc_table.delete(*acc_table.get_children())
    for i, r in enumerate(fetch("SELECT AccountId, IBAN, CustomerId, BranchId, Balance FROM Account")):
        vals = tuple(_format_cell(x) for x in r)
        if acc_table['columns'] and acc_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        acc_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_account():
    """Delete the selected account record from the DB."""
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
    """Edit the selected account; validate inputs and update DB."""
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
    """Create a transaction: validate, insert with current date, and refresh."""
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
        # Insert the transaction; SQL Server GETDATE() will set timestamp
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

mkbtn(txn_tab, "Add", command=add_txn, boot='success').pack(pady=(0,6), padx=10, anchor='w')
btn_frame = ttk.Frame(txn_tab)
btn_frame.pack(anchor='w', padx=10, pady=(0,6))

mkbtn(btn_frame, 'Edit', command=lambda: edit_txn(), boot='info').pack(side='left')
mkbtn(btn_frame, 'Delete', command=lambda: delete_txn(), boot='danger').pack(side='left', padx=6)
mkbtn(btn_frame, 'Delete Selected', command=lambda: delete_selected(txn_table, 'DELETE FROM [Transaction] WHERE TransactionId = ?', 1, True, load_txns), boot='outline-danger').pack(side='left', padx=6)

txn_table = make_table(txn_tab, ("ID","Acc","Emp","Amount","Date"), ("ID","Acc","Emp","Amount","Date"), with_select=True)

def load_txns():
    """Populate the transaction list from the Transaction table."""
    txn_table.delete(*txn_table.get_children())
    for i, r in enumerate(fetch("SELECT TransactionId, AccountId, EmpId, Amount, TransactionDate FROM [Transaction]")):
        vals = tuple(_format_cell(x) for x in r)
        if txn_table['columns'] and txn_table['columns'][0] == '_sel':
            vals = ('☐',) + vals
        txn_table.insert("", "end", values=vals, tags=('odd' if i%2 else 'even',))

def delete_txn():
    """Delete the selected transaction entry after confirmation."""
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
    """Edit a transaction: validate inputs, update DB and refresh list."""
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
