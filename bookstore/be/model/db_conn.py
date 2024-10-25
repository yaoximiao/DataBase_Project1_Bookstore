from be.model import store
from pymongo.database import Database
from pymongo.collection import Collection

class DBConn:
    def __init__(self):
        # self.db: Database = store.get_db_conn()
        self.db: Database = store.get_db()
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        获取指定的集合
        :param collection_name: 集合名称
        :return: MongoDB集合对象
        """
        return store.get_collection(collection_name)

    def user_id_exist(self, user_id):
        # user_collection = self.db.user
        # return user_collection.count_documents({"user_id": user_id}) > 0
        """
        检查用户ID是否存在
        :param user_id: 用户ID
        :return: 存在返回True，否则返回False
        """
        users = self.get_collection("users")
        return users.count_documents({"user_id": user_id}) > 0
    
    def book_id_exist(self, store_id, book_id):
        # store_collection = self.db.store
        # return store_collection.count_documents({"store_id": store_id, "book_id": book_id}) > 0
        """
        检查指定商店中的图书是否存在
        :param store_id: 商店ID
        :param book_id: 图书ID
        :return: 存在返回True，否则返回False
        """
        stores = self.get_collection("stores")
        return stores.count_documents({
            "store_id": store_id,
            "book_id": book_id
        }) > 0
    

    def store_id_exist(self, store_id):
        # user_store_collection = self.db.user_store
        # return user_store_collection.count_documents({"store_id": store_id}) > 0
        """
        检查商店ID是否存在
        :param store_id: 商店ID
        :return: 存在返回True，否则返回False
        """
        user_store = self.get_collection("user_store")
        return user_store.count_documents({"store_id": store_id}) > 0