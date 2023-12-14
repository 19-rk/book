from datetime import datetime, timedelta
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.views import views_bp

from app.views.utils import check_auth, check_missing_params, check_user_id
from app.controllers.Borrow_info import get_borrow_count_byid, get_borrow_info_by_book, get_borrow_info_with_book, get_history_borrow_info_with_book, add_borrow_info, add_history_borrow_info
from app.controllers.Borrow_info import  update_borrow_info, delete_borrow_info_by_book
from app.controllers.Book_info import get_book_info, update_book_info

# 获取用户借阅数量
@views_bp.route('/api/borrow/count', methods=['GET'])
@jwt_required()
def get_borrow_count():
    '''
    可选参数: user_id
    管理员:   使用user_id, 查询用户的借阅数量
    普通用户: 不使用user_id, 查询自己的借阅数量
    '''
    check_auth(get_jwt_identity(), admin_auth=False)
    user_id = check_user_id(request.args.get('user_id', None), get_jwt_identity(), admin_need_user_id=True)

    # 查询用户借阅数量
    count = get_borrow_count_byid(user_id)
    return jsonify({'code': 200,
                    'message': '查询成功', 
                    'count': count, 
                    'info': '您有{}条借阅记录, 请注意归还'.format(count) if count > 0 else '您暂无借阅记录'})

# 借阅图书
@views_bp.route('/api/borrow/borrow', methods=['POST'])
@jwt_required()
def borrow():
    '''
    需要参数: book_id, user_id
    图书状态已借
    添加借阅记录
    '''
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=True)
    # 检查参数
    data = request.get_json()
    check_missing_params(data, ['book_id', 'user_id'])
    # 查询图书
    book = get_book_info(data['book_id'])
    # 检查图书是否已借出
    if book['status'] != '在馆':
        return jsonify({'code': 400, 'message': '图书已经'+book['status']})
    try:
        update_book_info(book_id=book['book_id'], status='借出', commit_now=False)
        add_borrow_info(
            book_id = book['book_id'],
            user_id = data['user_id'],
            borrow_date = datetime.now(),
            due_date = datetime.now() + timedelta(days = 30)
        )
        return jsonify({'code': 200, 'message': '借阅成功'})
    except Exception as e:
        print('--------Error-借阅图书--------\n', e, '\n------------------------------')
        raise e
# 续借
@views_bp.route('/api/borrow/renew', methods=['POST'])
@jwt_required()
def renew():
    '''
    需要参数: book_id
    可选参数: days 整数续借天数,默认30天
    '''
    # 鉴权
    check_auth( get_jwt_identity(), admin_auth=True)
    # 检查参数
    data = request.get_json()
    check_missing_params(data, ['book_id'])
    # 查询借阅
    borrow = get_borrow_info_by_book(data['book_id']) 
    if borrow is None:
        raise Exception('借阅记录不存在')

    new_due_date = borrow.due_date + timedelta(days=int(data.get('days', 30)))
    try:
        update_borrow_info(borrow.borrow_id, due_date=new_due_date)
        return jsonify({'code': 200, 'message': '续借成功'})
    except Exception as e:
        print('--------Error-借阅图书--------\n', e, '\n------------------------------')
        raise e
 
# 归还
@views_bp.route('/api/borrow/return', methods=['POST'])
@jwt_required()
def borrow_return():
    '''
    参数: book_id
    借阅记录删除，历史借阅增加
    对应book_info.status改变
    '''
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=True)

    # 检查参数
    data = request.get_json()
    check_missing_params(data, ['book_id'])

    # 查询借阅记录
    borrow = get_borrow_info_by_book(data['book_id'])
    try:
        update_book_info(borrow.book_id, status='在馆', commit_now=False)
        delete_borrow_info_by_book(borrow.book_id, commit_now=False)
        add_history_borrow_info(
            book_id = borrow.book_id,
            user_id = borrow.user_id,
            borrow_date = borrow.borrow_date,
            due_date = borrow.due_date,
            return_date = datetime.now()
        )
        return jsonify({'code': 200, 'message': '归还成功'})
    except Exception as e:
        print('--------Error-归还图书--------\n', e, '\n------------------------------')
        raise e

# 查询借阅记录
@views_bp.route('/api/borrow/page', methods=['GET'])
@jwt_required()
def borrow_page():
    '''
    可选参数: user_id,管理员可获取全部or指定用户的借阅记录
    '''
    # 鉴权
    user_id = get_jwt_identity()
    check_auth(user_id, admin_auth=False)
    
    user_id = check_user_id(request.args.get('user_id', None), user_id)
    keyword = request.args.get('keyword', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    
    # 查询借阅记录,多表联查
    borrow_records = get_borrow_info_with_book(user_id=user_id, keyword=keyword, page=page, per_page=per_page)
    # 返回借阅信息
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'books': borrow_records.get('books'),
        'total_pages': borrow_records.get('total_pages'),
        'total_items': borrow_records.get('total_items')
    })

# 查询历史借阅信息
@views_bp.route('/api/borrow/HistoricalPage', methods=['GET'])
@jwt_required()
def HistoricalPage_page():
    # 鉴权
    user_id = get_jwt_identity()
    check_auth(user_id, admin_auth=False)
    user_id = check_user_id(request.args.get('user_id', None), user_id)
    keyword = request.args.get('keyword', None)

    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    # 查询借阅记录,多表联查
    borrow_records = get_history_borrow_info_with_book(user_id=user_id,keyword=keyword, page=page, per_page=per_page) 
    # 返回借阅信息
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'books': borrow_records.get('books'),
        'total_pages': borrow_records.get('total_pages'),
        'total_items': borrow_records.get('total_items')
        })

# 临期的书
@views_bp.route('/api/borrow/expire', methods=['GET'])
@jwt_required()
def expire_books():
    '''
    可选参数: user_id,管理员可获取全部or指定用户的借阅记录
    可选参数: due_days: 临期天数,默认5天
    可选参数: page: 页码
    可选参数: pageSize: 每页数量
    '''
    # 鉴权
    user_id = get_jwt_identity()
    check_auth(user_id, admin_auth=False)
    
    user_id = check_user_id(request.args.get('user_id', None), user_id)
    due_days = request.args.get('due_days', 5, type=int)
    due_day =  datetime.now() + timedelta(days=due_days)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    
    # 查询借阅记录,多表联查
    borrow_records = get_borrow_info_with_book(user_id=user_id, due_day=due_day, page=page, per_page=per_page)
    # 返回借阅信息
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'books': borrow_records.get('books'),
        'total_pages': borrow_records.get('total_pages'),
        'total_items': borrow_records.get('total_items')
    })
