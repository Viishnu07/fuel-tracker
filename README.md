# 🚗 Fuel & Expense Tracker (Tkinter + SQLite)

A simple desktop application to log and analyze your vehicle’s fuel usage and expenses. Built using **Python**, **Tkinter**, **SQLite**, and **Matplotlib**.

This project was started as a fun experiment to track fuel efficiency and spending, inspired by the Malaysian government's BUDI95 fuel subsidy program.

---

## 📸 Preview

<img width="474" height="610" alt="Screenshot 2025-10-22 000849" src="https://github.com/user-attachments/assets/48a5d350-fd40-4913-adc4-2a6acdda9fed" />

---

## ✨ Features

-   **Log Entries:** Easily add new fuel purchases (date, amount, price, distance).
-   **Detailed Metrics:** Automatically calculates `km/L`, `L/100km`, and `RM/km` for each entry.
-   **Data Visualization:** View interactive charts for fuel efficiency and cost-per-km trends over time.
-   **Admin Panel:** Secure (password-protected) section to **modify** or **delete** incorrect entries.
-   **Full History:** View a complete, sortable table of all past entries and overall averages.

---

## 🧰 Tech Stack

-   **Python 3**
-   **Tkinter** for the native GUI
-   **SQLite** for local, persistent data storage
-   **Matplotlib** for embedding data visualizations
-   **PyInstaller** (for bundling into an `.exe`)

---

## ⚙️ How to Run


### Run the Executable (Easy)

1.  Go to the [**Releases**](https://github.com/Viishnu07/fuel-tracker) page of this repository.
2.  Download the latest `.zip` file.
3.  Unzip the folder.
4.  **Important:** Keep the `.exe` file and the `fuel.db` file in the **same directory**.
5.  Double-click the `.exe` file to run the application.



## 🔒 Cybersecurity Disclaimer

As a final-year cybersecurity student, I want to note that this was a personal "vibecoding" project.

This app prioritizes rapid development and functionality over security. It **does not** fully follow secure software development best practices (e.g., no password hashing, minimal input validation, plain-text password in code).

⚠️ **Please use this for personal, non-sensitive data only.** It is intended for educational and local use, not for production.

---

## 🚀 Future Improvements

-   [ ] Implement proper password hashing (`bcrypt`) for the admin panel.
-   [ ] Add support for tracking multiple vehicles.
-   [ ] Include expense tracking for maintenance, tolls, and insurance.
-   [ ] Add a data export-to-CSV feature.
