# from datetime import datetime, timedelta
# from be.model.store import get_db
# from be.model import db_conn
# from be.model import error
# from pymongo.errors import PyMongoError
# import uuid

# class Order(db_conn.DBConn):
#     def __init__(self):
#         db_conn.DBConn.__init__(self)

#     def create_order(self, user_id, store_id, book_id, quantity):
#         """创建新订单"""
        

#     def get_order_status(self, order_id):
#         """获取订单状态"""
#         order = self.db.orders.find_one({'_id': order_id})
#         if order:
#             return order['status']
#         else:
#             return None

#     def cancel_order(self, order_id):
#         """取消订单"""
#         order = self.db.orders.find_one({'_id': order_id})
#         if order:
#             if order['status'] == 'pending':
#                 self.db.orders.update_one({'_id': order_id}, {'$set': {
#                     'status': 'canceled',
#                     'canceled_at': datetime.now()
#                 }})
#                 return True
#             else:
#                 return False
#         else:
#             return False

#     def auto_cancel_orders(self):
#         """自动取消超时未支付的订单"""
#         timeout = datetime.now() - timedelta(minutes=30)
#         self.db.orders.update_many({
#             'status': 'pending',
#             'created_at': {'$lt': timeout}
#         }, {'$set': {
#             'status': 'canceled',
#             'canceled_at': datetime.now()
#         }})

#     def get_buyer_orders(self, buyer_id):
#         """获取买家的历史订单"""
#         orders = list(self.db.orders.find({'buyer_id': buyer_id}))
#         return orders