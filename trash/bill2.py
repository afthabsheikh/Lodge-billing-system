import tkinter as tk
import datetime
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
import sqlite3

# Create or connect to the SQLite database
conn = sqlite3.connect('lodge_track.db')
cursor = conn.cursor()

# Create tables for Entries and Bills if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Entries (
        id INTEGER PRIMARY KEY,
        guest_name TEXT,
        entry_date TEXT,
        exit_date TEXT,
        bill FLOAT
    ) 
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bills (
        id INTEGER PRIMARY KEY,
        guest_name TEXT,
        entry_date TEXT,
        exit_date TEXT,
        bill FLOAT,
        amount REAL
    )
''')

class LodgeTrackApp:
    def __init__(self, root):

        self.root = root
        self.root.geometry("1100x400")
        self.root.title("LodgeTrackApp")
        self.root.configure(bg="dark grey")
        self.create_treeview()
        
        self.add_info_button = tk.Button(root, text="Add Customer", width=13, bg='light blue', command=self.add_info)
        self.add_info_button.grid(row=2, column=0, padx=50, pady=10)

        self.display_entries_button = tk.Button(root, text="Display Entries", width=13, bg='light blue', command=self.display_entries)
        self.display_entries_button.grid(row=2, column=1, padx=50, pady=10)

        self.delete_button = tk.Button(root, text="Delete", width=13, bg='light blue', command=self.delete_info)
        self.delete_button.grid(row=2, column=2, padx=50, pady=10)

        self.update_button = tk.Button(root, text="Update", width=13, bg='light blue', command=self.update_info)
        self.update_button.grid(row=2, column=3, padx=50, pady=10)

        self.generate_bill_button = tk.Button(root, text="Generate Bill", width=13, bg='light blue', command=self.generate_bill)
        self.generate_bill_button.grid(row=2, column=4, padx=50, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Entry", "Exit", "Bill"))
        self.tree.column("#0", width=0)
        self.tree.heading("#1", text="ID")
        self.tree.heading("#2", text="Name")
        self.tree.heading("#3", text="Entry")
        self.tree.heading("#4", text="Exit")
        self.tree.heading("#5", text="Bill")
        self.tree.grid(row=4, columnspan=6, padx=50, pady=10)
        
    def add_info(self):
        # Create a new Toplevel window for customer details
        self.customer_details_window = tk.Toplevel(self.root)
        self.customer_details_window.geometry("400x300")
        self.customer_details_window.title("Customer Details")
        self.customer_details_window.configure(bg="black")

        guest_name_label = tk.Label(self.customer_details_window, bg='white', text="Guest Name:")
        guest_name_label.grid(row=0, column=0, padx=10, pady=10)

        self.guest_name_entry = tk.Entry(self.customer_details_window)
        self.guest_name_entry.grid(row=0, column=1, padx=10, pady=10)

        entry_date_label = tk.Label(self.customer_details_window, bg='white', text="Entry Date (YYYY-MM-DD):")
        entry_date_label.grid(row=1, column=0, padx=10, pady=10)

        self.entry_date_calendar = DateEntry(self.customer_details_window, date_pattern="yyyy-mm-dd")
        self.entry_date_calendar.grid(row=1, column=1, padx=10, pady=10)

        exit_date_label = tk.Label(self.customer_details_window, bg='white', text="Exit Date (YYYY-MM-DD):")
        exit_date_label.grid(row=2, column=0, padx=10, pady=10)

        self.exit_date_calendar = DateEntry(self.customer_details_window, date_pattern="yyyy-mm-dd")
        self.exit_date_calendar.grid(row=2, column=1, padx=10, pady=10)

        add_entry_exit_button = tk.Button(self.customer_details_window, bg='red', text="Add Entry/Exit", command=self.add_entry_exit)
        add_entry_exit_button.grid(row=3, column=1, padx=10, pady=10)
        
    def add_entry_exit(self):
        guest_name = self.guest_name_entry.get()
        entry_datetime = self.entry_date_calendar.get()
        exit_datetime = self.exit_date_calendar.get()

        if entry_datetime > exit_datetime:
            tk.messagebox.showinfo("Invalid", "Invalid date entry: Entry date must be lesser than exit date.")
        elif exit_datetime < entry_datetime:
            tk.messagebox.showinfo("Invalid", "Invalid date entry: Entry date must be lesser than exit date.")
        else:
            cursor.execute("INSERT INTO Entries (guest_name, entry_date, exit_date) VALUES (?, ?, ?)",
                       (guest_name, entry_datetime, exit_datetime))
            conn.commit()
            tk.messagebox.showinfo("Success", "Entry and exit recorded successfully")
        
        if self.customer_details_window:
            self.customer_details_window.destroy()

    def delete_info(self):
        # Get the selected item in the Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            tk.messagebox.showwarning("Warning", "No customer selected for deletion.")
            return

        # Retrieve the customer's ID from the selected item
        customer_id = self.tree.item(selected_item, "values")[0]

        # Delete the customer's details from the Treeview
        self.tree.delete(selected_item)

        cursor.execute("DELETE FROM Entries WHERE id=?", (customer_id,))
        conn.commit()

        # Update the customer IDs for the remaining customers in the Treeview
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(i + 1,) + self.tree.item(item, "values")[1:])

        cursor.execute("UPDATE Entries SET id=id-1 WHERE id > ?", (customer_id,))
        conn.commit()
        
    def update_info(self):
        # Get the selected item in the Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            tk.messagebox.showwarning("Warning", "No customer selected for editing.")
            return

        # Retrieve the customer's ID from the selected item
        customer_id = self.tree.item(selected_item, "values")[0]

        cursor.execute("SELECT guest_name, entry_date, exit_date FROM Entries WHERE id=?", (customer_id,))
        customer_details = cursor.fetchone()

        if customer_details:
            # Create a popup window for editing
            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.title("Edit Customer Details")
            self.edit_window.geometry('400x300')
            self.edit_window.configure(bg="black")

            guest_name_label = tk.Label(self.edit_window, bg='white', text="Guest Name:")
            guest_name_label.grid(row=0, column=0, padx=10, pady=10)

            self.updated_guest_name_entry = tk.Entry(self.edit_window)
            self.updated_guest_name_entry.insert(0, customer_details[0])  # Set the current value
            self.updated_guest_name_entry.grid(row=0, column=1, padx=10, pady=10)

            entry_date_label = tk.Label(self.edit_window, bg='white', text="Entry Date (YYYY-MM-DD):")
            entry_date_label.grid(row=1, column=0, padx=10, pady=10)

            self.updated_entry_date_calendar = DateEntry(self.edit_window, date_pattern="yyyy-mm-dd")
            self.updated_entry_date_calendar.set_date(customer_details[1])  # Set the current value
            self.updated_entry_date_calendar.grid(row=1, column=1, padx=10, pady=10)

            exit_date_label = tk.Label(self.edit_window, bg='white', text="Exit Date (YYYY-MM-DD):")
            exit_date_label.grid(row=4, column=0, padx=10, pady=10)

            self.updated_exit_date_calendar = DateEntry(self.edit_window, date_pattern="yyyy-mm-dd")
            self.updated_exit_date_calendar.set_date(customer_details[2])  # Set the current value
            self.updated_exit_date_calendar.grid(row=4, column=1, padx=10, pady=10)

            # Create a button to update the details
            update_button = tk.Button(self.edit_window, text="Update", bg='red', command=lambda: self.update_customer_details(customer_id))
            update_button.grid(row=6, column=1, padx=10, pady=10)

    def update_customer_details(self, customer_id):
        # Get updated values from input fields
        updated_guest_name = self.updated_guest_name_entry.get()
        updated_entry_date = self.updated_entry_date_calendar.get()
        updated_exit_date = self.updated_exit_date_calendar.get()

        # Update the Treeview with the new values
        selected_item = self.tree.selection()
        self.tree.item(selected_item, values=(customer_id, updated_guest_name, updated_entry_date, updated_exit_date))

        if updated_entry_date > updated_exit_date:
            tk.messagebox.showinfo("Invalid", "Invalid date entry: Entry date must be lesser than exit date.")
        elif updated_exit_date < updated_entry_date:
            tk.messagebox.showinfo("Invalid", "Invalid date entry: Entry date must be lesser than exit date.")
        else:
            # Update the Treeview with the new values
            selected_item = self.tree.selection()
            self.tree.item(selected_item, values=(customer_id, updated_guest_name, updated_entry_date, updated_exit_date))

            cursor.execute("UPDATE Entries SET guest_name=?, entry_date=?, exit_date=? WHERE id=?",
                       (updated_guest_name, updated_entry_date, updated_exit_date, customer_id))
            conn.commit()

            tk.messagebox.showinfo("Success", "Customer details updated successfully.")
        if self.edit_window:
            self.edit_window.destroy()

    def generate_bill(self):
        # Get the selected item in the Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            tk.messagebox.showwarning("Warning", "No customer selected to generate a bill.")
            return

        # Retrieve the customer's entry and exit dates from the Treeview
        customer_id = self.tree.item(selected_item, "values")[0]
        entry_date = self.tree.item(selected_item, "values")[2]
        exit_date = self.tree.item(selected_item, "values")[3]

        bill = self.calculate_bill(entry_date, exit_date)

        # Update the bill amount in the database for the selected customer
        cursor.execute("UPDATE Entries SET bill=? WHERE id=?", (bill, customer_id))
        conn.commit()

        # Display the bill in a message box
        tk.messagebox.showinfo("Bill", f"Bill Amount: Rs{bill:.2f}")

    def calculate_bill(self, entry_date, exit_date):
        try:
            entry_date = datetime.datetime.strptime(entry_date, "%Y-%m-%d")
            exit_date = datetime.datetime.strptime(exit_date, "%Y-%m-%d")
            delta = exit_date - entry_date
            num_days = delta.days
            daily_rate = 100  # Replace with your daily rate
            bill = num_days * daily_rate
            return bill
        except ValueError:
            return 0 
        
    def display_entries(self):
        self.clear_treeview()
        cursor.execute("SELECT * FROM Entries")
        entries = cursor.fetchall()
        self.display_data(entries)

    def display_data(self, data):
        for row in data:
            self.tree.insert("", "end", values=row)

    def clear_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

if __name__ == "__main__":
    root = tk.Tk()
    app = LodgeTrackApp(root)
    root.mainloop()
