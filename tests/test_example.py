import pytest
import pandas as pd
from utils import MT
from pandas.testing import assert_frame_equal

@pytest.fixture(scope="module")
def tracker():
    tracker = MT("example_test.db")
    if tracker.is_empty():
        tracker.initialize_empty_database()
        tracker.add_user(1, "test", "1234")
        tracker.add_user(2, "test2", "1234")
        tracker.add_transaction_by_userid(1, 50, "2020.12.31", "TEST")
        tracker.add_transaction_by_username("test", 50, "2020.12.31", "TEST")
        tracker.add_transaction_by_userid(2, 50, "2020.12.31", "TEST")
        tracker.add_transaction_by_username("test2", 50, "2020.12.31", "TEST")
    yield tracker
    tracker.close()

def test_users(tracker):
    users_df = tracker.get_users_df()
    data = [
        [1, "test", "1234"],
        [2, "test2", "1234"],
    ]
    columns = ["user_id", "username", "password"]
    users_expected = pd.DataFrame(data, columns=columns)
    users_expected.set_index("user_id", inplace=True)
    assert_frame_equal(users_expected, users_df)

def test_transactions(tracker):
    transactions_df = tracker.get_transactions_df()
    data = [
        [1, 1, 50.0, "2020.12.31", "TEST"],
        [2, 1, 50.0, "2020.12.31", "TEST"],
        [3, 2, 50.0, "2020.12.31", "TEST"],
        [4, 2, 50.0, "2020.12.31", "TEST"],
    ]
    columns = ["rowid", "user_id", "amount", "date", "category"]
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_users_custom_query(tracker):
    users_df = tracker.get_users_df_custom("""
        SELECT * FROM users
        WHERE user_id = 1
    """)
    data = [
        [1, "test", "1234"],
    ]
    columns = ["user_id", "username", "password"]
    users_expected = pd.DataFrame(data, columns=columns)
    users_expected.set_index("user_id", inplace=True)
    assert_frame_equal(users_expected, users_df)

def test_transactions_custom_query(tracker):
    transactions_df = tracker.get_transactions_df_custom("""
        SELECT rowid, * FROM transactions
        WHERE user_id = 1
    """)
    data = [
        [1, 1, 50.0, "2020.12.31", "TEST"],
        [2, 1, 50.0, "2020.12.31", "TEST"]
    ]
    columns = ["rowid", "user_id", "amount", "date", "category"]
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_userid_from_username(tracker):
    actual = tracker.get_userid_from_username("test")
    expected = 1
    assert actual == expected

def test_add_user(tracker):
    tracker.add_user(3, "hi", "hi")
    users_df = tracker.get_users_df()
    tracker.remove_user_by_userid(3)
    data = [
        [1, "test", "1234"],
        [2, "test2", "1234"],
        [3, "hi", "hi"]
    ]
    columns = ["user_id", "username", "password"]
    users_expected = pd.DataFrame(data, columns=columns)
    users_expected.set_index("user_id", inplace=True)
    assert_frame_equal(users_expected, users_df)

def test_add_transaction_by_userid(tracker):
    tracker.add_transaction_by_userid(
        1, 70, "2021.10.10", "hi"
    )
    transactions_df = tracker.get_transactions_df()
    tracker.remove_transaction_by_rowid(5)
    data = [
        [1, 1, 50.0, "2020.12.31", "TEST"],
        [2, 1, 50.0, "2020.12.31", "TEST"],
        [3, 2, 50.0, "2020.12.31", "TEST"],
        [4, 2, 50.0, "2020.12.31", "TEST"],
        [5, 1, 70.0, "2021.10.10", "hi"],
    ]
    columns = ["rowid", "user_id", "amount", "date", "category"]
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_add_transaction_by_username(tracker):
    tracker.add_transaction_by_username(
        "test", 70, "2021.10.10", "hi"
    )
    transactions_df = tracker.get_transactions_df()
    tracker.remove_transaction_by_rowid(5)
    data = [
        [1, 1, 50.0, "2020.12.31", "TEST"],
        [2, 1, 50.0, "2020.12.31", "TEST"],
        [3, 2, 50.0, "2020.12.31", "TEST"],
        [4, 2, 50.0, "2020.12.31", "TEST"],
        [5, 1, 70.0, "2021.10.10", "hi"],
    ]
    columns = ["rowid", "user_id", "amount", "date", "category"]
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)
