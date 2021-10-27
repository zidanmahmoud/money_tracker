import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date
from scipy.interpolate import interp1d
from utils import MT

def get_db(path):
    db = MT()
    db.open_db(path)
    if db.is_empty():
        db.initialize_database()

        db.add_user(1, "sameer")

        db.add_income("sameer", 2400, date(2021, 9, 1), "Salary")
        db.add_expense("sameer", 1000, date(2021, 9, 5), "Rent")
        db.add_expense("sameer", 50, date(2021, 9, 5), "Insurance")
        db.add_expense("sameer", 15, date(2021, 9, 8), "Gym")
        db.add_expense("sameer", 60, date(2021, 9, 14), "Entertainment")
        db.add_expense("sameer", 20, date(2021, 9, 27), "Groceries")

        db.add_expense("sameer", 1000, date(2021, 10, 5), "Rent")
        db.add_expense("sameer", 50, date(2021, 10, 5), "Insurance")
        db.add_expense("sameer", 20, date(2021, 10, 5), "Groceries")
        db.add_expense("sameer", 15, date(2021, 10, 8), "Gym")
        db.add_expense("sameer", 20, date(2021, 10, 14), "Groceries")
        db.add_expense("sameer", 60, date(2021, 10, 14), "Entertainment")
        db.add_expense("sameer", 20, date(2021, 10, 27), "Groceries")
        db.add_expense("sameer", 500, date(2021, 10, 15), "Car")

        db.add_income("sameer", 2400, date(2021, 11, 1), "Salary")
        db.add_expense("sameer", 1000, date(2021, 11, 5), "Rent")
        db.add_expense("sameer", 50, date(2021, 11, 5), "Insurance")
        db.add_expense("sameer", 60, date(2021, 11, 7), "Groceries")
        db.add_expense("sameer", 15, date(2021, 11, 8), "Gym")
        db.add_expense("sameer", 100, date(2021, 11, 14), "Travel")
        db.add_expense("sameer", 20, date(2021, 11, 27), "Groceries")

        db.add_income("sameer", 2400, date(2021, 12, 1), "Salary")
        db.add_expense("sameer", 1000, date(2021, 12, 5), "Rent")
        db.add_expense("sameer", 200, date(2021, 12, 5), "Insurance")
        db.add_expense("sameer", 100, date(2021, 12, 7), "Groceries")
        db.add_expense("sameer", 15, date(2021, 12, 8), "Gym")
        db.add_expense("sameer", 400, date(2021, 12, 15), "Car")
        db.add_expense("sameer", 70, date(2021, 12, 27), "Groceries")

    return db

def plot_expenses_by_category(db, piechart=True, barchart=False):
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
    if piechart and not barchart:
        fig = plt.figure("Expenses By Category - Pie Chart")
        ax = fig.subplots(1, 1)
        df.plot(kind="pie", subplots=True, ax=ax)
    elif not piechart and barchart:
        fig = plt.figure("Expenses By Category - Bar Chart")
        ax = fig.subplots(1, 1)
        df.plot(kind="barh", ax=ax)
        ax.set_xlabel("Amount")
        ax.invert_yaxis()
        ax.get_legend().remove()
        ax.set_axisbelow(True)
        ax.grid(True)
    else:
        raise RuntimeError
    fig.tight_layout()
    return fig, ax

def plot_monthly_moneyflow(db, year):
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
    return fig, ax

def plot_nerworth(db, year):
    networth_qr = """
        WITH monthly AS
        (
            SELECT strftime("%m", date) AS Month,
            SUM(amount) AS flow
            FROM transactions
            GROUP BY Month
        )
        SELECT
            t1.Month,
            (SELECT SUM(t2.flow) FROM monthly AS t2 WHERE t2.Month <= t1.Month) AS Flow
        FROM monthly AS t1
        ORDER BY t1.Month
    """
    df = db.get_transactions_df_custom(
        networth_qr
    ).set_index("Month")

    fig = plt.figure("Yearly Networth")
    ax = fig.subplots(1, 1)

    x_axis = np.array(df.index.array, dtype=int)
    y_val = np.array(df.Flow)
    ax.plot(x_axis, y_val, "o", color="#1f77b4")

    quad_interp = interp1d(x_axis, y_val, kind="quadratic")
    xnew = np.linspace(x_axis[0], x_axis[-1], 200)
    ynew = quad_interp(xnew)

    pos = ynew.copy()
    neg = ynew.copy()
    pos[pos < 0] = np.nan
    neg[neg > 0] = np.nan

    ax.plot(xnew, pos, "--", color="#2ca02c")
    ax.plot(xnew, neg, "--", color="#ff7f0e")
    ax.fill_between(xnew, pos, color="#2ca02c", alpha=0.5)
    ax.fill_between(xnew, neg, color="#ff7f0e", alpha=0.5)

    ax.set_xticks(x_axis)
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Worth")
    ax.grid(True)
    fig.tight_layout()


if __name__ == "__main__":
    db = get_db("DATA.db")
    print(db.get_transactions_df())
    plot_expenses_by_category(db)
    year = 2021
    plot_monthly_moneyflow(db, year)
    plot_nerworth(db, year)
    plt.show()

