from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import delivery

bp_delivery = Blueprint("delivery", __name__, url_prefix="/delivery")

@bp_delivery.route("/deliver", methods=["POST"])
def deliver_order():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    # print("success receive")
    d = delivery.Delivery()
    code, message = d.deliver_order(user_id, order_id)
    
    return jsonify({"message": message}), code

@bp_delivery.route("/receive", methods=["POST"])
def receive_order():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    
    d = delivery.Delivery()
    code, message = d.receive_order(user_id, order_id)
    
    return jsonify({"message": message}), code