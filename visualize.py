import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
from utils import MT

if __name__ == "__main__":
    db = MT()
    db.open_db("DATA.db")
    if db.is_empty():
        db.initialize_database()
        db.add_user(1, "sameer")
        # db.add_income("sameer", 2400, date(2021, 10, 1), "Salary")
        db.add_expense("sameer", 1000, date(2021, 10, 5), "Rent")
        db.add_expense("sameer", 50, date(2021, 10, 5), "Insurance")
        db.add_expense("sameer", 20, date(2021, 10, 5), "Groceries")
        db.add_expense("sameer", 15, date(2021, 10, 8), "Gym")
        db.add_expense("sameer", 20, date(2021, 10, 14), "Groceries")
        db.add_expense("sameer", 60, date(2021, 10, 14), "Entertainment")
        db.add_expense("sameer", 20, date(2021, 10, 27), "Groceries")

        db.add_income("sameer", 2400, date(2021, 11, 1), "Salary")
        db.add_expense("sameer", 1000, date(2021, 11, 5), "Rent")
        db.add_expense("sameer", 50, date(2021, 11, 5), "Insurance")
        db.add_expense("sameer", 60, date(2021, 11, 7), "Groceries")
        db.add_expense("sameer", 15, date(2021, 11, 8), "Gym")
        db.add_expense("sameer", 100, date(2021, 11, 14), "Travel")
        db.add_expense("sameer", 20, date(2021, 11, 27), "Groceries")
    print(db.get_transactions_df())

    expenses_by_category_qr = """
        SELECT
            category AS Category,
            sum(-amount) AS Amount
            FROM transactions
        WHERE amount < 0
        GROUP BY category
        ORDER BY amount DESC
    """
    df = db.get_transactions_df_custom(expenses_by_category_qr).set_index("Category")
    fig = plt.figure("Expenses By Category - Bar Chart")
    ax = fig.subplots(1, 1)
    df.plot(kind="barh", ax=ax)
    ax.set_xlabel("Amount")
    ax.invert_yaxis()
    ax.get_legend().remove()
    ax.set_axisbelow(True)
    ax.grid(True)
    fig.tight_layout()
    fig = plt.figure("Expenses By Category - Pie Chart")

    ax = fig.subplots(1, 1)
    df.plot(kind="pie", subplots=True, ax=ax)
    fig.tight_layout()

    # sqlite does not support full join yet,
    # so it is emulated by left join and union
    # https://stackoverflow.com/questions/1923259/full-outer-join-with-sqlite
    year = 2021
    moneyflow_qr = f"""
        WITH INCOME AS
        (
            SELECT
                strftime("%m", date) AS Month,
                sum(amount) AS Income
                FROM transactions
                WHERE amount > 0 AND strftime("%Y", date)="{year}"
            GROUP BY Month
        ),
        EXPENSES AS
        (
            SELECT
                strftime("%m", date) AS Month,
                sum(-amount) AS Expenses
                FROM transactions
                WHERE amount < 0 AND strftime("%Y", date)="{year}"
            GROUP BY Month
        )
        SELECT i.Month, i.Income, e.Expenses
            FROM INCOME i
                LEFT JOIN EXPENSES e
                ON i.Month = e.Month
        UNION ALL
        SELECT e.Month, i.Income, e.Expenses
            FROM EXPENSES e
                LEFT JOIN INCOME i
                ON i.Month = e.Month
        WHERE i.Month IS NULL
        ORDER BY i.Month
    """
    df = db.get_transactions_df_custom(
        moneyflow_qr
    ).set_index("Month")
    fig = plt.figure("Moneyflow Per Month")
    ax = fig.subplots(1, 1)
    df.plot(kind="bar", ax=ax)
    ax.set_ylabel("Amount")
    ax.set_axisbelow(True)
    ax.grid(True)
    fig.tight_layout()

    # TODO: Calculate net worth and plot it

    plt.show()

