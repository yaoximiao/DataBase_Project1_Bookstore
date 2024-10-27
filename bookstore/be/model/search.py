from typing import Dict, List, Optional
from be.model import db_conn
from pymongo.errors import PyMongoError
from pymongo import ASCENDING, TEXT

class BookSearch(db_conn.DBConn):
    def __init__(self):
        super().__init__()
        # 确保创建必要的索引
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """创建必要的索引以优化搜索性能"""
        try:
            stores = self.get_collection("stores")
            # 为book_info字段创建文本索引
            stores.create_index([
                ("book_info.title", TEXT),
                ("book_info.tags", TEXT),
                ("book_info.content", TEXT),
                ("book_info.book_intro", TEXT)
            ])
            # 为store_id创建普通索引
            stores.create_index([("store_id", ASCENDING)])
        except PyMongoError as e:
            print(f"Index creation failed: {str(e)}")

    def search_books(self, 
                    keywords: str,
                    store_id: Optional[str] = None,
                    search_scopes: Optional[List[str]] = None,
                    page: int = 1,
                    page_size: int = 20) -> Dict:
        """
        搜索图书
        :param keywords: 搜索关键词
        :param store_id: 商店ID,如果提供则只搜索该商店
        :param search_scopes: 搜索范围列表,可包含 title,tags,content,book_intro
        :param page: 当前页码(从1开始)
        :param page_size: 每页显示数量
        :return: 包含搜索结果和分页信息的字典
        """
        try:
            stores = self.get_collection("stores")
            
            # 构建搜索条件
            query = {}
            
            # 添加商店过滤条件
            if store_id:
                query["store_id"] = store_id
            
            # 添加文本搜索条件
            if keywords:
                # 根据搜索范围构建查询条件
                if search_scopes:
                    text_search_fields = []
                    for scope in search_scopes:
                        if scope in ["title", "tags", "content", "book_intro"]:
                            field_path = f"book_info.{scope}"
                            text_search_fields.append({field_path: {"$regex": keywords, "$options": "i"}})
                    if text_search_fields:
                        query["$or"] = text_search_fields
                else:
                    # 如果未指定搜索范围,则在所有支持的字段中搜索
                    query["$text"] = {"$search": keywords}

            # 计算总数
            total_count = stores.count_documents(query)
            
            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size
            
            # 确保页码有效
            page = max(1, min(page, total_pages))
            
            # 执行分页查询
            skip = (page - 1) * page_size
            cursor = stores.find(
                query,
                {
                    "book_info": 1,
                    "store_id": 1,
                    "stock_level": 1,
                    "_id": 0
                }
            ).skip(skip).limit(page_size)
            
            # 构造返回结果
            books = list(cursor)
            
            return {
                "status": "success",
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "books": books
            }
            
        except PyMongoError as e:
            return {
                "status": "error",
                "message": f"Database error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
            
    def get_book_detail(self, store_id: str, book_id: str) -> Dict:
        """
        获取图书详细信息
        :param store_id: 商店ID
        :param book_id: 图书ID
        :return: 图书详细信息
        """
        try:
            stores = self.get_collection("stores")
            book = stores.find_one(
                {"store_id": store_id, "book_id": book_id},
                {"book_info": 1, "stock_level": 1, "_id": 0}
            )
            if book:
                return {
                    "status": "success",
                    "data": book
                }
            else:
                return {
                    "status": "error",
                    "message": "Book not found"
                }
        except PyMongoError as e:
            return {
                "status": "error",
                "message": f"Database error: {str(e)}"
            }