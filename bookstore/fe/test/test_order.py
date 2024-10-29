import json
import pytest
import uuid
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
class TestOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_order_user_id_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        
        yield

    def test_order_history(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, orders = self.buyer.order_history()
        assert code == 200
        assert isinstance(orders, list)

    def test_cancel_order(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        print("order_id_in_order.py",order_id)
        code = self.buyer.cancel_order(order_id)
        assert code == 200
    
    def test_auto_cancel_timeout_orders(self):
        # 生成一本书并创建一个未支付的订单
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.old_order(self.store_id, buy_book_id_list)
        assert code == 200

        # 模拟等待超时并调用自动取消函数
        code, message = self.buyer.auto_cancel_timeout_orders(order_id)  # 假设这里调用的是 Buyer 类的函数
        assert code == 200
        assert message == "ok"

    def test_cancel_non_exist_order(self):
        order_id = "non_exist_order_id"
        code = self.buyer.cancel_order(order_id)
        assert code != 200

    def test_cancel_order_for_non_exist_user(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        order_id = "test_order_id_{}".format(str(uuid.uuid1())) 
        code = self.buyer.cancel_order(order_id)
        assert code != 200

    def test_order_history_for_non_exist_user(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        code, orders = self.buyer.order_history()
        assert code != 200
        assert orders == []


