from flask import Blueprint, request, jsonify
from be.model.search import BookSearch

bp_search = Blueprint("search", __name__, url_prefix="/search")

@bp_search.route("/books", methods=["GET"])
def search_books():
    """
    搜索图书API
    参数:
    - keywords: 搜索关键词
    - store_id: (可选)商店ID
    - search_scopes: (可选)搜索范围,多个范围用逗号分隔
    - page: (可选)页码,默认1
    - page_size: (可选)每页数量,默认20
    """
    try:
        # 获取查询参数
        keywords = request.args.get("keywords", "")
        store_id = request.args.get("store_id")
        search_scopes = request.args.get("search_scopes", "").split(",") if request.args.get("search_scopes") else None
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))

        # 参数验证
        if page < 1:
            return jsonify({"message": "Invalid page number"}), 400
        if page_size < 1:
            return jsonify({"message": "Invalid page size"}), 400

        # 执行搜索
        search = BookSearch()
        print("keyword="+str(keywords))
        print("store_id="+str(store_id))
        print("search_scopes="+str(search_scopes))
        print("page="+str(page))
        print("page_size="+str(page_size))
        result = search.search_books(
            keywords=keywords,
            store_id=store_id,
            search_scopes=search_scopes,
            page=page,
            page_size=page_size
        )

        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify({"message": result["message"]}), 500

    except ValueError as e:
        return jsonify({"message": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500

@bp_search.route("/book/<store_id>/<book_id>", methods=["GET"])
def get_book_detail(store_id: str, book_id: str):
    """
    获取图书详细信息API
    """
    try:
        search = BookSearch()
        result = search.get_book_detail(store_id, book_id)

        if result["status"] == "success":
            return jsonify(result["data"]), 200
        else:
            return jsonify({"message": result["message"]}), 404

    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500