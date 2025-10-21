import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime
import sys

# --- New Imports for Charting ---
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.dates import DateFormatter
except ImportError:
    print("Matplotlib not found. Please install it: pip install matplotlib")
    messagebox.showerror("Missing Library", "Matplotlib is required for charts. Please install it:\n\npip install matplotlib")
    sys.exit()
# ----------------------------------

DB_FILE = "fuel.db"
ADMIN_PASSWORD = "Viishnu15!"

# --- Database Functions (Unchanged) ---

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        total_rm REAL NOT NULL,
        price_per_litre REAL NOT NULL,
        distance_km REAL NOT NULL,
        litres REAL NOT NULL,
        km_per_litre REAL NOT NULL,
        l_per_100km REAL NOT NULL,
        rm_per_km REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_entry_to_db(date, total_rm, price_per_litre, distance_km):
    try:
        litres = total_rm / price_per_litre
        km_per_litre = distance_km / litres
        l_per_100km = (litres / distance_km) * 100
        rm_per_km = total_rm / distance_km

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO fuel_log (date, total_rm, price_per_litre, distance_km, litres, km_per_litre, l_per_100km, rm_per_km)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, total_rm, price_per_litre, distance_km, litres, km_per_litre, l_per_100km, rm_per_km))
        conn.commit()
        conn.close()
        
        return {
            "litres": litres, "km_per_litre": km_per_litre,
            "l_per_100km": l_per_100km, "rm_per_km": rm_per_km
        }
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to add entry: {e}")
        return None

def get_summary_data():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM fuel_log ORDER BY date DESC")
    all_entries = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(id), SUM(total_rm), SUM(litres), SUM(distance_km) FROM fuel_log")
    totals = cursor.fetchone()
    conn.close()
    
    count, total_rm, total_litres, total_distance = totals
    
    if total_distance and total_litres:
        avg_km_l = total_distance / total_litres
        avg_l_100km = (total_litres / total_distance) * 100
        avg_rm_km = total_rm / total_distance
    else:
        avg_km_l, avg_l_100km, avg_rm_km = 0, 0, 0
        
    summary = {
        "count": count or 0, "total_rm": total_rm or 0,
        "total_litres": total_litres or 0, "total_distance": total_distance or 0,
        "avg_km_l": avg_km_l, "avg_l_100km": avg_l_100km, "avg_rm_km": avg_rm_km
    }
    return all_entries, summary

def update_entry_in_db(entry_id, date, total_rm, price_per_litre, distance_km):
    try:
        litres = total_rm / price_per_litre
        km_per_litre = distance_km / litres
        l_per_100km = (litres / distance_km) * 100
        rm_per_km = total_rm / distance_km
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE fuel_log 
        SET date = ?, total_rm = ?, price_per_litre = ?, distance_km = ?, 
            litres = ?, km_per_litre = ?, l_per_100km = ?, rm_per_km = ?
        WHERE id = ?
        """, (date, total_rm, price_per_litre, distance_km, 
              litres, km_per_litre, l_per_100km, rm_per_km, 
              entry_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to update entry: {e}")
        return False

def delete_entry_from_db(entry_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fuel_log WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return True

# --- NEW: Function to get data specifically for plotting ---
def get_plot_data():
    """Fetches data sorted correctly for time-series plotting."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Order by date ASCENDING for line plots
    cursor.execute("SELECT date, km_per_litre, rm_per_km FROM fuel_log ORDER BY date ASC")
    data = cursor.fetchall()
    conn.close()
    return data

# --- Main Application Class (Modified) ---

class FuelTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 Fuel & Expense Tracker")
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # --- Input Fields ---
        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_entry = ttk.Entry(main_frame, width=30)
        self.date_entry.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.date_entry.insert(0, datetime.date.today().isoformat())

        ttk.Label(main_frame, text="Amount (RM):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.rm_entry = ttk.Entry(main_frame, width=30)
        self.rm_entry.grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(main_frame, text="Price/Litre (RM):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.price_entry = ttk.Entry(main_frame, width=30)
        self.price_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.price_entry.insert(0, "1.99")

        ttk.Label(main_frame, text="Distance (km):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.distance_entry = ttk.Entry(main_frame, width=30)
        self.distance_entry.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # --- Buttons ---
        self.add_button = ttk.Button(main_frame, text="Add Entry", command=self.submit_entry)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.summary_button = ttk.Button(main_frame, text="Show Full History", command=self.show_summary_window)
        self.summary_button.grid(row=5, column=0, columnspan=2, pady=5)
        
        # --- NEW: Dashboard Button ---
        self.dashboard_button = ttk.Button(main_frame, text="📊 Show Dashboard", command=self.show_dashboard_window)
        self.dashboard_button.grid(row=6, column=0, columnspan=2, pady=5)
        
        # --- Admin Section ---
        ttk.Separator(main_frame, orient='horizontal').grid(row=7, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.admin_button = ttk.Button(main_frame, text="Modify/Delete Entries (Admin)", command=self.open_admin_panel)
        self.admin_button.grid(row=8, column=0, columnspan=2, pady=5)
        
        # --- Status & Result ---
        self.status_label = ttk.Label(main_frame, text="Enter details and click 'Add Entry'")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(10,5))
        
        ttk.Label(main_frame, text="Last Entry Metrics:", font=('Helvetica', 10, 'bold')).grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=(5,0))
        self.result_text = tk.Text(main_frame, height=6, width=45, wrap=tk.WORD)
        self.result_text.grid(row=11, column=0, columnspan=2, pady=5)
        self.result_text.config(state=tk.DISABLED)

    def submit_entry(self):
        try:
            date = self.date_entry.get()
            total_rm = float(self.rm_entry.get())
            price_per_litre = float(self.price_entry.get())
            distance_km = float(self.distance_entry.get())
            
            if not date or total_rm <= 0 or price_per_litre <= 0 or distance_km <= 0:
                raise ValueError("All fields must be filled with positive numbers.")

            metrics = add_entry_to_db(date, total_rm, price_per_litre, distance_km)
            
            if metrics:
                self.result_text.config(state=tk.NORMAL)
                self.result_text.delete(1.0, tk.END)
                result_str = (
                    f"Entry Added for {date}:\n"
                    f"  Litres: {metrics['litres']:.2f} L\n"
                    f"  Efficiency: {metrics['km_per_litre']:.2f} km/L\n"
                    f"  Consumption: {metrics['l_per_100km']:.2f} L/100km\n"
                    f"  Cost: RM {metrics['rm_per_km']:.3f} per km"
                )
                self.result_text.insert(tk.END, result_str)
                self.result_text.config(state=tk.DISABLED)
                
                self.status_label.config(text=f"✅ Entry added successfully for {date}!", foreground="green")
                self.rm_entry.delete(0, tk.END)
                self.distance_entry.delete(0, tk.END)
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}\nPlease enter valid numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def show_summary_window(self):
        summary_win = tk.Toplevel(self.root)
        summary_win.title("Full History & Summary")
        summary_win.geometry("800x600")
        
        frame = ttk.Frame(summary_win, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        all_entries, summary = get_summary_data()
        
        summary_frame = ttk.LabelFrame(frame, text="Overall Averages")
        summary_frame.pack(fill=tk.X, pady=5)
        
        avg_text = (
            f"Total Entries: {summary['count']} | Total Distance: {summary['total_distance']:.2f} km | Total Spent: RM {summary['total_rm']:.2f}\n"
            f"Avg. Efficiency: {summary['avg_km_l']:.2f} km/L | "
            f"Avg. Consumption: {summary['avg_l_100km']:.2f} L/100km | "
            f"Avg. Cost: RM {summary['avg_rm_km']:.3f}/km"
        )
        ttk.Label(summary_frame, text=avg_text, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)

        history_frame = ttk.LabelFrame(frame, text="All Entries")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        cols = ('ID', 'Date', 'RM', 'Price/L', 'Dist(km)', 'Litres', 'km/L', 'L/100km', 'RM/km')
        tree = ttk.Treeview(history_frame, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor=tk.CENTER)
        tree.column('Date', anchor=tk.W, width=90)
        tree.column('ID', width=30)
        
        for entry in all_entries:
            tree.insert("", tk.END, values=(
                entry['id'], entry['date'], f"{entry['total_rm']:.2f}",
                f"{entry['price_per_litre']:.2f}", f"{entry['distance_km']:.1f}",
                f"{entry['litres']:.2f}", f"{entry['km_per_litre']:.2f}",
                f"{entry['l_per_100km']:.2f}", f"{entry['rm_per_km']:.3f}"
            ))
            
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def open_admin_panel(self):
        password = simpledialog.askstring("Password Required", "Enter Admin Password:", show='*')
        
        if password == ADMIN_PASSWORD:
            self.create_admin_window()
        elif password is not None:
            messagebox.showerror("Access Denied", "Incorrect password.")
            
    def create_admin_window(self):
        admin_win = tk.Toplevel(self.root)
        admin_win.title("🔒 Admin Panel - Modify/Delete Entries")
        admin_win.geometry("900x600")
        admin_win.grab_set()
        
        frame = ttk.Frame(admin_win, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ('ID', 'Date', 'RM', 'Price/L', 'Dist(km)', 'Litres', 'km/L', 'L/100km', 'RM/km')
        tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor=tk.CENTER)
        tree.column('Date', anchor=tk.W, width=90)
        tree.column('ID', width=30)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        def refresh_tree():
            for item in tree.get_children():
                tree.delete(item)
            all_entries, _ = get_summary_data()
            for entry in all_entries:
                tree.insert("", tk.END, values=(
                    entry['id'], entry['date'], f"{entry['total_rm']:.2f}",
                    f"{entry['price_per_litre']:.2f}", f"{entry['distance_km']:.1f}",
                    f"{entry['litres']:.2f}", f"{entry['km_per_litre']:.2f}",
                    f"{entry['l_per_100km']:.2f}", f"{entry['rm_per_km']:.3f}"
                ))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def on_modify():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select an entry to modify.")
                return
            item_data = tree.item(selected_item, 'values')
            self.create_modify_window(admin_win, item_data, refresh_tree)
        
        def on_delete():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select an entry to delete.")
                return
            item_data = tree.item(selected_item, 'values')
            entry_id = item_data[0]
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete entry ID {entry_id} ({item_data[1]})?"):
                if delete_entry_from_db(entry_id):
                    messagebox.showinfo("Success", f"Entry ID {entry_id} deleted.")
                    refresh_tree()
                else:
                    messagebox.showerror("Error", f"Failed to delete entry ID {entry_id}.")

        modify_btn = ttk.Button(button_frame, text="Modify Selected Entry", command=on_modify)
        modify_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = ttk.Button(button_frame, text="Delete Selected Entry", command=on_delete)
        delete_btn.pack(side=tk.LEFT, padx=5)
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=refresh_tree)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        refresh_tree()
        
    def create_modify_window(self, parent_win, item_data, refresh_callback):
        entry_id = item_data[0]
        modify_win = tk.Toplevel(parent_win)
        modify_win.title(f"Edit Entry ID: {entry_id}")
        modify_win.grab_set()
        
        frame = ttk.Frame(modify_win, padding="15")
        frame.pack()
        
        ttk.Label(frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        date_var = tk.StringVar(value=item_data[1])
        date_e = ttk.Entry(frame, textvariable=date_var, width=25)
        date_e.grid(row=0, column=1)
        
        ttk.Label(frame, text="Amount (RM):").grid(row=1, column=0, sticky=tk.W, pady=5)
        rm_var = tk.StringVar(value=item_data[2])
        rm_e = ttk.Entry(frame, textvariable=rm_var, width=25)
        rm_e.grid(row=1, column=1)

        ttk.Label(frame, text="Price/Litre (RM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        price_var = tk.StringVar(value=item_data[3])
        price_e = ttk.Entry(frame, textvariable=price_var, width=25)
        price_e.grid(row=2, column=1)
        
        ttk.Label(frame, text="Distance (km):").grid(row=3, column=0, sticky=tk.W, pady=5)
        dist_var = tk.StringVar(value=item_data[4])
        dist_e = ttk.Entry(frame, textvariable=dist_var, width=25)
        dist_e.grid(row=3, column=1)
        
        def on_update():
            try:
                new_date = date_var.get()
                new_rm = float(rm_var.get())
                new_price = float(price_var.get())
                new_dist = float(dist_var.get())
                
                if not new_date or new_rm <= 0 or new_price <= 0 or new_dist <= 0:
                    raise ValueError("All fields must be positive values.")
                
                if update_entry_in_db(entry_id, new_date, new_rm, new_price, new_dist):
                    messagebox.showinfo("Success", f"Entry ID {entry_id} updated successfully.", parent=modify_win)
                    refresh_callback()
                    modify_win.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update database.", parent=modify_win)
                    
            except ValueError as e:
                messagebox.showerror("Input Error", f"Invalid data: {e}", parent=modify_win)

        update_btn = ttk.Button(frame, text="Update Entry", command=on_update)
        update_btn.grid(row=4, column=0, columnspan=2, pady=10)

    # --- NEW DASHBOARD/CHARTING METHOD ---

    def show_dashboard_window(self):
        """Creates a new window and displays Matplotlib charts."""
        
        plot_data = get_plot_data()
        
        if len(plot_data) < 2:
            messagebox.showinfo("Not Enough Data", "You need at least two entries to draw a chart.")
            return

        dash_win = tk.Toplevel(self.root)
        dash_win.title("📊 Data Dashboard")
        dash_win.geometry("900x700")

        frame = ttk.Frame(dash_win, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # --- Process Data for Plotting ---
        dates = []
        km_l_values = []
        rm_km_values = []
        
        for row in plot_data:
            try:
                # Convert date string (YYYY-MM-DD) to datetime object
                dates.append(datetime.datetime.strptime(row['date'], '%Y-%m-%d').date())
                km_l_values.append(row['km_per_litre'])
                rm_km_values.append(row['rm_per_km'])
            except ValueError:
                print(f"Skipping bad date format: {row['date']}")
                continue

        # --- Create the Matplotlib Figure and Subplots ---
        # We create one Figure that holds two subplots (ax1, ax2)
        fig = Figure(figsize=(8, 6), dpi=100)
        fig.subplots_adjust(hspace=0.4) # Add space between plots
        
        ax1 = fig.add_subplot(2, 1, 1) # (rows, columns, plot_number)
        ax2 = fig.add_subplot(2, 1, 2)

        # --- Plot 1: Efficiency (km/L) ---
        ax1.plot(dates, km_l_values, marker='o', linestyle='-', color='b')
        ax1.set_title("Fuel Efficiency Over Time")
        ax1.set_ylabel("Efficiency (km/L)")
        ax1.grid(True)
        
        # --- Plot 2: Cost (RM/km) ---
        ax2.plot(dates, rm_km_values, marker='s', linestyle='--', color='r')
        ax2.set_title("Cost Per Kilometre Over Time")
        ax2.set_ylabel("Cost (RM/km)")
        ax2.set_xlabel("Date")
        ax2.grid(True)
        
        # Format the x-axis for both plots to show dates nicely
        date_format = DateFormatter("%Y-%m-%d")
        ax1.xaxis.set_major_formatter(date_format)
        ax2.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate() # Auto-rotate dates to prevent overlap

        # --- Embed the Figure in the Tkinter Window ---
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        

# --- Main execution ---
if __name__ == "__main__":
    setup_database()
    root_window = tk.Tk()
    app = FuelTrackerApp(root_window)
    root_window.mainloop()