from money_tracker import MT

if __name__ == "__main__":

    instance = MT("DATA.db")
    instance.initialize_empty_database()

    print(instance.get_users_df())
    print("---------------------------\n")
    print(instance.get_transactions_df())

    only_rent_qr = """
        SELECT rowid, * FROM transactions
        WHERE category="Rent"
    """
    print("---------------------------\n")
    print(instance.get_transactions_df_custom(only_rent_qr))

    username = "travolta"
    user_id = instance.get_userid_from_username(f"{username}")
    print(
        instance.get_transactions_df_custom(f"""
            SELECT rowid, * FROM transactions
            WHERE user_id={user_id}
        """)
    )

    instance.close()
