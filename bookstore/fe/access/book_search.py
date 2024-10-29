import requests
from urllib.parse import urljoin

class SearchBooks:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def search_books(self, keywords: str = "", store_id: str = None, search_scopes: list = None, page: int = 1, page_size: int = 20) -> (int, dict):
        """
        搜索图书
        :return: (code, response) HTTP状态码和响应数据
        """
        params = {
            "keywords": keywords,
            "page": page,
            "page_size": page_size
        }
        if store_id:
            params["store_id"] = store_id
        if search_scopes:
            params["search_scopes"] = ",".join(search_scopes)

        url = urljoin(self.url_prefix, "books")
        r = requests.get(url, params=params)
        return r.status_code, r.json() if r.status_code == 200 else None

    def get_book_detail(self, store_id: str, book_id: str) -> (int, dict):
        """
        获取图书详情
        :return: (code, response) HTTP状态码和响应数据
        """
        url = urljoin(self.url_prefix, f"book/{store_id}/{book_id}")
        r = requests.get(url)
        return r.status_code, r.json() if r.status_code == 200 else None