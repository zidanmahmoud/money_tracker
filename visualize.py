import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date
from scipy.interpolate import interp1d
from utils import MT

# # Dark mode but default color cycle (dark mode color cycle is terrible)
# default_colors = plt.rcParams['axes.prop_cycle']
# plt.style.use("dark_background")
# plt.rcParams['axes.prop_cycle'] = default_colors

def get_db(path):
    db = MT()
    db.open_db(path)
    if db.is_empty():
        db.initialize_database()

        db.add_income(date(2021, 9, 1), 2400, "Salary")
        db.add_expense(date(2021, 9, 5), 1000, "Rent")
        db.add_expense(date(2021, 9, 5), 50, "Insurance")
        db.add_expense(date(2021, 9, 8), 15, "Gym")
        db.add_expense(date(2021, 9, 14), 60, "Entertainment")
        db.add_expense(date(2021, 9, 27), 20, "Groceries")

        db.add_expense(date(2021, 10, 5), 1000, "Rent")
        db.add_expense(date(2021, 10, 5), 50, "Insurance")
        db.add_expense(date(2021, 10, 5), 20, "Groceries")
        db.add_expense(date(2021, 10, 8), 15, "Gym")
        db.add_expense(date(2021, 10, 14), 20, "Groceries")
        db.add_expense(date(2021, 10, 14), 60, "Entertainment")
        db.add_expense(date(2021, 10, 27), 20, "Groceries")
        db.add_expense(date(2021, 10, 15), 500, "Car")

        db.add_income(date(2021, 11, 1), 2400, "Salary")
        db.add_expense(date(2021, 11, 5), 1000, "Rent")
        db.add_expense(date(2021, 11, 5), 50, "Insurance")
        db.add_expense(date(2021, 11, 7), 60, "Groceries")
        db.add_expense(date(2021, 11, 8), 15, "Gym")
        db.add_expense(date(2021, 11, 14), 100, "Travel")
        db.add_expense(date(2021, 11, 27), 20, "Groceries")

        db.add_income(date(2021, 12, 1), 2400, "Salary")
        db.add_expense(date(2021, 12, 5), 1000, "Rent")
        db.add_expense(date(2021, 12, 5), 200, "Insurance")
        db.add_expense(date(2021, 12, 7), 100, "Groceries")
        db.add_expense(date(2021, 12, 8), 15, "Gym")
        db.add_expense(date(2021, 12, 15), 400, "Car")
        db.add_expense(date(2021, 12, 27), 70, "Groceries")

    return db

def plot_expenses_by_category(ax, db, piechart=True):
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
    ax.set_title("Expenses By Category")
    if piechart is True:
        df.plot(kind="pie", subplots=True, ax=ax)
    else:
        df.plot(kind="barh", ax=ax)
        ax.set_xlabel("Amount")
        ax.invert_yaxis()
        ax.get_legend().remove()
        ax.set_axisbelow(True)
        ax.grid(True)
    return fig, ax

def plot_monthly_moneyflow(ax, db, year):
    # sqlite does not support full join yet,
    # so it is emulated by left join and union
    # https://stackoverflow.com/questions/1923259/full-outer-join-with-sqlite
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
    df.plot(kind="bar", ax=ax)
    ax.set_title("Moneyflow Per Month")
    ax.set_ylabel("Amount")
    ax.set_axisbelow(True)
    ax.grid(True)
    # fig.tight_layout()
    return fig, ax

def plot_nerworth(ax, db, year):
    networth_qr = f"""
        WITH monthly AS
        (
            SELECT
                strftime("%m", date) AS Month,
                SUM(amount) AS flow
            FROM transactions
            WHERE strftime("%Y", date) = "{year}"
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

    ax.set_title("Yearly Networth")
    ax.set_xticks(x_axis)
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Worth")
    ax.grid(True)


if __name__ == "__main__":
    db = get_db("DATA.db")

    fig = plt.figure("Expenses By Category")
    ax = fig.subplots(1, 1)
    plot_expenses_by_category(ax, db, True)

    year = 2021

    fig = plt.figure("Moneyflow Per Month")
    ax = fig.subplots(1, 1)
    plot_monthly_moneyflow(ax, db, year)

    fig = plt.figure("Yearly Networth")
    ax = fig.subplots(1, 1)
    plot_nerworth(ax, db, year)
    plt.show()

