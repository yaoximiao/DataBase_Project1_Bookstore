from pymongo.errors import PyMongoError
from be.model import error
from be.model import db_conn
import json

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            
            stores = self.get_collection("stores")
            result = stores.insert_one({
                'store_id': store_id,
                'book_id': book_id,
                'book_info': json.loads(book_json_str),
                'stock_level': stock_level
            })
            if not result.acknowledged:
                return 528, "Failed to insert book"
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                print("i pass here!!!")
                return error.error_non_exist_book_id(book_id)

            store_collection = self.db.get_collection('stores')
            result = store_collection.update_one(
                {'store_id': store_id, 'book_id': book_id},
                {'$inc': {'stock_level': add_stock_level}}
            )
            if result.matched_count == 0:
                return 527, "Book not found in store"
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            # print("user_id in create_store", user_id)
            # print(self.user_id_exist(user_id))
            if not self.user_id_exist(user_id):
                # print("i pass here!!!")
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            
            user_store = self.get_collection('user_store')
            result = user_store.insert_one({
                'store_id': store_id,
                'user_id': user_id
            })
            if not result.acknowledged:
                return 528, "Failed to create store"
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        return 200, "ok"

    def user_id_exist(self, user_id: str) -> bool:
        users = self.get_collection('users')
        return users.count_documents({'user_id': user_id}) > 0

    def store_id_exist(self, store_id: str) -> bool:
        user_store = self.get_collection('user_store')
        return user_store.count_documents({'store_id': store_id}) > 0

    def book_id_exist(self, store_id: str, book_id: str) -> bool:
        stores = self.get_collection('stores')
        return stores.count_documents({'store_id': store_id, 'book_id': book_id}) > 0