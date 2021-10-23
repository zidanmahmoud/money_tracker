import pytest
import pandas as pd
from utils import MT
from pandas.testing import assert_frame_equal

@pytest.fixture
def example_database():
    tracker = MT("example_test.db")
    tracker.initialize_empty_database()
    tracker.add_user(1, "test", "1234")
    tracker.add_user(2, "test2", "1234")
    tracker.add_transaction_by_userid(1, 50, "2020.12.31", "TEST")
    tracker.add_transaction_by_username("test", 50, "2020.12.31", "TEST")
    tracker.add_transaction_by_userid(2, 50, "2020.12.31", "TEST")
    tracker.add_transaction_by_username("test2", 50, "2020.12.31", "TEST")
    return (
        tracker.get_users_df(),
        tracker.get_transactions_df()
    )

def test_example(example_database):
    users_df = example_database[0]
    transactions_df = example_database[1]

    data = [
        [1, "test", "1234"],
        [2, "test2", "1234"],
    ]
    columns = ["user_id", "username", "password"]
    users_expected = pd.DataFrame(data, columns=columns)
    users_expected.set_index("user_id", inplace=True)

    data = [
        [1, 1, 50.0, "2020.12.31", "TEST"],
        [2, 1, 50.0, "2020.12.31", "TEST"],
        [3, 2, 50.0, "2020.12.31", "TEST"],
        [4, 2, 50.0, "2020.12.31", "TEST"],
    ]
    columns = ["rowid", "user_id", "amount", "date", "category"]
    transactions_expected = pd.DataFrame(data, columns=columns)
    transactions_expected.set_index("rowid", inplace=True)

    assert_frame_equal(users_expected, users_df)
    assert_frame_equal(transactions_expected, transactions_df)

