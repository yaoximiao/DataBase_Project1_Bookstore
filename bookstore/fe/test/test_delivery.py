import pytest
import uuid
from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from fe.access.delivery import Delivery
from fe.test.gen_book_data import GenBook
from fe.access.book import Book
from fe import conf

class TestDelivery:
    buy_book_info_list: [Book]
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # 初始化卖家用户
        self.seller_id = "test_delivery_seller_{}".format(str(uuid.uuid1()))
        self.store_id = "test_delivery_store_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        # 生成测试图书数据
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, 
            low_stock_level=False,
            max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok

        # 初始化买家用户
        self.buyer_id = "test_delivery_buyer_{}".format(str(uuid.uuid1()))
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        # 计算总价
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        # 买家下单并付款
        self.buyer.add_funds(self.total_price + 1000)  # 多充值一些以确保足够
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        print("pre操作后的order_id="+self.order_id)
        code = self.buyer.payment(self.order_id)
        assert code == 200

        # 创建发货和收货对象
        self.seller_delivery = Delivery(conf.URL, self.seller_id, self.password)
        self.buyer_delivery = Delivery(conf.URL, self.buyer_id, self.password)

        yield

    def test_ok(self):
        """测试正常发货和收货流程"""
        # 卖家发货
        print("test_ok_order_id="+str(self.order_id))
        code = self.seller_delivery.deliver_order(self.order_id)
        assert code == 200

        # 买家收货
        code = self.buyer_delivery.receive_order(self.order_id)
        assert code == 200

    def test_repeat_deliver(self):
        """测试重复发货"""
        # 第一次发货
        code = self.seller_delivery.deliver_order(self.order_id)
        assert code == 200

        # 重复发货
        code = self.seller_delivery.deliver_order(self.order_id)
        assert code != 200

    def test_deliver_non_exist_order(self):
        """测试发货不存在的订单"""
        non_exist_order_id = str(uuid.uuid1())
        code = self.seller_delivery.deliver_order(non_exist_order_id)
        assert code != 200

    def test_buyer_deliver(self):
        """测试买家尝试发货（权限验证）"""
        code = self.buyer_delivery.deliver_order(self.order_id)
        assert code != 200

    def test_seller_receive(self):
        """测试卖家尝试确认收货（权限验证）"""
        # 先由卖家发货
        code = self.seller_delivery.deliver_order(self.order_id)
        assert code == 200

        # 卖家尝试确认收货
        code = self.seller_delivery.receive_order(self.order_id)
        assert code != 200

    def test_receive_before_deliver(self):
        """测试在发货前确认收货"""
        code = self.buyer_delivery.receive_order(self.order_id)
        assert code != 200

    def test_receive_non_exist_order(self):
        """测试确认收货不存在的订单"""
        non_exist_order_id = str(uuid.uuid1())
        code = self.buyer_delivery.receive_order(non_exist_order_id)
        assert code != 200

    def test_repeat_receive(self):
        """测试重复确认收货"""
        # 卖家发货
        code = self.seller_delivery.deliver_order(self.order_id)
        assert code == 200

        # 第一次确认收货
        code = self.buyer_delivery.receive_order(self.order_id)
        assert code == 200

        # 重复确认收货
        code = self.buyer_delivery.receive_order(self.order_id)
        assert code != 200

    # def test_authentication_error(self):
    #     """测试认证错误"""
    #     # 使用错误的密码创建delivery对象
    #     wrong_seller_delivery = Delivery(conf.URL, self.seller_id, self.password + "_x")
    #     code = wrong_seller_delivery.deliver_order(self.order_id)
    #     assert code != 200
        """测试认证错误"""