import sqlite3
import pandas as pd


class MT:
    def __init__(self):
        """
        MT (Money Tracker) is an I/O class to the database of the app
        money tracker.

        MT uses the builtin python sqlite3 to initialize,
        read, and modify a database file with a transactions table
        that contains the date, amount, and category of each transaction.
        """
        self._db = None
        self._cu = None

    #== Public functions

    def open_db(self, path):
        self._db = sqlite3.connect(path)
        self._cu = self._db.cursor()

    def initialize_database(self):
        self._cu.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                date     TEXT,
                amount   REAL,
                category TEXT
            )
        """)
        self._commit()

    def close(self):
        self._db.close()

    def is_empty(self):
        self._cu.execute("SELECT name FROM sqlite_master")
        check = self._cu.fetchall()
        if len(check) == 0:
            return True
        return False

    def get_transactions_df(self):
        df = pd.read_sql_query(
            "SELECT rowid, * FROM transactions",
            self._db, index_col="rowid",
        )
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.date
        return df

    def get_transactions_df_custom(self, custom_query):
        df = pd.read_sql_query(custom_query, self._db)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.date
        return df

    def add_income(self, date, amount, category):
        self._add_transaction(date, amount, category)

    def add_expense(self, date, amount, category):
        self._add_transaction(date, -1*amount, category)

    def remove_transaction_by_rowid(self, row_id):
        self._cu.execute(f"DELETE FROM transactions WHERE rowid={row_id}")
        self._commit()

    #== Private functions

    def _commit(self):
        self._db.commit()

    def _add_transaction(self, date, amount, category):
        add_trns_qr = f"""
            INSERT INTO transactions VALUES(
                '{date}', {amount}, '{category}'
            )
        """
        self._cu.execute(add_trns_qr)
        self._commit()
