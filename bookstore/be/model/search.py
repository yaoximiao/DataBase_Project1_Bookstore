# from be.model import db_conn
# from be.model import error
# from typing import Dict, List, Optional

# class SearchManager(db_conn.DBConn):
#     def __init__(self):
#         db_conn.DBConn.__init__(self)
#         self.books = self.get_collection("books")
        
#         # 创建文本索引
#         self.books.create_index([
#             ("title", "text"),
#             ("author", "text"),
#             ("tags", "text"),
#             ("content", "text"),
#             ("book_intro", "text")
#         ])
    
#     def search_books(self, 
#                     keywords: str,
#                     store_id: Optional[str] = None,
#                     page: int = 1,
#                     page_size: int = 20) -> (int, str, Dict):
#         try:
#             # 构建查询条件
#             query = {"$text": {"$search": keywords}}
#             if store_id:
#                 query["store_id"] = store_id
                
#             # 计算分页
#             skip = (page - 1) * page_size
            
#             # 执行搜索，按相关性排序
#             cursor = self.books.find(
#                 query,
#                 {"score": {"$meta": "textScore"}}
#             ).sort([
#                 ("score", {"$meta": "textScore"})
#             ]).skip(skip).limit(page_size)
            
#             # 获取总数
#             total = self.books.count_documents(query)
            
#             # 格式化结果
#             books = []
#             for book in cursor:
#                 books.append({
#                     "book_id": book["id"],
#                     "title": book["title"],
#                     "author": book.get("author", ""),
#                     "price": book["price"],
#                     "tags": book.get("tags", []),
#                     "store_id": book["store_id"]
#                 })
                
#             return 200, "ok", {
#                 "books": books,
#                 "total": total,
#                 "page": page,
#                 "total_pages": (total + page_size - 1) // page_size
#             }
            
#         except Exception as e:
#             return 530, f"Search error: {str(e)}", None