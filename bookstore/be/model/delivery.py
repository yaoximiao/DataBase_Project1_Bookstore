from pymongo.errors import PyMongoError
from be.model import error
from be.model import db_conn

class Delivery(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def deliver_order(self, user_id: str, order_id: str) -> (int, str):
        """
        卖家发货
        :param user_id: 卖家用户ID
        :param order_id: 订单ID
        :return: (code, message)
        """
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            # 获取订单信息
            orders = self.get_collection("orders")
            order_details = self.get_collection("order_details")
            order = orders.find_one({"order_id": order_id})
            
            if order is None:
                return error.error_invalid_order_id(order_id)

            # 验证订单是否属于该卖家
            user_store = self.get_collection("user_store")
            if not user_store.find_one({"user_id": user_id, "store_id": order["store_id"]}):
                return error.error_authorization_fail()

            order_detail = order_details.find_one({"order_id": order_id})
            
            if not order_detail:  # 如果未找到对应的订单详情
                return error.error_invalid_order_id(order_id)
            
            print("status = " + str(order_detail["status"]))
            if order_detail["status"] != "paid":
                return error.error_invalid_order_state(order_id)
            
            # 更新订单状态为已发货
            result = orders.update_one(
                {"order_id": order_id},
                {"$set": {"status": "delivered"}}
            )

            if result.modified_count == 0:
                return 528, "Failed to update order status"

        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        
        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        """
        买家确认收货
        :param user_id: 买家用户ID
        :param order_id: 订单ID
        :return: (code, message)
        """
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            # 获取订单信息
            orders = self.get_collection("orders")
            order = orders.find_one({"order_id": order_id})
            
            if order is None:
                return error.error_non_exist_order_id(order_id)

            # 验证订单是否属于该买家
            if order["user_id"] != user_id:
                return error.error_authorization_fail()

            # 检查订单状态是否为已发货
            if order["status"] != "delivered":
                return error.error_invalid_order_state()

            # 更新订单状态为已完成
            result = orders.update_one(
                {"order_id": order_id},
                {"$set": {"status": "completed"}}
            )

            self.delete_order_and_details(order_id)

            if result.modified_count == 0:
                return 528, "Failed to update order status"

        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        
        return 200, "ok"

    def user_id_exist(self, user_id: str) -> bool:
        users = self.get_collection('users')
        return users.count_documents({'user_id': user_id}) > 0
    
    def delete_order_and_details(self, order_id: str):
        orders = self.get_collection("orders")
        order_details = self.get_collection("order_details")

        # 删除订单
        orders.delete_one({"order_id": order_id})
        
        # 删除相关订单详情
        order_details.delete_many({"order_id": order_id})