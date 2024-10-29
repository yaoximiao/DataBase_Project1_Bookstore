# from urllib.parse import urljoin
# import requests

# class OrderAccess:
#     def __init__(self, url_prefix, token):
#         self.url_prefix = urljoin(url_prefix, 'order/')
#         self.token = token

#     def create_order(self, buyer_id, store_id, book_id, quantity):
#         url = urljoin(self.url_prefix, 'create')
#         headers = {'token': self.token}
#         data = {
#             'buyer_id': buyer_id,
#             'store_id': store_id,
#             'book_id': book_id,
#             'quantity': quantity
#         }
#         response = requests.post(url, headers=headers, json=data)
#         return response.status_code, response.json().get('order_id')

#     def get_order_status(self, order_id):
#         url = urljoin(self.url_prefix, f'status/{order_id}')
#         headers = {'token': self.token}
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             return response.json().get('status')
#         else:
#             return None

#     def cancel_order(self, order_id):
#         url = urljoin(self.url_prefix, f'cancel/{order_id}')
#         headers = {'token': self.token}
#         response = requests.post(url, headers=headers)
#         return response.status_code

#     def get_buyer_orders(self, buyer_id):
#         url = urljoin(self.url_prefix, f'buyer/{buyer_id}')
#         headers = {'token': self.token}
#         response = requests.get(url, headers=headers)
#         return response.json()

#     def auto_cancel_orders(self):
#         url = urljoin(self.url_prefix, 'auto_cancel')
#         headers = {'token': self.token}
#         response = requests.post(url, headers=headers)
#         return response.status_code