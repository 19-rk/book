from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.views import views_bp
from app.views.utils import check_auth, check_missing_params

from app.controllers.Admin_operation_record import add_admin_operation_record
from app.controllers.Book_info import add_book_info, get_book_info_by_keyword, get_book_info, update_book_info, get_top_book_info
from app.controllers.Book_category import get_all_book_category

# 获取所有图书类别
@views_bp.route('/api/book/category', methods=['GET'])
def get_book_category():
    '''
    获取所有图书类别(code和名称)
    '''
    categorys = get_all_book_category()
    category_list = [ { 'code': _.code, 'name': _.name } for _ in categorys]
    return jsonify({'code': 200, 'message': '查询成功', 'categorys': category_list})

# 模糊查询图书
@views_bp.route('/api/book/page', methods=['GET'])
def search():
    # 获取查询参数
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    # 查询图书，模糊查询书名和作者和出版社
    try:
        books = get_book_info_by_keyword(keyword=keyword, page=page, per_page=per_page)
    except Exception as e:
        print('--------Error-模糊查询图书--------\n', e, '\n------------------------------')
        raise e

    return jsonify({'code': 200, 
                    'message': '查询成功',
                    'books': books['books'], 
                    'total_pages': books['total_pages'],
                    'total_items': books['total_items']})

# 查询图书
@views_bp.route('/api/book/getById', methods=['GET'])
def get_book_by_id():
    '''
    必需参数: 图书编号
    '''
    # 获取查询参数
    book_id = request.args.get('book_id', '')
    # 返回图书信息
    return jsonify({'code': 200, 'message': '查询成功', 'book': get_book_info(book_id)})

# 添加图书
@views_bp.route('/api/book/add', methods=['POST'])
@jwt_required()
def add_book():
    '''
    添加图书, 需要管理员权限
    必需参数: 分类编码、ISBN、书名、作者、出版社、价格
    '''
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=True)
    # 检查参数
    data = request.get_json()
    check_missing_params(data,['category_code','isbn','title','author','publisher','price'])
    # 添加图书
    try:
        add_book_info(category_code=data.get('category_code'),
                         isbn=data.get('isbn'),
                         title=data.get('title'),
                         author=data.get('author'),
                         publisher=data.get('publisher'),
                         publish_date=data.get('publish_date', None),
                         price=data.get('price'),
                         intro=data.get('intro', '无'),
                         status=data.get('status', '在馆'),
                         commit_now=False)
        add_admin_operation_record(get_jwt_identity(), None, None, '添加图书'+"《"+data.get('title')+"》", reason='无', commit_now=True)
        return jsonify({'code': 200, 'message': '添加成功'})
    except Exception as e:
        print('--------Error-添加图书--------\n', e, '\n------------------------------')
        raise e

# 修改图书
@views_bp.route('/api/book/update', methods=['PUT'])
@jwt_required()
def book_update():
    '''
    修改图书, 需要管理员权限
    必需参数: 图书编号
    可选参数: 分类编码、ISBN、书名、作者、出版社、出版日期、价格、简介、状态
    '''
    print('------------------', request.get_json())
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=True)
    # 检查参数
    data = request.get_json()
    check_missing_params(data,['book_id'])
    # 修改图书
    try:
        update_book_info( book_id=data['book_id'],
                          category_code=data.get('category_code'),
                          isbn=data.get('isbn'),
                          title=data.get('title'),
                          author=data.get('author'),
                          publisher=data.get('publisher'),
                          publish_date=data.get('publish_date'),
                          price=data.get('price'),
                          intro=data.get('intro'),
                          status=data.get('status')
                        )
        return jsonify({'code': 200, 'message': '修改成功'})
    except Exception as e:
        print('--------Error-修改图书--------\n', e, '\n------------------------------')
        raise e

# 删除图书
@views_bp.route('/api/book/delete', methods=['DELETE'])
@jwt_required()
def book_delete():
    '''
    删除图书, 需要管理员权限
    必需参数: 图书编号
    可选参数: 下架原因
    '''
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=True)
    # 检查参数
    data = request.get_json()
    check_missing_params(data,['book_id'])   
    # 删除图书,修改为下架状态
    book = get_book_info(data['book_id'])
    if book['status'] != '在馆':
        return jsonify({'code': 400, 'message': '图书'+book['status']+'，无法下架'})
    try:
        update_book_info(book_id=data['book_id'], status='下架', commit_now=False)
        add_admin_operation_record(get_jwt_identity(), None, None, '下架图书'+"《"+book['title']+"》", reason=data.get('reason', '无'))
        return jsonify({'code': 200, 'message': '下架成功'})
    except Exception as e:
        print('--------Error-下架图书--------\n', e, '\n------------------------------')
        raise e
    
@views_bp.route('/api/book/top', methods=['GET'])
def get_top_book():
    n = request.args.get('n', 10, type=int)
    return jsonify({'code': 200, 'message': '查询成功', 'books': get_top_book_info(n)})
