import logging
# import os
# import sqlite3 as sqlite
import threading
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection


class Store:
    database: str

    # def __init__(self, db_path):
    #     self.database = os.path.join(db_path, "be.db")
    #     self.init_tables()
    def __init__(self, host: str = 'localhost', port: int = 27017, db_name: str = 'bookstore'):
        """
        初始化MongoDB连接
        :param host: MongoDB主机地址
        :param port: MongoDB端口号
        :param db_name: 数据库名称
        """
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.init_collections()

    # def init_tables(self):
    #     try:
    #         conn = self.get_db_conn()
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user ("
    #             "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
    #             "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user_store("
    #             "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS store( "
    #             "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
    #             " PRIMARY KEY(store_id, book_id))"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order( "
    #             "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order_detail( "
    #             "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
    #             "PRIMARY KEY(order_id, book_id))"
    #         )

    #         conn.commit()
    #     except sqlite.Error as e:
    #         logging.error(e)
    #         conn.rollback()
    def init_collections(self):
        """
        初始化所需的collections(相当于关系型数据库中的表)
        """
        try:
            # 用户集合
            if "users" not in self.db.list_collection_names():
                self.db.create_collection("users")
                self.db.users.create_index("user_id", unique=True)

            # 用户商店关系集合
            if "user_store" not in self.db.list_collection_names():
                self.db.create_collection("user_store")
                self.db.user_store.create_index([("user_id", 1), ("store_id", 1)], unique=True)

            # 商店集合
            if "stores" not in self.db.list_collection_names():
                self.db.create_collection("stores")
                self.db.stores.create_index([("store_id", 1), ("book_id", 1)], unique=True)

            # 订单集合
            if "orders" not in self.db.list_collection_names():
                self.db.create_collection("orders")
                self.db.orders.create_index("order_id", unique=True)

            # 订单详情集合
            if "order_details" not in self.db.list_collection_names():
                self.db.create_collection("order_details")
                self.db.order_details.create_index([("order_id", 1), ("book_id", 1)], unique=True)

        except Exception as e:
            logging.error(f"初始化MongoDB集合时出错: {str(e)}")
            raise e
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        获取指定的集合
        :param collection_name: 集合名称
        :return: MongoDB集合对象
        """
        return self.db[collection_name]

    def get_database(self) -> Database:
        """
        获取数据库实例
        :return: MongoDB数据库实例
        """
        return self.db

    def close(self):
        """
        关闭数据库连接
        """
        if self.client:
            self.client.close()
    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()
# database_instance: Optional[Store] = None

# def init_database(db_path):
#     global database_instance
#     database_instance = Store(db_path)
def init_database(host: str = 'localhost', port: int = 27017, db_name: str = 'bookstore'):
    """
    初始化全局数据库实例
    :param host: MongoDB主机地址
    :param port: MongoDB端口号
    :param db_name: 数据库名称
    """
    global database_instance
    if database_instance is None:
        database_instance = Store(host, port, db_name)

# def get_db_conn():
#     global database_instance
#     return database_instance.get_db_conn()
def get_db() -> Database:
    """
    获取数据库实例
    :return: MongoDB数据库实例
    """
    global database_instance
    if database_instance is None:
        init_database()
    return database_instance.get_database()


def get_collection(collection_name: str) -> Collection:
    """
    获取指定的集合
    :param collection_name: 集合名称
    :return: MongoDB集合对象
    """
    global database_instance
    if database_instance is None:
        init_database()
    return database_instance.get_collection(collection_name)
