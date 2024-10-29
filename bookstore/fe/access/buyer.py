import datetime
import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth
import json
from datetime import datetime, timedelta


class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")
    
    def old_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "old_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: str) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
    def order_history(self):
        json = {
            "user_id": self.user_id
        }
        url = urljoin(self.url_prefix, "order_history")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code, r.json().get("orders", [])

    def cancel_order(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "cancel_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
    def auto_cancel_timeout_orders(self, order_id) -> (int, str):
        """自动取消超时未支付订单"""
        url = None
        headers=None
        try:
           
            # 请求获取超时未支付订单
            url = urljoin(self.url_prefix, "auto_cancel_timeout_orders")
            headers = {"token": self.token}
            json = {
                "order_id": order_id
            }
            r = requests.post(url, headers=headers, json=json)
            if r.status_code != 200:
                return r.status_code, r.json().get("message", "Error retrieving timeout orders")
            
            return r.status_code, "ok"
        except Exception as e:
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Payload: {json}")
            print(f"Error: {str(e)}")
            return 500, str(e)
        
    def get_order_details(self, order_id) -> (int, dict):
        # """获取订单详情"""
        url = None
        headers = None
        try:
            # 请求获取订单详情
            url = urljoin(self.url_prefix, f"get_order_details")  
            headers = {"token": self.token}
            params = {
                "order_id": order_id
            }
            print("pass here")
            r = requests.get(url, headers=headers, params=params)
            
            if r.status_code != 200:
                print("r.status_code="+str(r.status_code))
                return r.status_code, {"message": r.json().get("message", "Error retrieving order details")}
            # print(r.json())
            return r.status_code, r.json()  # 返回订单详情的 JSON 数据
        except Exception as e:
            return 500, {"message": str(e)}
