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
        tracker.add_income(date(2020, 12, 31), 50, "TEST")
        tracker.add_expense(date(2020, 12, 31), 50, "TEST")
        tracker.add_income(date(2020, 12, 31), 50, "TEST")
        tracker.add_expense(date(2020, 12, 31), 50, "TEST")
    yield tracker
    tracker.close()

def default_trans_data():
    data = [
        [1, date(2020, 12, 31), 50.0, "TEST"],
        [2, date(2020, 12, 31),-50.0, "TEST"],
        [3, date(2020, 12, 31), 50.0, "TEST"],
        [4, date(2020, 12, 31),-50.0, "TEST"],
    ]
    columns = ["rowid", "date", "amount", "category"]
    return (data, columns)

def test_transactions(tracker):
    transactions_df = tracker.get_transactions_df()
    data, columns = default_trans_data()
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_transactions_custom_query(tracker):
    transactions_df = tracker.get_transactions_df_custom("""
        SELECT rowid, * FROM transactions
        WHERE rowid <= 2
    """).set_index("rowid")
    data, columns = default_trans_data()
    transactions_expected = pd.DataFrame(data[:2], columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)

def test_add_expense(tracker):
    tracker.add_expense(date(2021, 10, 10), 70, "hi")
    transactions_df = tracker.get_transactions_df()
    tracker.remove_transaction_by_rowid(5)
    data, columns = default_trans_data()
    data.append([5, date(2021, 10, 10), -70.0, "hi"])
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)
    assert_frame_equal(transactions_expected, transactions_df)
