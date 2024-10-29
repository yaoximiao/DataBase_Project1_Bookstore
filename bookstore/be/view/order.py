# from flask import Blueprint, request, jsonify
# from be.model.order import Order

# bp_order = Blueprint('order', __name__, url_prefix='/order')

# @bp_order.route('/create', methods=['POST'])
# def create_order():
#     buyer_id = request.json['buyer_id']
#     store_id = request.json['store_id'] 
#     book_id = request.json['book_id']
#     quantity = request.json['quantity']

#     order = Order()
#     order_id = order.create_order(buyer_id, store_id, book_id, quantity)
#     return jsonify({'order_id': order_id}), 200

# @bp_order.route('/status/<order_id>', methods=['GET'])
# def get_order_status(order_id):
#     order = Order()
#     status = order.get_order_status(order_id)
#     if status:
#         return jsonify({'status': status}), 200
#     else:
#         return jsonify({'message': 'Order not found'}), 404

# @bp_order.route('/cancel/<order_id>', methods=['POST'])
# def cancel_order(order_id):
#     order = Order()
#     if order.cancel_order(order_id):
#         return jsonify({'message': 'Order canceled'}), 200
#     else:
#         return jsonify({'message': 'Order cannot be canceled'}), 400

# @bp_order.route('/buyer/<buyer_id>', methods=['GET'])
# def get_buyer_orders(buyer_id):
#     order = Order()
#     orders = order.get_buyer_orders(buyer_id)
#     return jsonify(orders), 200

# @bp_order.route('/auto_cancel', methods=['POST'])
# def auto_cancel_orders():
#     order = Order()
#     order.auto_cancel_orders()
#     return jsonify({'message': 'Overdue orders canceled'}), 200