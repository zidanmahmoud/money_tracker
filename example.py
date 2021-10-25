from datetime import date
from utils import MT

if __name__ == "__main__":
    tracker = MT()
    tracker.open_db("example_data.db")
    if tracker.is_empty():
        tracker.initialize_database()
        tracker.add_user(1, "test", "1234")
        tracker.add_user(2, "test2", "1234")
        tracker.add_transaction_by_userid(1, 50, date(2020, 12, 31), "TEST")
        tracker.add_transaction_by_username("test", 50, date(2020, 12, 31), "TEST")
        tracker.add_transaction_by_userid(2, 50, date(2020, 12, 31), "TEST")
        tracker.add_transaction_by_username("test2", 50, date(2020, 12, 31), "TEST")
    print(tracker.get_users_df())
    print(tracker.get_transactions_df())
