from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code

@bp_buyer.route("/old_order", methods=["POST"])
def old_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.old_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code

@bp_buyer.route("/order_history", methods=["POST"])
def order_history():
    user_id: str = request.json.get("user_id")
    b = Buyer()
    code, message, orders = b.get_order_history(user_id)
    return jsonify({"message": message, "orders": orders}), code

@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.cancel_order(user_id, order_id)
    return jsonify({"message": message}), code

@bp_buyer.route("/auto_cancel_timeout_orders", methods=["POST"])
def auto_cancel():
    data = request.get_json()  # 从请求中获取 JSON 数据
    order_id = data.get("order_id")
    # 检查是否提供了必要的参数
    if not order_id :
        return jsonify({"message": "Missing user_id or timeout"}), 400

    b = Buyer()  # 创建 Buyer 实例，传入 user_id
    code, message = b.auto_cancel_timeout_orders(order_id)

    return jsonify({"message": message}), code

@bp_buyer.route("/get_order_details", methods=["GET"])
def get_order_details():
    """获取订单详情"""
    b = Buyer()  # 创建 Buyer 实例
    data = request.args  # 从请求中获取 JSON 数据
    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"message": "Missing order_id"}), 400  # 如果没有提供 order_id，返回 400 错误

    # 调用获取订单详情的函数
    code, order_details = b.get_order_details(order_id)

    # 返回相应的状态码和订单详情
    if code == 200:
        return jsonify(order_details), 200  # 返回订单详情和 200 状态码
    else:
        return jsonify({"message": order_details}), code  