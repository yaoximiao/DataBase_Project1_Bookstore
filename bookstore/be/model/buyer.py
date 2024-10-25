import uuid
import json
import logging
from pymongo.errors import PyMongoError
from be.model import db_conn
from be.model import error

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            uid = f"{user_id}_{store_id}_{str(uuid.uuid1())}"
            
            # store_collection = self.db.store
            # order_detail_collection = self.db.new_order_detail
            # order_collection = self.db.new_order
            # 获取相关集合
            stores = self.get_collection("stores")
            order_details = self.get_collection("order_details")
            orders = self.get_collection("orders")

            for book_id, count in id_and_count:
                # book = store_collection.find_one({"store_id": store_id, "book_id": book_id})
                # if book is None:
                #     return error.error_non_exist_book_id(book_id) + (order_id,)
                 # 查找书籍
                # print("pass 查找书籍")
                book = stores.find_one({"store_id": store_id, "book_id": book_id})
                if book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book['stock_level']
                book_info = json.loads(book['book_info'])
                price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # result = store_collection.update_one(
                #     {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                #     {"$inc": {"stock_level": -count}}
                # )
                # if result.modified_count == 0:
                #     return error.error_stock_level_low(book_id) + (order_id,)
                 # 更新库存
                result = stores.update_one(
                    {
                        "store_id": store_id, 
                        "book_id": book_id, 
                        "stock_level": {"$gte": count}
                    },
                    {"$inc": {"stock_level": -count}}
                )
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                order_details.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })

            orders.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id
            })
            
            order_id = uid
        except PyMongoError as e:
            logging.info(f"528, {str(e)}")
            return 528, f"{str(e)}", ""
        except BaseException as e:
            logging.info(f"530, {str(e)}")
            return 530, f"{str(e)}", ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # order_collection = self.db.new_order
            # user_collection = self.db.user
            # user_store_collection = self.db.user_store
            # order_detail_collection = self.db.new_order_detail
            # 获取相关集合
            orders = self.get_collection("orders")
            users = self.get_collection("users")
            user_store = self.get_collection("user_store")
            order_details = self.get_collection("order_details")

            order = orders.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = order['user_id']
            store_id = order['store_id']
            print("buyer_id = ", buyer_id)
            print("store_id = ", store_id)
            if buyer_id != user_id:
                return error.error_authorization_fail()

            buyer = users.find_one({"user_id": buyer_id})
            if buyer is None:
                return error.error_non_exist_user_id(buyer_id)
            
            balance = buyer['balance']
            if password != buyer['password']:
                return error.error_authorization_fail()

            store = user_store.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = store['user_id']

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            required_order_details = order_details.find({"order_id": order_id})
            total_price = sum(detail['count'] * detail['price'] for detail in required_order_details)
            print("total_price is ", total_price)
            print("balance is ", balance)
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            result = users.update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            result = users.update_one(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_user_id(seller_id)

            orders.delete_one({"order_id": order_id})
            order_details.delete_many({"order_id": order_id})

        except PyMongoError as e:
            return 528, f"{str(e)}"
        except BaseException as e:
            print("i pass here!!!")
            return 530, f"{str(e)}"

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # user_collection = self.db.user
            users = self.get_collection("users")
            user = users.find_one({"user_id": user_id})
            
            if user is None or user['password'] != password:
                return error.error_authorization_fail()

            result = users.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
            # if result.modified_count == 0:
            #     print("I pass here!!")
            #     return error.error_non_exist_user_id(user_id)

        except PyMongoError as e:
            return 528, f"{str(e)}"
        except BaseException as e:
            return 530, f"{str(e)}"

        return 200, "ok"

    def user_id_exist(self, user_id: str) -> bool:
        # return self.db.user.count_documents({"user_id": user_id}) > 0
        users = self.get_collection("users")
        return users.count_documents({"user_id": user_id}) > 0

    def store_id_exist(self, store_id: str) -> bool:
        # return self.db.user_store.count_documents({"store_id": store_id}) > 0
        user_store = self.get_collection("user_store")
        return user_store.count_documents({"store_id": store_id}) > 0