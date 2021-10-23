from utils import MT

if __name__ == "__main__":

    instance = MT("DATA.db")
    instance.initialize_empty_database()
    # instance.add_user(1, "test", "1234")
    # instance.add_user(2, "test2", "1234")
    # instance.add_transaction_by_userid(1, 50, "2020.12.31", "TEST")
    # instance.add_transaction_by_username("test", 50, "2020.12.31", "TEST")
    # instance.add_transaction_by_userid(2, 50, "2020.12.31", "TEST")
    # instance.add_transaction_by_username("test2", 50, "2020.12.31", "TEST")

    print(instance.get_users_df())
    print("---------------------------\n")
    print(instance.get_transactions_df())

    only_rent_qr = """
        SELECT rowid, * FROM transactions
        WHERE category="TEST"
    """
    print("---------------------------\n")
    print(instance.get_transactions_df_custom(only_rent_qr))

    username = "test"
    user_id = instance.get_userid_from_username(f"{username}")
    print(
        instance.get_transactions_df_custom(f"""
            SELECT rowid, * FROM transactions
            WHERE user_id={user_id}
        """)
    )

    instance.close()
