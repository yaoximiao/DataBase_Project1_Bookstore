# import requests
# from urllib.parse import urljoin


# class Order:
#     def __init__(self, url_prefix):
#         self.url_prefix = urljoin(url_prefix, "order/")

#     def ship_order(self, order_id: str, user_id: str, store_id: str, token: str) -> (int, str):
#         json = {"order_id": order_id, "user_id": user_id, "store_id": store_id}
#         headers = {"token": token}
#         url = urljoin(self.url_prefix, "ship")
#         r = requests.post(url, headers=headers, json=json)
#         return r.status_code, r.json().get("message")

#     def cancel_order(self, order_id: str, user_id: str, reason: str, token: str) -> int:
#         json = {"order_id": order_id, "user_id": user_id, "reason": reason}
#         headers = {"token": token}
#         url = urljoin(self.url_prefix, "cancel")
#         r = requests.post(url, headers=headers, json=json)
#         return r.status_code

#     def get_order(self, order_id: str, user_id: str, token: str) -> (int, dict):
#         headers = {"token": token}
#         url = urljoin(self.url_prefix, order_id)
#         params = {"user_id": user_id}
#         r = requests.get(url, headers=headers, params=params)
#         return r.status_code, r.json().get("order")

#     def get_user_orders(self, user_id: str, token: str, status: str = None) -> (int, list):
#         headers = {"token": token}
#         url = urljoin(self.url_prefix, "history")
#         params = {"user_id": user_id}
#         if status:
#             params["status"] = status
#         r = requests.get(url, headers=headers, params=params)
#         return r.status_code, r.json().get("orders")
