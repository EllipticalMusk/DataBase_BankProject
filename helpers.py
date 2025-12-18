import tkinter as tk
from tkinter import ttk, messagebox

# Module-level `root` will be set by the main app after creating the Tk instance
root = None


def make_form(parent, fields):
    frame = ttk.Frame(parent, padding=(10, 8))
    frame.pack(fill='x')
    entries = {}
    for i, label in enumerate(fields):
        ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', padx=(0,8), pady=6)
        ent = ttk.Entry(frame)
        ent.grid(row=i, column=1, sticky='we', pady=6)
        entries[label] = ent
    frame.columnconfigure(1, weight=1)
    return entries


def make_table(parent, columns, headings, with_select=False):
    frame = ttk.Frame(parent, padding=(10, 8))
    frame.pack(fill='both', expand=True)
    # optionally add a select checkbox column at the start
    if with_select:
        columns = ('_sel',) + tuple(columns)
        headings = ('',) + tuple(headings)
    tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
    for c, h in zip(columns, headings):
        if c == '_sel':
            tree.heading(c, text=h)
            tree.column(c, width=36, anchor='center', stretch=False)
        else:
            tree.heading(c, text=h)
            tree.column(c, anchor='center')
    vsb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')
    tree.tag_configure('odd', background='#fbfbfb')
    tree.tag_configure('even', background='white')
    if with_select:
        tree.bind('<Button-1>', lambda e: _on_tree_click(e, tree))
    return tree


def _toggle_check(tree, item):
    try:
        cur = tree.set(item, '_sel')
    except Exception:
        return
    new = '☑' if cur != '☑' else '☐'
    tree.set(item, '_sel', new)


def _on_tree_click(event, tree):
    # Toggle checkbox if clicked in first column
    col = tree.identify_column(event.x)
    row = tree.identify_row(event.y)
    if not row:
        return
    if col == '#1':
        _toggle_check(tree, row)


def tree_sort(tree, col, reverse=False):
    # Skip sorting on selection column
    if col == '_sel':
        return
    data = []
    for k in tree.get_children(''):
        v = tree.set(k, col)
        data.append((v, k))
    def _try_num(x):
        try:
            return float(x)
        except Exception:
            return x
    data.sort(key=lambda t: _try_num(t[0]), reverse=reverse)
    for index, (_, k) in enumerate(data):
        tree.move(k, '', index)
    # toggle next time
    tree._sort_states = getattr(tree, '_sort_states', {})
    tree._sort_states[col] = not reverse


def delete_selected(tree, delete_sql, id_pos_with_select=1, id_is_int=False, reload_callback=None):
    # collect checked items
    items = [it for it in tree.get_children('') if tree.set(it, '_sel') == '☑']
    if not items:
        messagebox.showwarning('No selection', 'No rows checked for deletion.')
        return
    if not messagebox.askyesno('Confirm', f'Delete {len(items)} selected rows?'):
        return
    from data import execute
    try:
        for it in items:
            vals = tree.item(it, 'values')
            v = vals[id_pos_with_select]
            if id_is_int:
                v = int(v)
            execute(delete_sql, (v,))
        if reload_callback:
            reload_callback()
        else:
            for it in items:
                try:
                    tree.delete(it)
                except Exception:
                    pass
        messagebox.showinfo('Deleted', f'Deleted {len(items)} rows.')
    except Exception as e:
        messagebox.showerror('Error', str(e))


def _format_cell(v):
    if v is None:
        return ""
    try:
        import datetime
        if isinstance(v, bytes):
            return v.decode(errors='ignore')
        if isinstance(v, datetime.datetime) or isinstance(v, datetime.date):
            return v.strftime('%Y-%m-%d %H:%M:%S') if hasattr(v, 'hour') else v.strftime('%Y-%m-%d')
    except Exception:
        pass
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v)
    return str(v)


def _make_edit_dialog(title, fields, values, on_save):
    # uses module-level `root` variable; main app should set helpers.root = root
    win = tk.Toplevel(root)
    win.title(title)
    entries = {}
    for i, key in enumerate(fields):
        ttk.Label(win, text=key).grid(row=i, column=0, sticky='w', padx=8, pady=6)
        ent = ttk.Entry(win)
        ent.grid(row=i, column=1, sticky='we', padx=8, pady=6)
        ent.insert(0, '' if values[i] is None else str(values[i]))
        entries[key] = ent
    win.columnconfigure(1, weight=1)
    def _save():
        data = {k: entries[k].get().strip() for k in fields}
        try:
            on_save(data)
            win.destroy()
        except Exception as e:
            messagebox.showerror('Edit error', str(e), parent=win)
    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=(4,8))
    ttk.Button(btn_frame, text='Save', command=_save).pack(side='left', padx=6)
    ttk.Button(btn_frame, text='Cancel', command=win.destroy).pack(side='left')
    win.transient(root)
    win.grab_set()
    win.wait_window()
