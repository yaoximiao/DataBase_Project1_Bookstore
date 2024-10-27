# from flask import Blueprint
# from flask import request
# from flask import jsonify
# from be.model import order
# from be.model import user

# bp_order = Blueprint("order", __name__, url_prefix="/order")

# @bp_order.route("/ship", methods=["POST"])
# def ship_order():
#     order_id = request.json.get("order_id")
#     seller_id = request.json.get("user_id")
#     store_id = request.json.get("store_id")
#     token = request.headers.get("token")
    
#     if not order_id or not seller_id or not store_id:
#         return jsonify({"message": "Invalid parameters"}), 400
        
#     user_instance = user.User()
#     code, message = user_instance.check_token(seller_id, token)
#     if code != 200:
#         return jsonify({"message": message}), code
        
#     order_manager = order.OrderManager()
#     code, message = order_manager.ship_order(seller_id, store_id, order_id)
#     return jsonify({"message": message}), code

# @bp_order.route("/cancel", methods=["POST"])
# def cancel_order():
#     order_id = request.json.get("order_id")
#     user_id = request.json.get("user_id")
#     reason = request.json.get("reason", "User request")
#     token = request.headers.get("token")

#     if not order_id or not user_id or not token:
#         return jsonify({"message": "Invalid parameters"}), 400

#     user_instance = user.User()
#     code, message = user_instance.check_token(user_id, token)
#     if code != 200:
#         return jsonify({"message": message}), code

#     order_manager = order.OrderManager()
#     code, message = order_manager.cancel_order(user_id, order_id, reason)
#     return jsonify({"message": message}), code

# @bp_order.route("/<order_id>", methods=["GET"])
# def get_order(order_id):
#     user_id = request.args.get("user_id")
#     token = request.headers.get("token")

#     if not order_id or not user_id or not token:
#         return jsonify({"message": "Invalid parameters"}), 400

#     user_instance = user.User()
#     code, message = user_instance.check_token(user_id, token)
#     if code != 200:
#         return jsonify({"message": message}), code

#     order_manager = order.OrderManager()
#     code, order_details = order_manager.get_order(user_id, order_id)
#     if code != 200:
#         return jsonify({"message": order_details}), code

#     return jsonify({"order": order_details}), code

# @bp_order.route("/history", methods=["GET"])
# def get_user_orders():
#     user_id = request.args.get("user_id")
#     status = request.args.get("status")  # 可选参数
#     token = request.headers.get("token")

#     if not user_id or not token:
#         return jsonify({"message": "Invalid parameters"}), 400

#     user_instance = user.User()
#     code, message = user_instance.check_token(user_id, token)
#     if code != 200:
#         return jsonify({"message": message}), code

#     order_manager = order.OrderManager()
#     code, orders = order_manager.get_user_orders(user_id, status)
#     return jsonify({"orders": orders}), code