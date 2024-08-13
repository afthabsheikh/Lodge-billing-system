import tkinter as tk
from tkinter import ttk,messagebox
from tkcalendar import Calendar, DateEntry
from tktimepicker import AnalogPicker, AnalogThemes
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk
import datetime
from sqlite3 import connect

# Create or connect to the SQLite database
conn = connect('lodge.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Entries (
        id INTEGER PRIMARY KEY,
        guest_name TEXT,
        entry_date TEXT,
        entry_time TEXT,
        exit_date TEXT,
        exit_time TEXT,
        bill FLOAT
    ) 
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bills (
        id INTEGER PRIMARY KEY,
        guest_name TEXT,
        entry_date TEXT,
        entry_time TEXT,
        exit_date TEXT,
        exit_time TEXT,
        bill FLOAT,
        amount REAL
    )
''')

class LodgeTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1500x700")
        self.root.title("LodgeTrackApp")
        
        style = ThemedStyle()
        style.set_theme("radiance")
        self.create_treeview()
        self.create_buttons()

    def create_buttons(self):
        #self.button_frame=tk.Frame(root)
        #self.button_frame.grid(row=0,column=1,padx=10,pady=10,sticky="nsew")

        #self.root.grid_columnconfigure(1,weight=0)
        add_info_button = ttk.Button(self.root, text="Add Customer", width=5, style="Custom.TButton", command=self.add_info)
        add_info_button.grid(row=0, column=0, padx=50, pady=10, ipadx=27, ipady=5)

        display_entries_button = ttk.Button(self.root, text="Display Entries", style="Custom.TButton", command=self.display_entries)
        display_entries_button.grid(row=0, column=1, padx=50, pady=10, ipadx=25, ipady=5)

        delete_button = ttk.Button(self.root, text="Delete", style="Custom.TButton", command=self.delete_info)
        delete_button.grid(row=0, column=2, padx=50, pady=10, ipadx=25, ipady=5)

        update_button = ttk.Button(self.root, text="Update", style="Custom.TButton", command=self.update_info)
        update_button.grid(row=0, column=3, padx=50, pady=10, ipadx=25, ipady=5)

        generate_bill_button = ttk.Button(self.root, text="Generate Bill", style="Custom.TButton", command=self.generate_bill)
        generate_bill_button.grid(row=0, column=4, padx=50, pady=10, ipadx=25, ipady=5)

    def create_treeview(self):
        #self.tree_frame=tk.Frame(root)
        #self.tree_frame.grid(row=0,column=0,sticky="nsew")
        #root.grid_rowconfigure(0,weight=1)
        #root.grid_columnconfigure(0,weight=1)
        
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Entry date", "Entry time", "Exit date", "Exit time", "Bill"))
        self.tree.column("#0", width=0)
        self.tree.heading("#1", text="ID")
        self.tree.heading("#2", text="Name")
        self.tree.heading("#3", text="Entry date")
        self.tree.heading("#4", text="Entry time")
        self.tree.heading("#5", text="Exit date")
        self.tree.heading("#6", text="Exit time")
        self.tree.heading("#7", text="Bill")
        self.tree.grid(row=5, columnspan=5, padx=0, pady=10)

    def add_info(self):
        self.customer_details_window = tk.Toplevel(self.root)
        self.customer_details_window.geometry("500x500")
        self.customer_details_window.title("Customer Details")
        self.customer_details_window.configure(bg="light grey")

        guest_name_label = ttk.Label(self.customer_details_window, text="Guest Name:")
        guest_name_label.grid(row=0, column=0, padx=10, pady=10)
        guest_name_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light grey")

        self.guest_name_entry = ttk.Entry(self.customer_details_window)
        self.guest_name_entry.grid(row=0, column=1, padx=10, pady=10)

        entry_date_label = ttk.Label(self.customer_details_window, text="Entry Date (YYYY-MM-DD):")
        entry_date_label.grid(row=1, column=0, padx=10, pady=10)
        entry_date_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light grey")

        self.entry_date_calendar = DateEntry(self.customer_details_window, date_pattern="yyyy-mm-dd")
        self.entry_date_calendar.grid(row=1, column=1, padx=10, pady=10)

        entry_time_label = ttk.Label(self.customer_details_window, text="Entry Time (HH:MM):")
        entry_time_label.grid(row=2, column=0, padx=10, pady=10)
        entry_time_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light grey")

        self.entry_time_entry = ttk.Entry(self.customer_details_window)
        self.entry_time_entry.grid(row=2, column=1, padx=10, pady=10)

        exit_date_label = ttk.Label(self.customer_details_window, text="Exit Date (YYYY-MM-DD):")
        exit_date_label.grid(row=3, column=0, padx=10, pady=10)
        exit_date_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light grey")

        self.exit_date_calendar = DateEntry(self.customer_details_window, date_pattern="yyyy-mm-dd")
        self.exit_date_calendar.grid(row=3, column=1, padx=10, pady=10)

        exit_time_label = ttk.Label(self.customer_details_window, text="Exit Time (HH:MM):")
        exit_time_label.grid(row=4, column=0, padx=10, pady=10)
        exit_time_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light grey")

        self.exit_time_entry = ttk.Entry(self.customer_details_window)
        self.exit_time_entry.grid(row=4, column=1, padx=10, pady=10)

        add_entry_exit_button = ttk.Button(self.customer_details_window, text="Add Entry/Exit", style="Custom.TButton", command=self.add_entry_exit)
        add_entry_exit_button.grid(row=5, column=1, padx=10, pady=10, ipadx=15, ipady=2)

    def add_entry_exit(self):
        guest_name = self.guest_name_entry.get()
        entry_date_str = self.entry_date_calendar.get()
        entry_time_str = self.entry_time_entry.get()
        exit_date_str = self.exit_date_calendar.get()
        exit_time_str = self.exit_time_entry.get()

        entry_datetime_str = f"{entry_date_str} {entry_time_str}"
        exit_datetime_str = f"{exit_date_str} {exit_time_str}"

        try:
            entry_datetime = datetime.datetime.strptime(entry_datetime_str, "%Y-%m-%d %H:%M")
            exit_datetime = datetime.datetime.strptime(exit_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showinfo("Invalid", "Invalid date and time format. Please use YYYY-MM-DD HH:MM!!")
            return

        if entry_datetime > exit_datetime:
            messagebox.showinfo("Invalid", "Invalid date entry: Entry date must be earlier than exit date.")
        else:
            cursor.execute("INSERT INTO Entries (guest_name, entry_date, entry_time, exit_date, exit_time, bill) VALUES (?, ?, ?, ?, ?, ?)",
                           (guest_name, entry_date_str, entry_time_str, exit_date_str, exit_time_str, 0.0))
            conn.commit()
            messagebox.showinfo("Success", "Entry and exit recorded successfully")

        if self.customer_details_window:
            self.customer_details_window.destroy()

    def delete_info(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showwarning("Warning", "No customer selected for deletion.")
            return

        customer_id = self.tree.item(selected_item, "values")[0]
        self.tree.delete(selected_item)

        cursor.execute("DELETE FROM Entries WHERE id=?", (customer_id,))
        conn.commit()

        # Update the customer IDs for the remaining customers in the Treeview
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(i + 1,) + self.tree.item(item, "values")[1:])

        cursor.execute("UPDATE Entries SET id=id-1 WHERE id > ?", (customer_id,))
        conn.commit()

    def update_info(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showwarning("Warning", "No customer selected for editing.")
            return

        customer_id = self.tree.item(selected_item, "values")[0]

        cursor.execute("SELECT guest_name, entry_date, exit_date, entry_time, exit_time FROM Entries WHERE id=?", (customer_id,))
        customer_details = cursor.fetchone()

        if customer_details:
            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.title("Edit Customer Details")
            self.edit_window.geometry('500x500')
            self.edit_window.configure(bg="light grey")

            guest_name_label = ttk.Label(self.edit_window, text="Guest Name:")
            guest_name_label.grid(row=0, column=0, padx=10, pady=10)
            guest_name_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light blue")

            self.updated_guest_name_entry = ttk.Entry(self.edit_window)
            self.updated_guest_name_entry.insert(0, customer_details[0])  # Set the current value
            self.updated_guest_name_entry.grid(row=0, column=1, padx=10, pady=10)

            entry_date_label = ttk.Label(self.edit_window, text="Entry Date (YYYY-MM-DD):")
            entry_date_label.grid(row=1, column=0, padx=10, pady=10)
            entry_date_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light blue")

            self.updated_entry_date_calendar = DateEntry(self.edit_window, date_pattern="yyyy-mm-dd")
            self.updated_entry_date_calendar.set_date(customer_details[1])
            self.updated_entry_date_calendar.grid(row=1, column=1, padx=10, pady=10)

            entry_time_label = ttk.Label(self.edit_window, text="Entry Time (HH:MM):")
            entry_time_label.grid(row=2, column=0, padx=10, pady=10)
            entry_time_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light blue")

            self.updated_entry_time_entry = ttk.Entry(self.edit_window)
            self.updated_entry_time_entry.insert(0, customer_details[3])
            self.updated_entry_time_entry.grid(row=2, column=1, padx=10, pady=10)

            exit_date_label = ttk.Label(self.edit_window, text="Exit Date (YYYY-MM-DD):")
            exit_date_label.grid(row=3, column=0, padx=10, pady=10)
            exit_date_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light blue")

            self.updated_exit_date_calendar = DateEntry(self.edit_window, date_pattern="yyyy-mm-dd")
            self.updated_exit_date_calendar.set_date(customer_details[2])
            self.updated_exit_date_calendar.grid(row=3, column=1, padx=10, pady=10)

            exit_time_label = ttk.Label(self.edit_window, text="Exit Time (HH:MM):")
            exit_time_label.grid(row=4, column=0, padx=10, pady=10)
            exit_time_label.config(font=("Helvetica",12,"bold"),foreground="black",background="light blue")

            self.updated_exit_time_entry = ttk.Entry(self.edit_window)
            self.updated_exit_time_entry.insert(0, customer_details[4])
            self.updated_exit_time_entry.grid(row=4, column=1, padx=10, pady=10)

            update_button = ttk.Button(self.edit_window, text="Update", style="Custom.TButton", command=lambda: self.update_customer_details(customer_id))
            update_button.grid(row=5, column=1, padx=10, pady=10, ipadx=25, ipady=5)

    def update_customer_details(self, customer_id):
        updated_guest_name = self.updated_guest_name_entry.get()
        updated_entry_date = self.updated_entry_date_calendar.get()
        updated_entry_time = self.updated_entry_time_entry.get()
        updated_exit_date = self.updated_exit_date_calendar.get()
        updated_exit_time = self.updated_exit_time_entry.get()

        updated_entry_datetime_str = f"{updated_entry_date} {updated_entry_time}"
        updated_exit_datetime_str = f"{updated_exit_date} {updated_exit_time}"

        try:
            updated_entry_datetime = datetime.datetime.strptime(updated_entry_datetime_str, "%Y-%m-%d %H:%M")
            updated_exit_datetime = datetime.datetime.strptime(updated_exit_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showinfo("Invalid", "Invalid date and time format. Please use YYYY-MM-DD HH:MM!!")
            return

        if updated_entry_datetime > updated_exit_datetime:
            messagebox.showinfo("Invalid", "Invalid date entry: Entry date must be earlier than exit date.")
        else:
            # Update the Treeview with the new values
            selected_item = self.tree.selection()
            self.tree.item(selected_item, values=(customer_id, updated_guest_name, updated_entry_date, updated_entry_time, updated_exit_date, updated_exit_time, 0.0))
            cursor.execute("UPDATE Entries SET guest_name=?, entry_date=?, entry_time=?, exit_date=?, exit_time=? WHERE id=?",
                           (updated_guest_name, updated_entry_date, updated_entry_time, updated_exit_date, updated_exit_time, customer_id))
            conn.commit()
            messagebox.showinfo("Success", "Customer details updated successfully.")

        if self.edit_window:
            self.edit_window.destroy()

    def generate_bill(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showwarning("Warning", "No customer selected to generate a bill.")
            return

        # Retrieve the customer's entry and exit dates from the Treeview
        customer_id = self.tree.item(selected_item, "values")[0]
        entry_date = self.tree.item(selected_item, "values")[2]
        entry_time = self.tree.item(selected_item, "values")[3]
        exit_date = self.tree.item(selected_item, "values")[4]
        exit_time = self.tree.item(selected_item, "values")[5]

        bill = self.calculate_bill(entry_date, entry_time, exit_date, exit_time)
        cursor.execute("UPDATE Entries SET bill=? WHERE id=?", (bill, customer_id))
        conn.commit()

        messagebox.showinfo("Bill", f"Bill Amount: Rs{bill:.2f}")

    def calculate_bill(self, entry_date, entry_time, exit_date, exit_time):
        try:
            entry_datetime = datetime.datetime.strptime(f"{entry_date} {entry_time}", "%Y-%m-%d %H:%M")
            exit_datetime = datetime.datetime.strptime(f"{exit_date} {exit_time}", "%Y-%m-%d %H:%M")
            delta = exit_datetime - entry_datetime
            num_days = delta.days
            num_seconds=delta.seconds
            num_hours=(num_days * 24)+(num_seconds//3600)
            #daily_rate = 900  # Replace based on daily rate
            hour_rate = 100
            bill = num_hours * hour_rate

            print("Entry date:",entry_datetime)
            print("Exit date:",exit_datetime)
            print("Days:",num_days)
            print("Hours:",num_hours)
            print("Ganerated bill:",bill)
            return bill
        except ValueError as e:
            print("Error",e)
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
