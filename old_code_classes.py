# class Transaction:

#     def __init__(self, id_, amount=None, date=None, category=None):
#         if not isinstance(id_, int):
#             raise TypeError("id_ must be of type: int")
#         self._id = id_

#         self._amount = amount
#         self._date = date
#         self._category = category
#         # self._subcategory = None

#     def get_id(self):
#         return self._id

#     @property
#     def amount(self):
#         return self._amount
#     @amount.setter
#     def amount(self, value):
#         self._amount = value

#     @property
#     def date(self):
#         return self._date
#     @date.setter
#     def date(self, value):
#         self._date = value

#     @property
#     def category(self):
#         return self._category
#     @category.setter
#     def category(self, value):
#         self._category = value

    # @property
    # def subcategory(self):
    #     return self._subcategory
    # @subcategory.setter
    # def subcategory(self, value):
    #     self._subcategory = value



# class User:
#     def __init__(self, id_):
#         if not isinstance(id_, int):
#             raise TypeError("id_ must be of type: int")
#         self._id = id_
#         self._transactions = list()

#     def get_transactions(self):
#         return self._transactions

#     def add_new_transaction(self, new_id, amount, date, category):
#         for t in self._transactions:
#             if t.get_id() == new_id:
#                 raise RuntimeError(f"User {self._id} already has a transaction with ID={new_id}")
#         self._transactions.append(Transaction(new_id, amount, date, category))

#     def save(self):
#         # data = {"id": self._id}
#         transactions_data = list()
#         for t in self._transactions:
#             transactions_data.append({
#                 "t_id": t.get_id(),
#                 "amount": t.amount,
#                 "date": t.date,
#                 "category": t.category
#             })
#         data = {
#             "id": self._id,
#             "transaction": transactions_data
#         }
#         with open(f"user_{self._id}.json", "w") as file_buffer:
#             json.dump(data, file_buffer, default=str, indent=4)