# from be.model import db_conn
# from be.model import error
# import time

# class OrderManager(db_conn.DBConn):
#     def __init__(self):
#         db_conn.DBConn.__init__(self)
#         self.orders = self.get_collection("orders")
#         self.users = self.get_collection("users")
#         self.stores = self.get_collection("stores")
        
#         # 创建复合索引
#         self.orders.create_index([("order_id", 1), ("status", 1)])
#         self.orders.create_index([("user_id", 1), ("status", 1)])
        
#     def ship_order(self, seller_id: str, store_id: str, order_id: str) -> (int, str):
#         try:
#             # 验证订单存在且状态为已支付
#             order = self.orders.find_one({
#                 "order_id": order_id,
#                 "store_id": store_id,
#                 "status": "paid"
#             })
            
#             if order is None:
#                 return error.error_invalid_order_id(order_id)

#             # 验证是否为店铺所有者
#             store = self.stores.find_one({"store_id": store_id, "seller_id": seller_id})
#             if store is None:
#                 return error.error_authorization_fail()
                
#             # 更新订单状态
#             result = self.orders.update_one(
#                 {"order_id": order_id},
#                 {
#                     "$set": {
#                         "status": "shipped",
#                         "ship_time": time.time()
#                     }
#                 }
#             )
            
#             if result.modified_count == 0:
#                 return error.error_invalid_order_id(order_id)
                
#             return 200, "ok"
                
#         except Exception as e:
#             return 530, "Internal error: {}".format(str(e))

#     def auto_cancel_orders(self):
#         """定期检查并自动取消超时订单"""
#         try:
#             current_time = time.time()
#             timeout_threshold = current_time - 1800  # 30分钟超时
            
#             # 查找超时未支付订单
#             timeout_orders = self.orders.find({
#                 "status": "pending",
#                 "create_time": {"$lt": timeout_threshold}
#             })
            
#             for order in timeout_orders:
#                 self.cancel_order(order["user_id"], order["order_id"], "auto_cancel")
                
#         except Exception as e:
#             print(f"Auto cancel error: {str(e)}")

#     def cancel_order(self, user_id: str, order_id: str, reason: str) -> (int, str):
#         try:
#             order = self.orders.find_one({
#                 "order_id": order_id,
#                 "user_id": user_id
#             })

#             if order is None:
#                 return error.error_invalid_order_id(order_id)

#             # 更新订单状态为已取消
#             result = self.orders.update_one(
#                 {"order_id": order_id},
#                 {
#                     "$set": {
#                         "status": "canceled",
#                         "cancel_time": time.time(),
#                         "cancel_reason": reason
#                     }
#                 }
#             )

#             if result.modified_count == 0:
#                 return error.error_invalid_order_id(order_id)

#             return 200, "Order canceled successfully"

#         except Exception as e:
#             return 530, "Internal error: {}".format(str(e))
        
#     def get_order(self, user_id: str, order_id: str) -> (int, dict):
#         try:
#             order = self.orders.find_one({
#                 "order_id": order_id,
#                 "user_id": user_id
#             })

#             if order is None:
#                 return error.error_invalid_order_id(order_id)

#             return 200, order

#         except Exception as e:
#             return 530, "Internal error: {}".format(str(e))
        
#     def get_user_orders(self, user_id: str, status: str = None) -> (int, list):
#         try:
#             query = {"user_id": user_id}
#             if status:
#                 query["status"] = status

#             orders = list(self.orders.find(query))

#             return 200, orders

#         except Exception as e:
#             return 530, "Internal error: {}".format(str(e))