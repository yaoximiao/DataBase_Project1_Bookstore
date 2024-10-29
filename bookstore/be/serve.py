import logging
import os
from flask import Flask
from flask import Blueprint
from flask import request
from requests import post
from be.view import auth
from be.view import seller
from be.view import buyer
from be.view import delivery
from be.view import search
from be.view import order
from be.model.store import init_database, init_completed_event

bp_shutdown = Blueprint("shutdown", __name__)
# app = Flask(__name__)

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."


def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")

    init_database(host='localhost', port=27017, db_name='bookstore')

    logging.basicConfig(filename=log_file, level=logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)
    app.register_blueprint(delivery.bp_delivery)
    app.register_blueprint(search.bp_search)
    # app.register_blueprint(order.bp_order)
    init_completed_event.set()
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,  # 启用调试模式
        use_reloader=False  # 禁用重载器，避免多次初始化
    )
