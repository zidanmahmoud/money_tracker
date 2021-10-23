import sqlite3
import warnings
import pandas as pd


class MT:
    def __init__(self, path):
        """
        MT (Money Tracker) is an I/O class to the database of the app
        money tracker.

        MT uses the builtin python sqlite3 to initialize,
        read, and modify a database file with two tables, namely, users
        and transactions. The users table contains the user_id, username,
        and password for each user. The transactions table contains the
        user_id, amount, date, and category of each transaction.
        """
        self._db = sqlite3.connect(path)
        self._cu = self._db.cursor()

    def _commit(self):
        self._db.commit()

    def close(self):
        self._db.close()

    def is_empty(self):
        self._cu.execute("SELECT name FROM sqlite_master")
        check = self._cu.fetchall()
        if len(check) == 0:
            return True
        return False

    def initialize_empty_database(self):
        create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        """
        create_transactions_table = """
            CREATE TABLE IF NOT EXISTS transactions (
                user_id  INTEGER,
                amount   REAL,
                date     TEXT,
                category TEXT
            )
        """
        self._cu.execute(create_users_table)
        self._cu.execute(create_transactions_table)
        self._commit()

    def get_userid_from_username(self, username):
        usernames = self._get_available_usernames()
        if username not in usernames:
            raise ValueError(
                f"Transaction cannot be added! No username: {username}"
            )
        get_id_qr = f"""
            SELECT user_id, username FROM users WHERE username='{username}'
        """
        return pd.read_sql_query(get_id_qr, self._db).iloc[0, 0]

    def get_users_df(self):
        return pd.read_sql_query(
            "SELECT * FROM users", self._db, index_col="user_id"
        )

    def get_users_df_custom(self, custom_query):
        return pd.read_sql_query(custom_query, self._db, index_col="user_id")

    def get_transactions_df(self):
        return pd.read_sql_query(
            "SELECT rowid, * FROM transactions", self._db, index_col="rowid"
        )

    def get_transactions_df_custom(self, custom_query):
        return pd.read_sql_query(custom_query, self._db, index_col="rowid")

    def _get_available_ids(self):
        return pd.read_sql_query(
            "SELECT user_id FROM users", self._db
        ).values.flatten()

    def _get_available_usernames(self):
        return pd.read_sql_query(
            "SELECT username FROM users", self._db
        ).values.flatten()

    def add_user(self, user_id, username, passwd):
        ids = self._get_available_ids()
        usernames = self._get_available_usernames()
        if user_id in ids:
            raise ValueError(f"""
                {user_id} already exists in the database!
                Please select another user_id
            """)
        if username in usernames:
            raise ValueError(f"""
                {username} already exists in the database!
                Please select another username
            """)
        add_usr_qr = f"""
            INSERT INTO users VALUES({user_id}, '{username}', '{passwd}')
        """
        self._cu.execute(add_usr_qr)
        self._commit()

    def add_transaction_by_userid(self, user_id, amount, date, category):
        ids = self._get_available_ids()
        if user_id not in ids:
            raise ValueError(
                f"Transaction cannot be added! No user id: {user_id}"
            )
        add_trns_qr = f"""
            INSERT INTO transactions VALUES(
                {user_id}, {amount}, '{date}', '{category}'
            )
        """
        self._cu.execute(add_trns_qr)
        self._commit()

    def add_transaction_by_username(self, username, amount, date, category):
        usernames = self._get_available_usernames()
        if username not in usernames:
            raise ValueError(
                f"Transaction cannot be added! No username: {username}"
            )
        get_id_qr = f"""
            SELECT user_id, username FROM users WHERE username='{username}'
        """
        user_id = pd.read_sql_query(get_id_qr, self._db).iloc[0, 0]
        add_trns_qr = f"""
            INSERT INTO transactions VALUES(
                {user_id}, {amount}, '{date}', '{category}'
            )
        """
        self._cu.execute(add_trns_qr)
        self._commit()

    def remove_transaction_by_rowid(self, row_id):
        self._cu.execute(f"DELETE FROM transactions WHERE rowid={row_id}")
        self._commit()

    def remove_user_by_userid(self, user_id):
        if user_id not in self._get_available_ids():
            warnings.warn(
                f"user_id {user_id} not found ... did not remove any users"
            )
        self._cu.execute(f"DELETE FROM users WHERE user_id={user_id}")
        self._cu.execute(f"DELETE FROM transactions WHERE user_id={user_id}")
        self._commit()
