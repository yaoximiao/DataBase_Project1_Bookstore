import pytest
from fe.access.book_search import SearchBooks
from fe.access.new_seller import register_new_seller
from fe.test.gen_book_data import GenBook
from fe import conf
import uuid

class TestSearchBooks:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # 初始化测试数据
        self.seller_id = "test_search_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        # 生成测试图书数据
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        assert ok

        self.buy_book_info_list = gen_book.buy_book_info_list
        self.search = SearchBooks(conf.URL)
        yield

    def test_search_by_keyword(self):
        # 测试基本关键词搜索
        book = self.buy_book_info_list[0][0]
        code, result = self.search.search_books(keywords=book.title)
        assert code == 200
        print(result["total"])
        assert result["total"] > 0
        assert result["status"] == "success"

    def test_search_with_store(self):
        # 测试指定商店搜索
        code, result = self.search.search_books(store_id=self.store_id)
        assert code == 200
        assert result["total"] > 0
        for book in result["books"]:
            assert book["store_id"] == self.store_id

    def test_search_with_scopes(self):
        # 测试指定搜索范围
        book = self.buy_book_info_list[0][0]
        scopes = ["title", "tags"]
        code, result = self.search.search_books(
            keywords=book.title,
            search_scopes=scopes
        )
        assert code == 200
        assert result["status"] == "success"

    def test_pagination(self):
        # 测试分页功能
        page_size = 2
        code, result = self.search.search_books(
            store_id=self.store_id,
            page=1,
            page_size=page_size
        )
        assert code == 200
        assert len(result["books"]) <= page_size

        if result["total_pages"] > 1:
            code, result2 = self.search.search_books(
                store_id=self.store_id,
                page=2,
                page_size=page_size
            )
            assert code == 200
            assert result2["books"] != result["books"]

    def test_invalid_pagination(self):
        # 测试无效的分页参数
        code, result = self.search.search_books(page=0)
        assert code == 400

        code, result = self.search.search_books(page_size=0)
        assert code == 400

    def test_get_book_detail(self):
        # 测试获取图书详情
        book = self.buy_book_info_list[0][0]
        code, result = self.search.get_book_detail(self.store_id, book.id)
        assert code == 200
        assert "book_info" in result
        assert result["book_info"]["id"] == book.id

    def test_get_non_exist_book(self):
        # 测试获取不存在的图书
        non_exist_id = str(uuid.uuid1())
        code, result = self.search.get_book_detail(self.store_id, non_exist_id)
        assert code == 404

    def test_search_non_exist_store(self):
        # 测试搜索不存在的商店
        non_exist_store = str(uuid.uuid1())
        code, result = self.search.search_books(store_id=non_exist_store)
        assert code == 200
        assert result["total"] == 0

    def test_search_with_empty_keyword(self):
        # 测试空关键词搜索
        code, result = self.search.search_books(keywords="")
        assert code == 200
        assert result["status"] == "success"

    def test_search_with_special_characters(self):
        # 测试特殊字符搜索
        code, result = self.search.search_books(keywords="!@#$%^")
        assert code == 200
        assert result["total"] == 0