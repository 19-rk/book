from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.views import views_bp
from app.views.utils import check_auth, check_missing_params

from app.controllers.User import delete_user, get_user_by_keyword, update_user
from app.controllers.Admin_info import update_admin_info, add_admin_info, delete_admin_info, get_all_admin_info
from app.controllers.Borrow_info import get_borrow_count_byid
from app.controllers.Admin_operation_record import add_admin_operation_record

# 模糊查询用户
@views_bp.route('/api/admin/user_page', methods=['GET'])
@jwt_required()
def admin_get_users():
    '''
    可选参数: keyword, page, pageSize
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    # 获取查询参数
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    # 查询
    users = get_user_by_keyword(keyword=keyword, page=page, per_page=per_page)
    # 返回用户信息
    users_list = [ {         
                    'user_id': _.user_id,
                    'name': _.name,
                    'gender': _.gender,
                    'type': _.type_,
                    'num_limit': _.num_limit,
                    'time_limit': _.time_limit,
                    'contact': _.contact,
                    'balance': float(_.balance),
                    'count': int(get_borrow_count_byid(_.user_id))
                    
                } for _ in users.items]
    return jsonify({'code': 200, 
                    'message': '查询成功', 
                    'users': users_list, 
                    'total_pages': users.pages, 
                    'total_items': users.total
                    })

# 删除用户
@views_bp.route('/api/admin/user_delete', methods=['DELETE'])
@jwt_required()
def admin_delete_user():
    '''
    必需参数: user_id
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    data = request.get_json()
    check_missing_params(data,['user_id'])
    # 删除用户
    try:
        delete_user(data['user_id'], commit_now=False)
        add_admin_operation_record(admin_id=get_jwt_identity(), affected_user_id=data['user_id'], affected_admin_id=None, content='删除用户', reason='无', commit_now=True)
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'code': 400, 'message': '用户存在使用记录，无法删除'})

# 超级管理员添加管理员
@views_bp.route('/api/admin/admin_add', methods=['POST'])
@jwt_required()
def s_add_admin():
    '''
    必需参数: password
    ID自动分配并返回
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    if get_jwt_identity()[0] != 'S':
        return jsonify({'code': 400, 'message': '非超级管理员无权添加管理员'})
    
    data = request.get_json()
    check_missing_params(data,['password'])
    # 添加管理员
    try:
        admin_id = add_admin_info(data['password'])
        return jsonify({'code': 200, 'message': '添加成功', 'admin_id':admin_id})
    except Exception as e:
        print('--------Error-添加管理员--------\n', e, '\n------------------------------')
        raise e
    
# 超级管理员删除管理员
@views_bp.route('/api/admin/admin_delete', methods=['DELETE'])
@jwt_required()
def s_delete_admin():
    '''
    必需参数: admin_id
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    if get_jwt_identity()[0] != 'S':
        return jsonify({'code': 400, 'message': '非超级管理员无权删除管理员'})
    
    data = request.get_json()
    check_missing_params(data,['admin_id'])
    # 删除管理员
    try:
        delete_admin_info(data['admin_id'], commit_now=False)
        add_admin_operation_record(admin_id=get_jwt_identity(), affected_user_id=None, affected_admin_id=data['admin_id'], content='删除管理员', reason='无', commit_now=True)
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        print('--------Error-删除管理员--------\n', e, '\n------------------------------')
        raise e

# 超级管理员获取所有管理员信息
@views_bp.route('/api/admin/admin_page', methods=['GET'])
@jwt_required()
def s_get_admins():
    '''
    可选参数: keyword, page, pageSize
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    if get_jwt_identity()[0] != 'S':
        return jsonify({'code': 400, 'message': '非超级管理员无权获取管理员信息'})
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword', None)
    # 查询
    admins = get_all_admin_info(keyword=keyword,page=page, per_page=per_page)
    # 返回用户信息
    admins_list = [ {         
                    'admin_id': _.admin_id,
                    'password': _.password,
                } for _ in admins.items]
    return jsonify({'code': 200, 
                    'message': '查询成功', 
                    'admins': admins_list, 
                    'total_pages': admins.pages, 
                    'total_items': admins.total
                    })
    
# 超级管理员修改管理员密码
@views_bp.route('/api/admin/admin_update', methods=['POST'])
@jwt_required()
def s_update_admin():
    '''
    必需参数: admin_id, password
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    if get_jwt_identity()[0] != 'S':
        return jsonify({'code': 400, 'message': '非超级管理员无权修改管理员密码'})
    
    data = request.get_json()
    check_missing_params(data,['admin_id','password'])
    # 修改管理员密码
    try:
        update_admin_info(data['admin_id'], data['password'])
        return jsonify({'code': 200, 'message': '修改成功'})
    except Exception as e:
        print('--------Error-修改管理员密码--------\n', e, '\n------------------------------')
        raise e
    
# 管理员修改普通用户密码
@views_bp.route('/api/admin/password_update', methods=['POST'])
@jwt_required()
def admin_update_password():
    '''
    必需参数: user_id, new_password
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    data = request.get_json()
    check_missing_params(data,['user_id', 'new_password'])
    if data['user_id'][0] == 'A' or data['user_id'][0] == 'S':
        return jsonify({'code': 400, 'message': '无法修改其他管理员密码'})
    # 修改密码
    try:
        update_user(user_id=data['user_id'], password=data['new_password'])
        return jsonify({'code': 200, 'message': '修改成功'})
    except Exception as e:
        print('--------Error-修改管理员密码--------\n', e, '\n------------------------------')
        raise e