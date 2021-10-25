import pytest
import pandas as pd
from datetime import date, datetime
from utils import MT
from pandas.testing import assert_frame_equal

# TODO: reduce duplications

@pytest.fixture(scope="module")
def tracker():
    tracker = MT()
    tracker.open_db("example_test.db")
    if tracker.is_empty():
        tracker.initialize_database()
        tracker.add_user(1, "test")
        tracker.add_user(2, "test2")
        tracker.add_income(
            "test", 50, date(2020, 12, 31), "TEST"
        )
        tracker.add_expense(
            "test", 50, date(2020, 12, 31), "TEST"
        )
        tracker.add_income(
            "test2", 50, date(2020, 12, 31), "TEST"
        )
        tracker.add_expense(
            "test2", 50, date(2020, 12, 31), "TEST"
        )
    yield tracker
    tracker.close()

def default_users_data():
    data = [
        [1, "test"],
        [2, "test2"],
    ]
    columns = ["user_id", "username"]
    return (data, columns)

def default_trans_data():
    data = [
        [1, 1, 50.0, datetime(2020, 12, 31), "TEST"],
        [2, 1,-50.0, datetime(2020, 12, 31), "TEST"],
        [3, 2, 50.0, datetime(2020, 12, 31), "TEST"],
        [4, 2,-50.0, datetime(2020, 12, 31), "TEST"],
    ]
    columns = ["rowid", "user_id", "amount", "date", "category"]
    return (data, columns)

def test_users(tracker):
    users_df = tracker.get_users_df()
    data, columns = default_users_data()
    users_expected = pd.DataFrame(data, columns=columns)
    users_expected.set_index("user_id", inplace=True)
    assert_frame_equal(users_expected, users_df)

def test_transactions(tracker):
    transactions_df = tracker.get_transactions_df()
    data, columns = default_trans_data()
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_users_custom_query(tracker):
    users_df = tracker.get_users_df_custom("""
        SELECT * FROM users
        WHERE user_id = 1
    """)
    data, columns = default_users_data()
    users_expected = pd.DataFrame(data[:-1], columns=columns)
    users_expected.set_index("user_id", inplace=True)
    assert_frame_equal(users_expected, users_df)

def test_transactions_custom_query(tracker):
    transactions_df = tracker.get_transactions_df_custom("""
        SELECT rowid, * FROM transactions
        WHERE user_id = 1
    """)
    data, columns = default_trans_data()
    transactions_expected = pd.DataFrame(data[:2], columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_add_user(tracker):
    tracker.add_user(3, "hi")
    users_df = tracker.get_users_df()
    tracker.remove_user("hi")
    data, columns = default_users_data()
    data.append([3, "hi"])
    users_expected = pd.DataFrame(data, columns=columns)
    users_expected.set_index("user_id", inplace=True)
    assert_frame_equal(users_expected, users_df)

def test_add_expense(tracker):
    tracker.add_expense(
        "test", 70, "2021.10.10", "hi"
    )
    transactions_df = tracker.get_transactions_df()
    tracker.remove_transaction_by_rowid(5)
    data, columns = default_trans_data()
    data.append([5, 1, -70.0, datetime(2021, 10, 10), "hi"])
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)
