import requests
from urllib.parse import urljoin
from fe.access.auth import Auth

class Delivery:
    def __init__(self, url_prefix, user_id: str, password: str):
        self.url_prefix = urljoin(url_prefix, "delivery/")
        self.user_id = user_id
        self.password = password
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        print("init_code="+str(code))
        assert code == 200

    def deliver_order(self, order_id: str) -> int:
        json = {
            "user_id": self.user_id,
            "order_id": order_id
        }
        print("order_id="+str(order_id))
        url = urljoin(self.url_prefix, "deliver")
        print("url="+str(url))
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def receive_order(self, order_id: str) -> int:
        json = {
            "user_id": self.user_id,
            "order_id": order_id
        }
        url = urljoin(self.url_prefix, "receive")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code