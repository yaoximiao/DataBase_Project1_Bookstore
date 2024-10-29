from datetime import datetime, timedelta
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

            stores = self.get_collection("stores")
            order_details = self.get_collection("order_details")
            orders = self.get_collection("orders")

            for book_id, count in id_and_count:
                book = stores.find_one({"store_id": store_id, "book_id": book_id})
                if book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book['stock_level']
                book_info = book['book_info']
                price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

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
                
                create_time = datetime.now()

                order_details.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price,
                    "status": "not pay",
                    "create_time": create_time,
                    "cancel_time": None,  # 初始化为 None
                    "cancel_reason": ""    # 初始化为空字符串
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

    def old_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            uid = f"{user_id}_{store_id}_{str(uuid.uuid1())}"

            stores = self.get_collection("stores")
            order_details = self.get_collection("order_details")
            orders = self.get_collection("orders")

            for book_id, count in id_and_count:
                book = stores.find_one({"store_id": store_id, "book_id": book_id})
                if book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book['stock_level']
                book_info = book['book_info']
                price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

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
                
                 # 设置超时时间为30分钟
                current_time = datetime.now()
                # 模拟 create_time 为当前时间的一个小时以前
                create_time = current_time - timedelta(hours=1)

                order_details.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price,
                    "status": "not pay",
                    "create_time": create_time,
                    "cancel_time": None,  # 初始化为 None
                    "cancel_reason": ""    # 初始化为空字符串
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

            result = order_details.update_one(
                {"order_id":order_id, "status": "not pay"},
                {"$set": {"status": "paid"}}
            )
            # orders.delete_one({"order_id": order_id})
            # order_details.delete_many({"order_id": order_id})

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
    
    def get_order_history(self, user_id: str) -> (int, str, list):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ([],)
            
            print("user_id="+str(user_id))
            orders = self.get_collection("orders")
            order_details = self.get_collection("order_details")
            
            user_orders = list(orders.find({"user_id": user_id}))
            order_history = []
            for order in user_orders:
                order_id = order["order_id"]
                details = list(order_details.find({"order_id": order_id}))
                
                order_info = {
                    "order_id": order_id,
                    "store_id": order["store_id"],
                    "create_time": details[0]["create_time"] if details else None,
                    "status": details[0]["status"] if details else None,
                    "books": [{
                        "book_id": detail["book_id"],
                        "count": detail["count"],
                        "price": detail["price"]
                    } for detail in details],
                    "total_price": sum(detail["count"] * detail["price"] for detail in details)
                }
                order_history.append(order_info)
            return 200, "ok", order_history
        except PyMongoError as e:
            logging.info(f"528, {str(e)}")
            return 528, f"{str(e)}", []
        except BaseException as e:
            logging.info(f"530, {str(e)}")
            return 530, f"{str(e)}", []

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        """取消订单"""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            
            orders = self.get_collection("orders")
            order_details = self.get_collection("order_details")
            stores = self.get_collection("stores")
            print("order_id="+str(order_id))
            print("user_id="+str(user_id))
            # 检查订单是否属于该用户
            order = orders.find_one({"order_id": order_id, "user_id": user_id})
            if not order:
                print("i pass here!!!")
                return error.error_invalid_order_id(order_id)
            
            # 检查订单状态
            details = list(order_details.find({"order_id": order_id}))
            if not details:
                return error.error_invalid_order_id(order_id)
            
            # 只能取消未支付的订单
            if details[0]["status"] != "not pay":
                return error.error_order_cannot_cancel(order_id)
            
            # 恢复库存
            store_id = order["store_id"]
            for detail in details:
                stores.update_one(
                    {"store_id": store_id, "book_id": detail["book_id"]},
                    {"$inc": {"stock_level": detail["count"]}}
                )
                
            # 更新订单状态
            current_time = datetime.now()
            order_details.update_many(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "cancelled",
                        "cancel_time": current_time,
                        "cancel_reason": "user cancelled"
                    }
                }
            )
            
            return 200, "ok"
        except PyMongoError as e:
            logging.info(f"528, {str(e)}")
            return 528, f"{str(e)}"
        except BaseException as e:
            logging.info(f"530, {str(e)}")
            return 530, f"{str(e)}"

    def auto_cancel_timeout_orders(self, order_id) -> (int, str):
        """自动取消超时未支付订单"""
        try:
            orders = self.get_collection("orders")
            order_details = self.get_collection("order_details")
            stores = self.get_collection("stores")
            # 设置超时时间为30分钟
            timeout = datetime.now() - timedelta(minutes=30)
            print("order_id=" + str(order_id))
            # 查找超时未支付的订单
            timeout_details = list(order_details.find({
                "order_id": order_id,
                "status": "not pay",
                "create_time": {"$lt": timeout}
            }))
            # print("*****")
            # print(str(timeout_details))
            # print("*****")
            # 按订单ID分组处理
            processed_orders = set()
            for detail in timeout_details:
                order_id = detail["order_id"]
                if order_id in processed_orders:
                    continue
                    
                processed_orders.add(order_id)
                order = orders.find_one({"order_id": order_id})
                if not order:
                    continue
                    
                # 恢复库存
                store_id = order["store_id"]
                order_details_list = list(order_details.find({"order_id": order_id}))
                for od in order_details_list:
                    stores.update_one(
                        {"store_id": store_id, "book_id": od["book_id"]},
                        {"$inc": {"stock_level": od["count"]}}
                    )
                
                # 更新订单状态
                current_time = datetime.now()
                order_details.update_many(
                    {"order_id": order_id},
                    {
                        "$set": {
                            "status": "cancelled",
                            "cancel_time": current_time,
                            "cancel_reason": "timeout"
                        }
                    }
                )
                
            return 200, "ok"
        except PyMongoError as e:
            logging.info(f"528, {str(e)}")
            return 528, f"{str(e)}"
        except BaseException as e:
            logging.info(f"530, {str(e)}")
            return 530, f"{str(e)}"
    
    def get_order_details(self, order_id) -> (int, dict):
        """获取订单详情"""
        try:
            orders = self.get_collection("orders")
            order_details = self.get_collection("order_details")

            # 查找订单
            order = orders.find_one({"order_id": order_id})
            if not order:
                return 404, {"message": "Order not found"}

            # 查找订单详情
            details = list(order_details.find({"order_id": order_id}))
            if not details:
                return 404, {"message": "Order details not found"}

            # 整理返回的数据
            order_info = {
                "order_id": order["order_id"],
                "store_id": order["store_id"],
                "status": order["status"],
                "create_time": order["create_time"],
                "cancel_reason": order["cancel_reason"]
            }
            print("!!!!!!!")
            print(order_info)
            print("!!!!!!!")
            
            return 200, order_info
        except PyMongoError as e:
            logging.info(f"Error retrieving order details: {str(e)}")
            return 528, {"message": f"{str(e)}"}
        except BaseException as e:
            logging.info(f"Error retrieving order details: {str(e)}")
            return 530, {"message": f"{str(e)}"}
