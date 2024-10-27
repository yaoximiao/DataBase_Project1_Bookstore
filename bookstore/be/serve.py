# import logging
# import os
# from flask import Flask
# from flask import Blueprint
# from flask import request
# from requests import post
# from be.view import auth
# from be.view import seller
# from be.view import buyer
# from be.model.store import init_database, init_completed_event

# bp_shutdown = Blueprint("shutdown", __name__)


# def shutdown_server():
#     func = request.environ.get("werkzeug.server.shutdown")
#     if func is None:
#         raise RuntimeError("Not running with the Werkzeug Server")
#     func()


# @bp_shutdown.route("/shutdown")
# def be_shutdown():
#     shutdown_server()
#     return "Server shutting down..."


# def be_run():
#     this_path = os.path.dirname(__file__)
#     parent_path = os.path.dirname(this_path)
#     log_file = os.path.join(parent_path, "app.log")
#     init_database(host: str = 'localhost', port: int = 27017, db_name: str = 'bookstore_db')

#     logging.basicConfig(filename=log_file, level=logging.ERROR)
#     handler = logging.StreamHandler()
#     formatter = logging.Formatter(
#         "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
#     )
#     handler.setFormatter(formatter)
#     logging.getLogger().addHandler(handler)

#     app = Flask(__name__)
#     app.register_blueprint(bp_shutdown)
#     app.register_blueprint(auth.bp_auth)
#     app.register_blueprint(seller.bp_seller)
#     app.register_blueprint(buyer.bp_buyer)
#     init_completed_event.set()
#     app.run()

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
from be.model.store import init_database, init_completed_event

bp_shutdown = Blueprint("shutdown", __name__)


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

    # 这里修复了 init_database 的调用，移除了类型注解
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
    init_completed_event.set()
    app.run()
