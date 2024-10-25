import jwt
import time
import logging
from pymongo.errors import DuplicateKeyError, PyMongoError
from be.model import error
from be.model import db_conn

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded

def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.users = self.get_collection("users")

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = f"terminal_{str(time.time())}"
            token = jwt_encode(user_id, terminal)
            self.users.insert_one({
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            })
            print("user_id in register", user_id)
        except DuplicateKeyError:
            return error.error_exist_user_id(user_id)
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        user = self.users.find_one({"user_id": user_id})
        if user is None:
            return error.error_authorization_fail()
        db_token = user['token']
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.users.find_one({"user_id": user_id})
        if user is None:
            return error.error_authorization_fail()
        if password != user['password']:
            return error.error_authorization_fail()
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            result = self.users.update_one(
                {"user_id": user_id},
                {"$set": {"token": token, "terminal": terminal}}
            )
            if result.modified_count == 0:
                return error.error_authorization_fail() + ("",)
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}", ""
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}", ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = f"terminal_{str(time.time())}"
            dummy_token = jwt_encode(user_id, terminal)

            result = self.users.update_one(
                {"user_id": user_id},
                {"$set": {"token": dummy_token, "terminal": terminal}}
            )
            if result.modified_count == 0:
                return error.error_authorization_fail()
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            result = self.users.delete_one({"user_id": user_id})
            if result.deleted_count == 0:
                return error.error_authorization_fail()
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = f"terminal_{str(time.time())}"
            token = jwt_encode(user_id, terminal)
            result = self.users.update_one(
                {"user_id": user_id},
                {"$set": {"password": new_password, "token": token, "terminal": terminal}}
            )
            if result.modified_count == 0:
                return error.error_authorization_fail()
        except PyMongoError as e:
            return 528, f"MongoDB Error: {str(e)}"
        except BaseException as e:
            return 530, f"Unexpected Error: {str(e)}"
        return 200, "ok"