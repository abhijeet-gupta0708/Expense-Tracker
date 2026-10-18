from pathlib import Path
import csv
import sqlite3
from datetime import date

ROOT = Path.cwd()
DB = ROOT / "expenses.db"
CSV = ROOT / "data" / "sample_expenses.csv"


def connect():
    connection = sqlite3.connect(DB)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0)
        )
    """)
    connection.commit()
    return connection


def seed(connection):
    if connection.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 0 and CSV.exists():
        with CSV.open(newline="", encoding="utf-8") as file:
            rows = [(r["date"], r["category"], r["description"], float(r["amount"]))
                    for r in csv.DictReader(file)]
        connection.executemany(
            "INSERT INTO expenses(date, category, description, amount) VALUES (?, ?, ?, ?)", rows
        )
        connection.commit()
        print("Imported fictional starter transactions.")


def listing(connection):
    rows = connection.execute(
        "SELECT id, date, category, description, amount FROM expenses ORDER BY date DESC, id DESC"
    ).fetchall()
    if not rows:
        print("No expenses yet.")
        return
    print(f"{'ID':>3} | {'Date':<10} | {'Category':<15} | {'Amount':>9} | Description")
    print("-" * 72)
    for row in rows:
        print(f"{row[0]:>3} | {row[1]} | {row[2]:<15} | {row[4]:>9.2f} | {row[3]}")


def add(connection):
    try:
        expense_date = input("Date YYYY-MM-DD (blank=today): ").strip() or date.today().isoformat()
        date.fromisoformat(expense_date)
        category = input("Category: ").strip()
        description = input("Description: ").strip()
        amount = float(input("Amount: "))
        if not category or not description or amount <= 0:
            raise ValueError("Category/description required and amount must be positive.")
        connection.execute(
            "INSERT INTO expenses(date, category, description, amount) VALUES (?, ?, ?, ?)",
            (expense_date, category, description, amount),
        )
        connection.commit()
        print("Expense added.")
    except ValueError as error:
        print("Invalid input:", error)


def summary(connection, monthly=False):
    if monthly:
        query = "SELECT substr(date, 1, 7), ROUND(SUM(amount), 2) FROM expenses GROUP BY 1 ORDER BY 1"
        title = "Monthly totals"
    else:
        query = "SELECT category, ROUND(SUM(amount), 2) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
        title = "Totals by category"
    print(title)
    rows = connection.execute(query).fetchall()
    if not rows:
        print("No expenses yet.")
        return
    for label, total in rows:
        print(f"{label}: {total:.2f}")


def main():
    connection = connect()
    try:
        seed(connection)
        while True:
            print("\nPERSONAL EXPENSE TRACKER\n1 List expenses\n2 Add expense\n3 Category summary\n4 Monthly summary\n5 Exit")
            choice = input("Choose 1-5: ").strip()
            if choice == "1":
                listing(connection)
            elif choice == "2":
                add(connection)
            elif choice == "3":
                summary(connection)
            elif choice == "4":
                summary(connection, monthly=True)
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("Choose a number from 1 to 5.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
