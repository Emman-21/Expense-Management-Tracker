# IMPORTED EXTENSIONS
import tkinter as tk # for gui syempre ahihi
from tkinter import ttk, messagebox #for pop up message box (warning purposes)
import sqlite3 # for database 
from datetime import datetime, date # for date and time related stuffs
import matplotlib.pyplot as plt # for graphing to make it more presentable
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import hashlib # for password security



# COLORS IN HEX VALUES (hulaan nalang kung ano ngolor yan whaha)
PRIMARY_COLOR = "#0F1E3A"
SECONDARY_COLOR = "#1B3A64"
ACCENT_COLOR = "#4DEAEF"
TEXT_COLOR = "#EFEFEF"
BUTTON_COLOR = "#2D5A8E"
DELETE_COLOR = "#9E2A2B"
MANAGE_COLOR = "#167A6E"
BLACK_COLOR = "#000000"



# GRAPH COLORS
GRAPH_COLORS = {
    'Total': ACCENT_COLOR,   
    'Water': '#1E88E5',       
    'Electricity': '#FFC107',     
    'Others': '#8BC34A'          
}



# SDG INTEGRATION & ANALYSIS (for pop up warnings when the total is increasing than last month)
SDG_TIPS = {
    "water": "SDG 6 Tip: Check for leaks or shorten showers to save thousands of liters of water and money!",
    "electricity": "SDG 7 & 13 Tip: Unplug appliances to stop 'phantom power.' Switching to LED bulbs also drastically reduces kWh use.",
    "others": "SDG 12 Tip: Before buying non-essentials, consider if it's durable, locally sourced, or second-hand to promote responsible consumption.",
    "default": "Great job tracking your finances! Saving money is the first step towards promoting responsible consumption."
}





# INPUT VALIDATION
def is_valid_month_format(month_str):
    # to format the date and time 
    try:
        datetime.strptime(month_str, "%Y-%m")
        return True
    except ValueError:
        return False


def clean_currency_input(value):
    # for peso sign para astig
    if isinstance(value, str):
        return value.replace('₱', '').replace(',', '').strip()
    return str(value)





# DATABASE SETUP (using sqlite)
def setup_database():
    # name of the database
    conn = sqlite3.connect('expenses_tracker.db')
    cursor = conn.cursor()

    # creating "expenses" table in database (MONTHLY TOTALS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL UNIQUE,
            water REAL,
            electricity REAL,
            others REAL,        
            total REAL
        )
    """)

    # creating "transactions" table in database (CATEGORIZED SPENDING)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL
        )
    """)

    # creating "users" table in database (AUTHENTICATION DATA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)


    # THE PASSWORD OF THE GUI
    admin_password_hash = hash_password("password123") #password
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                         ('admin', admin_password_hash)) #name
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    conn.close()





# AUTHENTICATION SYSTEM
def hash_password(password):
    # hashing the password 
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_hash, provided_password):
    # verify the password if correct or nah
    return stored_hash == hash_password(provided_password)


# LoginWindow class for Security (CREATING WINDOW FOR PASSWORD)
class LoginWindow(tk.Tk):
    # create windows box using tk geometry 
    def __init__(self, start_main_app_callback):
        super().__init__()
        self.title("🔒 Login to Tracker")
        self.geometry("350x250")
        self.configure(bg=PRIMARY_COLOR)
        self.start_main_app_callback = start_main_app_callback
        
        self.eval('tk::PlaceWindow . center')
        self.create_login_widgets()


    # create styles in password verification to make it more attractive
    def create_login_widgets(self):
        frame = ttk.Frame(self, padding="20 20 20 20", style='Login.TFrame')
        frame.pack(expand=True, padx=20, pady=20)
        
        style = ttk.Style(self)
        style.configure('Login.TFrame', background=SECONDARY_COLOR, borderwidth=5, relief='flat')
        style.configure('TEntry', fieldbackground=PRIMARY_COLOR, foreground=TEXT_COLOR)

        # for inputing username
        tk.Label(frame, text="Username:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(pady=5)
        self.username_entry = tk.Entry(frame, bg=PRIMARY_COLOR, fg=TEXT_COLOR, insertbackground=ACCENT_COLOR)
        self.username_entry.pack(pady=5)
        self.username_entry.bind('<Return>', lambda event: self.password_entry.focus())

        # for inputing password
        tk.Label(frame, text="Password:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(pady=5)
        self.password_entry = tk.Entry(frame, show="*", bg=PRIMARY_COLOR, fg=TEXT_COLOR, insertbackground=ACCENT_COLOR)
        self.password_entry.pack(pady=5)
        self.password_entry.bind('<Return>', lambda event: self.attempt_login())

        # LOGIN BUTTON
        tk.Button(frame, 
                  text="LOGIN", 
                  command=self.attempt_login, 
                  bg=ACCENT_COLOR, 
                  fg=PRIMARY_COLOR,
                  activebackground=ACCENT_COLOR,
                  activeforeground=PRIMARY_COLOR,
                  font=('Arial', 10, 'bold'),
                  relief='flat').pack(pady=15)
        
        self.username_entry.focus_set()


    # if the user types wrong password and username
    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect('expenses_tracker.db')
        cursor = conn.cursor()

        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and verify_password(user_data[0], password):
            self.destroy() 
            self.start_main_app_callback()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.") # pops up warning message





# MAIN APPLICATION CLASS
class ExpensesTrackerApp(tk.Tk):
    # creating window box 
    def __init__(self, main_app_launcher):
        super().__init__()
        self.title("💰 Expenses Management Tracker")
        self.geometry("1100x700")
        self.configure(bg=PRIMARY_COLOR)
        self.main_app_launcher = main_app_launcher
        
        self.current_sort_order = "month DESC"

        self.create_styles()
        self.create_widgets()
        
        current_month = datetime.now().strftime("%Y-%m")
        self.load_data() 
        self.update_others_display(current_month)
        
        self.plot_total_trend() 





    # SECURITY & USER MANAGEMENT
    def logout(self):  
        # create message for logout
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.destroy()
            self.main_app_launcher()





    # STYLING SYSTEM
    def create_styles(self):
        # add styles para daw maganda parang sya ahihi
        style = ttk.Style()
        style.theme_use('default')

        style.configure("Treeview",
                        background=SECONDARY_COLOR,
                        foreground=TEXT_COLOR,
                        fieldbackground=SECONDARY_COLOR,
                        font=('Arial', 10),
                        rowheight=25)

        style.map('Treeview',
                  background=[('selected', ACCENT_COLOR)],
                  foreground=[('selected', PRIMARY_COLOR)])

        style.configure("Treeview.Heading",
                        background=BUTTON_COLOR,
                        foreground=TEXT_COLOR,
                        font=('Arial', 10, 'bold'))
        
        style.configure('TFrame', background=SECONDARY_COLOR)
        style.configure('TLabel', background=SECONDARY_COLOR, foreground=TEXT_COLOR)
        style.configure('TMenubutton', background=PRIMARY_COLOR, foreground=TEXT_COLOR)
        
        style.configure('Sort.TMenubutton', background=BUTTON_COLOR, foreground=TEXT_COLOR, 
                        font=('Arial', 10, 'bold'), relief='flat')
        




    # DATA MANAGEMENT
    # connect with database
    def get_db_connection(self):
        return sqlite3.connect('expenses_tracker.db') # name of the database
    
    # for loading data in table
    def load_data(self, sort_by="month DESC"):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = f"SELECT month, water, electricity, others, total FROM expenses ORDER BY {sort_by}"
        cursor.execute(query)

        for row in cursor.fetchall():
            month = row[0]
            water = f"₱{row[1]:,.2f}"
            electricity = f"₱{row[2]:,.2f}"
            others = f"₱{row[3]:,.2f}"
            total = f"₱{row[4]:,.2f}"

            formatted_row = (month, water, electricity, others, total)
            self.tree.insert('', tk.END, values=formatted_row, iid=month)

        conn.close()





    # FORM MANAGEMENT
    def clear_entries(self):
        # clearing data entries
        default_month = datetime.now().strftime("%Y-%m")

        for key in self.entries:
            if self.entries[key].winfo_exists():
                self.entries[key].config(state='normal')
                self.entries[key].delete(0, tk.END)

        if 'month' in self.entries and self.entries['month'].winfo_exists():
            self.entries['month'].insert(0, default_month)
            
        if 'others' in self.entries and self.entries['others'].winfo_exists():
             self.entries['others'].insert(0, f"{0.0:.2f}")
             self.entries['others'].config(state='readonly')
        

    def update_others_display(self, month):
        # updating the data in db
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE month=?", (month,))
        total_others = cursor.fetchone()[0] or 0.0
        conn.close()

        if 'others' in self.entries and self.entries['others'].winfo_exists():
            self.entries['others'].config(state='normal')
            self.entries['others'].delete(0, tk.END)
            self.entries['others'].insert(0, f"{total_others:.2f}")
            self.entries['others'].config(state='readonly')





    # EVENT HANDLING & INTERACTIVITY
    def on_tree_select(self, event):
        selected_item = self.tree.focus() # gets the row that user selects
        
        if 'month' in self.entries and self.entries['month'].winfo_exists():
            self.entries['month'].config(state='normal')
            self.entries['month'].delete(0, tk.END)

        if selected_item:
            values = self.tree.item(selected_item, 'values') # get the data of row
            if values:
                
                selected_month = values[0]
                
                self.entries['month'].insert(0, selected_month)
                
                self.entries['water'].delete(0, tk.END)
                self.entries['electricity'].delete(0, tk.END)
                self.entries['water'].insert(0, clean_currency_input(values[1]))
                self.entries['electricity'].insert(0, clean_currency_input(values[2]))
                
                self.update_others_display(selected_month)
        else:
            self.clear_entries()


    def _refresh_all(self, month, current_win=None):
        self.update_others_display(month)
        self.load_data(self.current_sort_order)

        if self.graph_frame.winfo_children(): 
            self.plot_graph_data()
        if current_win:
            for w in self.winfo_children():
                if isinstance(w, tk.Toplevel) and "Manage Other Expenses" in w.title():
                    w.destroy()
            current_win.destroy()





    # TRANSACTIONS MANAGEMENT
    # get the transactions in db
    def get_transactions(self, month):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, description, amount FROM transactions WHERE month=? ORDER BY id DESC", (month,))
        data = cursor.fetchall()
        conn.close()
        return data


    # editing the transactions in db
    def update_transaction(self, trans_id, new_category, new_description, new_amount, month, win):
        try:
            new_amount = float(clean_currency_input(new_amount))
            if new_amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid amount: {e}")
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE transactions 
                SET category=?, description=?, amount=? 
                WHERE id=?
            """, (new_category, new_description, new_amount, trans_id))
            conn.commit()
            
            self._refresh_all(month, win)
            messagebox.showinfo("Success", f"Transaction ID {trans_id} updated.")

        except Exception as e: # in case theres some errors 
            messagebox.showerror("Database Error", f"Error updating transaction: {e}")
        finally:
            conn.close()


    # deleting the transactions in db
    def delete_transaction(self, trans_id, month, win):

        # pop up warning message if you want to delete the selected data transaction
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Transaction ID {trans_id}?"):
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM transactions WHERE id=?", (trans_id,))
            conn.commit()
            
            self._refresh_all(month, win)
            messagebox.showinfo("Success", f"Transaction ID {trans_id} deleted.")
            
        except Exception as e: # in case have a error 
            messagebox.showerror("Database Error", f"Error deleting transaction: {e}")
        finally:
            conn.close()


    # managing the transactions in other expenses 
    def manage_transactions_window(self):
        CATEGORIES = ['Food & Groceries', 'Transport', 'Healthcare',
                      'Sustainable Goods', 'Wasteful Spending', 'Entertainment']

        master_month = self.entries['month'].get().strip()
        
        # if it is not valid format it pops up a message that it is invalid
        if not is_valid_month_format(master_month):
            messagebox.showwarning("Warning", "Please enter a valid Month (YYYY-MM) first.")
            return

        # creates a window box for managing other expenses
        win = tk.Toplevel(self)
        win.title(f"🔄 Manage Other Expenses for {master_month}")
        win.configure(bg=SECONDARY_COLOR)
        win.grab_set()
        win.resizable(False, False)

        # Add new transaction button
        add_frame = tk.LabelFrame(win,
                                text="➕ Add New Transaction", 
                                bg=SECONDARY_COLOR, 
                                fg=ACCENT_COLOR, 
                                padx=10, 
                                pady=10, 
                                font=('Arial', 10, 'bold'))
        
        add_frame.pack(padx=15, 
                       pady=15, 
                       fill='x')

        # Category Label
        tk.Label(add_frame, 
                 text="Category:", 
                 bg=SECONDARY_COLOR, 
                 fg=TEXT_COLOR).grid(row=0, 
                                     column=0, 
                                     padx=5, 
                                     pady=5, 
                                     sticky='w')
        
        category_var = tk.StringVar(win, 
                                    value=CATEGORIES[0])
        
        # option box for choosing other transactions categories
        category_menu = ttk.OptionMenu(add_frame, 
                                       category_var, 
                                       CATEGORIES[0], 
                                       *CATEGORIES, 
                                       style='TMenubutton') 
        
        category_menu.config(width=20)

        category_menu.grid(row=0, 
                           column=1, 
                           padx=5, 
                           pady=5)

        tk.Label(add_frame, 
                 text="Description:", 
                 bg=SECONDARY_COLOR, 
                 fg=TEXT_COLOR).grid(row=1, 
                                     column=0, 
                                     padx=5, 
                                     pady=5, 
                                     sticky='w')
        
        desc_entry = tk.Entry(add_frame, 
                              bg=PRIMARY_COLOR, 
                              fg=TEXT_COLOR, 
                              width=30, 
                              insertbackground=ACCENT_COLOR)
        
        desc_entry.grid(row=1, 
                        column=1, 
                        padx=5, 
                        pady=5)

        # Amount Label
        tk.Label(add_frame, 
                 text="Amount (₱):", 
                 bg=SECONDARY_COLOR, 
                 fg=TEXT_COLOR).grid(row=2, 
                                     column=0, 
                                     padx=5, 
                                     pady=5, 
                                     sticky='w')
        
        amount_entry = tk.Entry(add_frame, 
                                bg=PRIMARY_COLOR, 
                                fg=TEXT_COLOR, 
                                width=30, 
                                insertbackground=ACCENT_COLOR)
        
        amount_entry.grid(row=2, 
                          column=1, 
                          padx=5, 
                          pady=5)


        # saving new transactions in db
        def save_new_transaction():
            try:
                category = category_var.get()
                description = desc_entry.get().strip()
                amount = float(clean_currency_input(amount_entry.get()))

                # if amount is negative or equals to zero it raise a error
                if amount <= 0:
                    raise ValueError("Amount must be positive.")
                
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO transactions (month, category, description, amount) 
                    VALUES (?, ?, ?, ?)
                """, (master_month, category, description, amount))
                conn.commit()
                conn.close()

                # if successful, it pops up a message that it successfully saved
                messagebox.showinfo("Success", f"₱{amount:.2f} saved under '{category}'.")

                self.update_others_display(master_month)
                self.load_data(self.current_sort_order)
                self.plot_total_trend()

                load_transaction_list()
                desc_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)

            # in case theres some exception errors
            except ValueError as e:
                messagebox.showerror("Input Error", f"Invalid amount: {e}")
            except Exception as e:
                messagebox.showerror("Database Error", f"Error saving transaction: {e}")

        # SAVE NEW TRANSACTION Button
        tk.Button(add_frame,
                  text="💾 SAVE NEW TRANSACTION",
                  command=save_new_transaction,
                  bg=ACCENT_COLOR,
                  fg=PRIMARY_COLOR,
                  activebackground=ACCENT_COLOR,
                  activeforeground=PRIMARY_COLOR,
                  font=('Arial', 10, 'bold'),
                  relief='flat').grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

        # Existing Transactions Label
        # creating a table for other categorized expenses transaction table
        list_frame = tk.LabelFrame(win,
                                   text="📋 Existing Transactions (Select to Edit)",
                                   bg=SECONDARY_COLOR,
                                   fg=ACCENT_COLOR,
                                   padx=10,
                                   pady=10,
                                   font=('Arial', 10, 'bold'))

        list_frame.pack(padx=15, 
                        pady=15, 
                        fill='both', 
                        expand=True)

        columns = ("ID", "Category", "Description", "Amount")

        trans_tree = ttk.Treeview(list_frame, 
                                  columns=columns, 
                                  show='headings', 
                                  height=8)

        vsb = ttk.Scrollbar(list_frame, 
                            orient="vertical", 
                            command=trans_tree.yview)
        
        trans_tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side='right', fill='y')

        for col in columns:
            trans_tree.heading(col, text=col)
        trans_tree.column("ID", width=40, anchor='center')
        trans_tree.column("Category", width=120)
        trans_tree.column("Description", width=150)
        trans_tree.column("Amount", width=80, anchor='e')

        trans_tree.pack(side='left', fill='both', expand=True)


        # load the transaction list
        def load_transaction_list():
            for item in trans_tree.get_children():
                trans_tree.delete(item)

            transactions = self.get_transactions(master_month)
            for trans in transactions:
                formatted_trans = (trans[0], trans[1], trans[2], f"{trans[3]:.2f}")
                trans_tree.insert('', 
                                  tk.END, 
                                  values=formatted_trans, 
                                  iid=trans[0])



        def on_trans_select(event):
            # when user clicks on a transaction in the list
            selected_item = trans_tree.focus()
            if not selected_item:
                return


            # gets the selected transaction detail
            values = trans_tree.item(selected_item, 'values')
            trans_id = values[0]    # Transaction ID from database
            current_category = values[1]   # Current category (e.g., "Food & Groceries")
            current_description = values[2] # Current description
            current_amount = values[3]  # Current amount


            # creates popup for editing
            edit_win = tk.Toplevel(win)
            edit_win.title(f"✏️ Edit Transaction ID {trans_id}")
            edit_win.configure(bg=SECONDARY_COLOR)
            edit_win.grab_set()
            edit_win.resizable(False, False)
            
            edit_frame = tk.Frame(edit_win, bg=SECONDARY_COLOR, padx=10, pady=10)
            edit_frame.pack()

            edit_categories = CATEGORIES
            edit_cat_var = tk.StringVar(edit_win, value=current_category)

            tk.Label(edit_frame, 
                     text="Category:", 
                     bg=SECONDARY_COLOR, 
                     fg=TEXT_COLOR).grid(row=0, 
                                         column=0, 
                                         padx=5, 
                                         pady=5, 
                                         sticky='w')
            
            ttk.OptionMenu(edit_frame, 
                           edit_cat_var, 
                           current_category, 
                           *edit_categories, 
                           style='TMenubutton').grid(row=0, 
                                                     column=1, 
                                                     padx=5, 
                                                     pady=5, 
                                                     sticky='ew')

            tk.Label(edit_frame, 
                     text="Description:", 
                     bg=SECONDARY_COLOR, 
                     fg=TEXT_COLOR).grid(row=1, 
                                         column=0, 
                                         padx=5, 
                                         pady=5, 
                                         sticky='w')
            
            edit_desc_entry = tk.Entry(edit_frame, 
                                       bg=PRIMARY_COLOR, 
                                       fg=TEXT_COLOR, 
                                       width=30, 
                                       insertbackground=ACCENT_COLOR)
            
            # shows current values for editing
            edit_desc_entry.insert(0, current_description)    # Pre-fill description

            edit_desc_entry.grid(row=1, 
                                 column=1, 
                                 padx=5, 
                                 pady=5, 
                                 sticky='ew')
            

            tk.Label(edit_frame, 
                     text="Amount (₱):", 
                     bg=SECONDARY_COLOR, 
                     fg=TEXT_COLOR).grid(row=2, 
                                         column=0, 
                                         padx=5, 
                                         pady=5, 
                                         sticky='w')
            
            edit_amount_entry = tk.Entry(edit_frame, 
                                         bg=PRIMARY_COLOR, 
                                         fg=TEXT_COLOR, 
                                         width=30, 
                                         insertbackground=ACCENT_COLOR)
            
            edit_amount_entry.insert(0, current_amount)     # Pre-fill amount

            edit_amount_entry.grid(row=2, 
                                   column=1, 
                                   padx=5, 
                                   pady=5, 
                                   sticky='ew')


            # buttons to save changes or delete
            # SAVE button
            tk.Button(edit_frame,
                      text="SAVE CHANGES",
                      command=lambda: self.update_transaction(
                          trans_id, edit_cat_var.get(), edit_desc_entry.get(), edit_amount_entry.get(), master_month, edit_win),
                      bg=BUTTON_COLOR,
                      fg=TEXT_COLOR,
                      relief='flat').grid(row=3, 
                                          column=0, 
                                          padx=5, 
                                          pady=10, 
                                          sticky='ew')
            # DELETE button
            tk.Button(edit_frame,
                      text="DELETE",
                      command=lambda: self.delete_transaction(
                          trans_id, master_month, edit_win),
                      bg=DELETE_COLOR,
                      fg=TEXT_COLOR,
                      relief='flat').grid(row=3, 
                                          column=1, 
                                          padx=5, 
                                          pady=10, 
                                          sticky='ew')

            edit_win.protocol("WM_DELETE_WINDOW", lambda: (edit_win.grab_release(), edit_win.destroy()))

        trans_tree.bind('<<TreeviewSelect>>', on_trans_select)

        load_transaction_list()

        # to manage the functions
        def on_manage_close():
            self.update_others_display(master_month)
            self.load_data(self.current_sort_order)
            self.plot_total_trend()
            win.grab_release()
            win.destroy()
        
        win.protocol("WM_DELETE_WINDOW", on_manage_close)





    # USER INTERFACE COMPONENTS
    def create_widgets(self):
        entry_frame = tk.Frame(self, bg=SECONDARY_COLOR, padx=15, pady=15)
        entry_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Data Entry Label
        tk.Label(entry_frame,
                 text="✏️ Data Entry (Bills & Monthly Total)",
                 font=('Arial', 14, 'bold'),
                 bg=SECONDARY_COLOR,
                 fg=ACCENT_COLOR).pack(pady=10)

        self.entries = {}
        fields = [("Month (YYYY-MM):", "month"),
                  ("Water Bill (₱):", "water"),
                  ("Electricity Bill (₱):", "electricity")]

        default_month = datetime.now().strftime("%Y-%m")

        # for inputing users information in data entry
        for label_text, key in fields:
            tk.Label(entry_frame,
                     text=label_text,
                     bg=SECONDARY_COLOR,
                     fg=TEXT_COLOR,
                     font=('Arial', 10)).pack(anchor='w', pady=(5, 0))
            
            entry = tk.Entry(entry_frame,
                             width=25,
                             bg=PRIMARY_COLOR,
                             fg=TEXT_COLOR,
                             insertbackground=ACCENT_COLOR,
                             borderwidth=2,
                             relief="flat",
                             font=('Arial', 10))

            entry.pack(anchor='w', pady=(0, 10))
            self.entries[key] = entry

        self.entries['month'].insert(0, default_month)

        # white box showing the total other expenses
        tk.Label(entry_frame,
                 text="Categorized Spending Total (Read-Only):",
                 bg=SECONDARY_COLOR,
                 fg=TEXT_COLOR,
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(5, 0))

        others_input_container = tk.Frame(entry_frame, bg=SECONDARY_COLOR)

        others_input_container.pack(fill='x', 
                                    anchor='w', 
                                    pady=(0, 10))

        others_entry = tk.Entry(others_input_container,
                                 width=15,
                                 bg=PRIMARY_COLOR,
                                 fg=BLACK_COLOR, 
                                 insertbackground=ACCENT_COLOR,
                                 borderwidth=2,
                                 relief="flat",
                                 font=('Arial', 10, 'bold'))

        others_entry.pack(side=tk.LEFT, fill='x', expand=True)
        self.entries['others'] = others_entry

        # Manage Spending Button (Other Expenses)
        tk.Button(others_input_container,
                  text="🔄 Manage Spending",
                  command=self.manage_transactions_window,
                  bg=MANAGE_COLOR,
                  fg=TEXT_COLOR,
                  activebackground=MANAGE_COLOR,
                  activeforeground=TEXT_COLOR,
                  font=('Arial', 10, 'bold'),
                  relief="flat",
                  padx=5,
                  pady=3).pack(side=tk.RIGHT, padx=(5, 0))

        self.entries['others'].config(state='readonly')

        button_frame = tk.Frame(entry_frame, bg=SECONDARY_COLOR)
        button_frame.pack(fill='x', pady=(10, 0))

        # SAVE EXPENSES Button
        tk.Button(button_frame,
                  text="💾 SAVE EXPENSES",
                  command=self.save_expense,
                  bg=ACCENT_COLOR,
                  fg=PRIMARY_COLOR,
                  activebackground=ACCENT_COLOR,
                  activeforeground=PRIMARY_COLOR,
                  font=('Arial', 11, 'bold'),
                  relief="flat",
                  padx=10,
                  pady=5).pack(side=tk.LEFT, 
                               expand=True, 
                               fill='x', 
                               padx=(0, 5))

        # UPDATE RECORD Button
        tk.Button(button_frame,
                  text="✏️ UPDATE RECORD",
                  command=self.edit_expense,
                  bg=BUTTON_COLOR,
                  fg=TEXT_COLOR,
                  activebackground='#3A6E9E',
                  activeforeground=TEXT_COLOR,
                  font=('Arial', 11, 'bold'),
                  relief="flat",
                  padx=10,
                  pady=5).pack(side=tk.RIGHT, 
                               expand=True, 
                               fill='x', 
                               padx=(5, 0))

        # CLEAR FIELDS Button
        tk.Button(entry_frame,
                  text="🔄 CLEAR FIELDS",
                  command=self.clear_entries,
                  bg='#555555',
                  fg=TEXT_COLOR,
                  activebackground='#777777',
                  activeforeground=TEXT_COLOR,
                  font=('Arial', 10, "bold"),
                  relief="flat",
                  padx=10,
                  pady=5).pack(fill='x', 
                               pady=(10, 5))

        # DELETE SELECTED Button
        tk.Button(entry_frame,
                  text="🗑️ DELETE SELECTED",
                  command=self.delete_expense,
                  bg=DELETE_COLOR,
                  fg=TEXT_COLOR,
                  activebackground='#C84A4B',
                  activeforeground=TEXT_COLOR,
                  font=('Arial', 10, 'bold'),
                  relief="flat",
                  padx=10,
                  pady=5).pack(fill='x', 
                               pady=(5, 10))
        
        # LOGOUT Button
        tk.Button(entry_frame,
                  text="🚪 LOGOUT",
                  command=self.logout,
                  bg="#751818",
                  fg=TEXT_COLOR,
                  activebackground='#555555',
                  activeforeground=TEXT_COLOR,
                  font=('Arial', 10, 'bold'),
                  relief="flat",
                  padx=10,
                  pady=5).pack(fill='x', 
                               pady=(20, 10))

        display_frame = tk.Frame(self, bg=PRIMARY_COLOR)
        display_frame.pack(side="right", 
                           fill="both", 
                           expand=True, 
                           padx=10, 
                           pady=10)

        self.create_sorting_controls(display_frame) 

        # Monthly Costs Label
        tk.Label(display_frame,
                 text="📋 Monthly Costs (Select a Month to Update)",
                 font=('Arial', 14, 'bold'),
                 bg=PRIMARY_COLOR,
                 fg=TEXT_COLOR).pack(pady=5, 
                                     anchor='w')


        # creating table for reading/viewing info
        tree_frame = tk.Frame(display_frame, bg=SECONDARY_COLOR)
        tree_frame.pack(fill='x', padx=5)

        columns = ("Month", "Water", "Electricity", "Others", "TOTAL")
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=columns, 
                                 show='headings', 
                                 height=10)

        tree_vsb = ttk.Scrollbar(tree_frame, 
                                 orient="vertical", 
                                 command=self.tree.yview)
        
        tree_hsb = ttk.Scrollbar(tree_frame, 
                                 orient="horizontal", 
                                 command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=tree_vsb.set, xscrollcommand=tree_hsb.set)

        self.tree.grid(row=0, 
                       column=0, 
                       sticky='nsew')
        
        tree_vsb.grid(row=0, 
                      column=1, 
                      sticky='ns')
        
        tree_hsb.grid(row=1, 
                      column=0, 
                      sticky='ew') 

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=120)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        graph_control_frame = tk.Frame(display_frame, bg=PRIMARY_COLOR)
        graph_control_frame.pack(pady=(20, 5),
                                 fill='x',
                                 padx=5)

        # Trend Analysis Label
        tk.Label(graph_control_frame,
                 text="📈 Trend Analysis:",
                 font=('Arial', 14, 'bold'),
                 bg=PRIMARY_COLOR,
                 fg=TEXT_COLOR).pack(side=tk.LEFT)


        # Total Trend Button 
        tk.Button(graph_control_frame,
                  text="Total Trend (Only)",
                  command=self.plot_total_trend,
                  bg=BUTTON_COLOR,
                  fg=TEXT_COLOR,
                  relief='flat').pack(side=tk.RIGHT, 
                                      padx=5)
        
        # Breakdown Trend Button
        tk.Button(graph_control_frame,
                  text="Breakdown Trend",
                  command=self.plot_breakdown_trend,
                  bg=MANAGE_COLOR, 
                  fg=TEXT_COLOR,
                  relief='flat').pack(side=tk.RIGHT, 
                                      padx=5)


        self.graph_frame = tk.Frame(display_frame, bg=PRIMARY_COLOR)
        self.graph_frame.pack(fill='both', 
                              expand=True, 
                              padx=5)


    # create sorting on the table for better readability
    def create_sorting_controls(self, master_frame):
        sort_frame = tk.Frame(master_frame, bg=PRIMARY_COLOR)
        sort_frame.pack(fill='x', pady=5)

        # the original sorting you see before you choose
        self.sort_var = tk.StringVar(self, value="🗓️ Sort by Latest Month")

        # sorting categories/choices
        sort_options = {
            "🗓️ Sort by Latest Month": "month DESC",
            "⬆️ Sort by Highest Total": "total DESC",
            "⬇️ Sort by Lowest Total": "total ASC"
        }
        
        # handling user sort selection
        def handle_sort_selection(choice):
            sql_order = sort_options[choice]
            self.sort_data_by_total(sql_order)

        # Sort By label
        tk.Label(sort_frame, 
                 text="Sort By:",
                 bg=PRIMARY_COLOR, 
                 fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5, 5))

        # option box to choose in the three sort choices
        sort_menu = ttk.OptionMenu(sort_frame, 
                                   self.sort_var, 
                                   self.sort_var.get(), 
                                   *sort_options.keys(), 
                                   command=handle_sort_selection)
        
        sort_menu.config(style='Sort.TMenubutton')
        sort_menu.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))





    #  DATA SORTING 
    def sort_data_by_total(self, sort_order):
        self.current_sort_order = sort_order
        self.load_data(sort_order)

        # sorting conditionals
        if sort_order == "total DESC":
             self.sort_var.set("⬆️ Sort by Highest Total")
        elif sort_order == "total ASC":
             self.sort_var.set("⬇️ Sort by Lowest Total")
        else:
             self.sort_var.set("🗓️ Sort by Latest Month")





    # DATA VISUALIZATION
    def _get_data_for_graph(self):
        # get data in db for graph (trend analysis)
        conn = self.get_db_connection() 
        cursor = conn.cursor()
        cursor.execute("SELECT month, water, electricity, others, total FROM expenses ORDER BY month ASC")
        data = cursor.fetchall()
        conn.close()
        return data


    # plotting the graph of total trend
    def plot_total_trend(self):
        data = self._get_data_for_graph() # gets the function for plotting/graphing
        
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # if theres no data...
        if not data:
            tk.Label(self.graph_frame,
                     text="There is no data for the graph. Save a few months to see trends!",
                     bg=PRIMARY_COLOR,
                     fg=TEXT_COLOR,
                     font=('Arial', 10, 'italic')).pack(pady=20)
            return

        months = [row[0] for row in data]
        total_costs = [row[4] for row in data]


        # creating line graphs for total monthtly expenses
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)

        ax.plot(months, 
                total_costs, 
                marker='o', 
                color=GRAPH_COLORS['Total'], 
                linewidth=3)

        fig.patch.set_facecolor(PRIMARY_COLOR)
        ax.set_facecolor(SECONDARY_COLOR)
        ax.tick_params(axis='x', colors=TEXT_COLOR)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        ax.set_ylabel("Total Expenses (₱)", color=TEXT_COLOR)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color=BUTTON_COLOR)

        ax.set_title("Total Monthly Expenses Trend",
                     color=TEXT_COLOR,
                     fontsize=12,
                     fontweight='bold')

        if len(months) > 6:
             plt.xticks(months, 
                        rotation=45, 
                        ha='right', 
                        fontsize=8)
        else:
             plt.xticks(months, 
                        rotation=0, 
                        fontsize=10)
        
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()


    # create a line graph in breakdown trend 
    def plot_breakdown_trend(self):
        data = self._get_data_for_graph() # gets the function to create/plot graph
        
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # if theres no data...
        if not data:
            tk.Label(self.graph_frame,
                     text="There is no data for the graph. Save a few months to see trends!",
                     bg=PRIMARY_COLOR,
                     fg=TEXT_COLOR,
                     font=('Arial', 10, 'italic')).pack(pady=20)
            return

        months = [row[0] for row in data]
        water_costs = [row[1] for row in data]
        electricity_costs = [row[2] for row in data]
        others_costs = [row[3] for row in data]

        # creating line graphs for breakdown trend
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)

        ax.plot(months, 
                water_costs, 
                marker='.', 
                color=GRAPH_COLORS['Water'], 
                linewidth=2, 
                label='Water')
        
        ax.plot(months, 
                electricity_costs, 
                marker='.', 
                color=GRAPH_COLORS['Electricity'], 
                linewidth=2, 
                label='Electricity')
        
        ax.plot(months, 
                others_costs, 
                marker='.', 
                color=GRAPH_COLORS['Others'], 
                linewidth=2, 
                label='Others')
        
        fig.patch.set_facecolor(PRIMARY_COLOR)
        ax.set_facecolor(SECONDARY_COLOR)
        ax.tick_params(axis='x', colors=TEXT_COLOR)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        ax.set_ylabel("Cost (₱)", color=TEXT_COLOR)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color=BUTTON_COLOR)


        ax.legend(loc='upper left', 
                  bbox_to_anchor=(1.0, 1.0), 
                  facecolor=PRIMARY_COLOR, 
                  edgecolor=TEXT_COLOR, 
                  labelcolor=TEXT_COLOR, 
                  ncol=1,
                  fontsize=8)

        ax.set_title("Monthly Breakdown Trend (Utilities & Others)",
                     color=TEXT_COLOR,
                     fontsize=12,
                     fontweight='bold')

        if len(months) > 6:
             plt.xticks(months, 
                        rotation=45, 
                        ha='right', 
                        fontsize=8)
        else:
             plt.xticks(months, 
                        rotation=0, 
                        fontsize=10)
        
        plt.tight_layout(rect=[0, 0, 1.03, 1])

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()


    def plot_graph_data(self):
        self.plot_total_trend()





    # EXPENSE OPERATION (CRUD)
    def save_expense(self): # saving data transactions
        data = {key: self.entries[key].get() for key in self.entries}

        try:
            month = data['month'].strip()
            
            # error handling if not valid month format
            if not is_valid_month_format(month):
                raise ValueError("Month format is incorrect (must be YYYY-MM).")

            water_str = clean_currency_input(data['water'])
            electricity_str = clean_currency_input(data['electricity'])
            
            water = float(water_str) if water_str else 0.0
            electricity = float(electricity_str) if electricity_str else 0.0
            
            if water < 0 or electricity < 0:
                raise ValueError("Bills must be non-negative numbers.")

        except ValueError as e: # error handling if user types str etc...
            messagebox.showerror("Input Error", f"Wrong Input: {e}.")
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # if the user inputs same month with data
        cursor.execute("SELECT total FROM expenses WHERE month=?", (month,))
        if cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", f"There is already a record for the month '{month}'. Please use the '✏️ EDIT RECORD' button if you wish to update it.")
            return

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE month=?", (month,))
        calculated_others = cursor.fetchone()[0] or 0.0
        others = calculated_others
        total = water + electricity + others

        # if no inputed all data entries 
        if total == 0.0:
            messagebox.showerror(
                "Missing Data Warning",
                "⚠️ No expenses recorded!\n\nPlease input the Water Bill, Electricity Bill, or add 'Other Expenses' before saving the record."
            )
            conn.close()
            return

        # conditionals which data entries is zero
        zero_fields = []
        if water == 0.0: zero_fields.append("Water Bill")
        if electricity == 0.0: zero_fields.append("Electricity Bill")
        if others == 0.0: zero_fields.append("'Other Expenses' (Categorized Spending)")

        # if the user not inputed either one in the data entries
        if zero_fields:
            warning_message_zero = (
                "⚠️ ZERO INPUT DETECTED!\n\n"
                "One or more expense fields were recorded as zero:\n"
                f"{', '.join(zero_fields)}\n\n"
                "Do you want to continue and save the record with these zero values?"
            )
            if not messagebox.askyesno("Confirm Zero Input", warning_message_zero):
                conn.close()
                return 

        cursor.execute("SELECT total, water, electricity, others FROM expenses ORDER BY month DESC LIMIT 1")
        last_month_data = cursor.fetchone()

        # pop up warning message if the total is increasing compared to last month
        comparison_warning_message = ""
        sdg_tip = SDG_TIPS["default"]

        if last_month_data:
            last_month_total = last_month_data[0]
            
            if total > last_month_total:
                difference = total - last_month_total
                comparison_warning_message = f"⚠️ WARNING! Save money! Your total expenses are high (₱{total:.2f}) compared to the previous month (₱{last_month_total:.2f}).\n\nIt increased by ₱{difference:.2f}. Save now!"

                increases = {
                    "water": water - (last_month_data[1] or 0),
                    "electricity": electricity - (last_month_data[2] or 0),
                    "others": others - (last_month_data[3] or 0)
                }

                max_increase_category = max(increases, key=lambda k: increases[k])

                if increases[max_increase_category] > 0:
                    sdg_tip = SDG_TIPS[max_increase_category]

                comparison_warning_message += f"\n\n{sdg_tip.upper()}"
            
            # if total decreased than last month, it congratulates you..
            elif total < last_month_total:
                messagebox.showinfo(
                    "🎉 Congratulations! You saved!",
                    f"Your total expenses have decreased (₱{total:.2f}) compared to the previous month (₱{last_month_total:.2f}).\n\nKeep saving!"
                )
        
        try:
            cursor.execute("""
                INSERT INTO expenses (month, water, electricity, others, total) 
                VALUES (?, ?, ?, ?, ?)
            """, (month, water, electricity, others, total))

            conn.commit()

            # if the total is increased than last month, it shows SDG tips on how to save expenses else, it saves the total expenses..
            if comparison_warning_message:
                messagebox.showwarning("Expense Warning & SDG Tip", comparison_warning_message)
            elif not last_month_data:
                messagebox.showinfo("Success!!", f"Expenses saved for {month}!")
            
            for key in ['water', 'electricity']:
                self.entries[key].delete(0, tk.END)

            self.load_data(self.current_sort_order)
            self.plot_total_trend()

        except Exception as e: # in case theres some exception errors
             messagebox.showerror("Database Error", f"An unexpected error occurred during save: {e}")

        conn.close()

    
    def edit_expense(self):
        data = {key: self.entries[key].get() for key in self.entries}

        try:
            month = data['month'].strip()
            water = float(clean_currency_input(data['water'] or 0))
            electricity = float(clean_currency_input(data['electricity'] or 0))

            # checks if it is not invalid format or equals to zero or a negative number
            if not is_valid_month_format(month):
                raise ValueError("Month format is incorrect (must be YYYY-MM).")
            if water < 0 or electricity < 0:
                 raise ValueError("Bills must be non-negative numbers.")

        except ValueError as e: # in case the users input is wrong
            messagebox.showerror("Input Error", f"Wrong Input: {e}. Bills must be valid numbers.")
            return

        # Error handling if the user not tap the tables data transaction
        if not self.tree.selection():
            messagebox.showwarning("Selection Error", "Please select a record from the list to edit.")
            return

        selected_values = self.tree.item(self.tree.focus(), 'values')
        original_month = selected_values[0]

        # error handling if the user changes the month when updating the data's
        if month != original_month:
            messagebox.showwarning("Month Mismatch", "The Month field must match the month of the selected record to update it.")
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # if successful, the data will be sent to db and appear in the table transaction
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE month=?", (month,))
        others = cursor.fetchone()[0] or 0.0
        total = water + electricity + others

        try:
            cursor.execute("""
                UPDATE expenses 
                SET water=?,
                electricity=?, 
                others=?, 
                total=? 
                WHERE month=?
            """, (water, electricity, others, total, month))

            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No record found for the month '{month}' to update.")
                conn.close()
                return

            conn.commit()
            messagebox.showinfo("Success!!", f"Expenses updated for {month}!")

            self.clear_entries()
            self.load_data(self.current_sort_order)
            self.plot_total_trend() 

        except Exception as e: # in case theres some exception error because of user
            messagebox.showerror("Database Error", f"Error updating record: {e}")

        conn.close()


    def delete_expense(self):
        selected_item = self.tree.focus()

        # if user not selected an transaction in the transaction table
        if not selected_item: 
            messagebox.showwarning("Selection Error", "First select a record from the list to delete.")
            return

        month_to_delete = self.tree.item(selected_item, 'values')[0]

        # pops up a warning message if the user surely wants to delete that transaction
        if messagebox.askyesno("Confirm Delete", f"⚠️ Are you sure you want to delete the record for {month_to_delete}?\n\nThis will permanently delete the monthly totals AND all categorized transactions associated with this month."):
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # when the user confirmed, the database deletes the data in the transaction table
            try:
                cursor.execute("DELETE FROM transactions WHERE month=?", (month_to_delete,))
                cursor.execute("DELETE FROM expenses WHERE month=?", (month_to_delete,))
                conn.commit()
                
                messagebox.showinfo("Success!!", f"Expenses have been cleared for {month_to_delete}.")

                self.clear_entries()
                self.load_data(self.current_sort_order)
                self.plot_total_trend()

            except Exception as e: # in case theres some error occured 
                messagebox.showerror("Database Error", f"Error deleting record: {e}")
            finally:
                conn.close()





# APPLICATION LAUNCHER
def start_app():

    # starts the app
    def start_main_tracker(): 
        app = ExpensesTrackerApp(start_app)
        app.mainloop()

    login_app = LoginWindow(start_main_tracker)
    login_app.mainloop()


if __name__ == "__main__":
    setup_database()  # Ensures database ready
    start_app()  # Launches application