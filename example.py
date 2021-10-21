from money_tracker import MT

if __name__ == "__main__":
    tracker = MT("example_data.db")
    tracker.initialize_empty_database()
    tracker.add_user(1, "test", "1234")
    tracker.add_user(2, "test2", "1234")
    tracker.add_transaction_by_userid(1, 50, "2020.12.31", "TEST")
    tracker.add_transaction_by_username("test", 50, "2020.12.31", "TEST")
    tracker.add_transaction_by_userid(2, 50, "2020.12.31", "TEST")
    tracker.add_transaction_by_username("test2", 50, "2020.12.31", "TEST")
    print(tracker.get_users_df())
    print(tracker.get_transactions_df())
