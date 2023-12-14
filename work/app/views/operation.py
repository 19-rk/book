from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.views import views_bp
from app.views.utils import check_auth

from app.controllers.Admin_operation_record import get_admin_operation_record


# 获取重要操作记录
@views_bp.route('/api/operation/admin_record', methods=['GET'])
@jwt_required()
def get_admin_record():
    '''
    可选参数: page, pageSize, admin_id
    '''
    check_auth(get_jwt_identity(), admin_auth=True)
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    admin_id = request.args.get('admin_id', None)
    # 查询
    records = get_admin_operation_record(admin_id=admin_id, page=page, per_page=per_page)

    return jsonify({'code': 200, 
                    'message': '查询成功', 
                    'records': records['records'], 
                    'total_pages': records['total_pages'], 
                    'total_items': records['total_items']
                    })
    
# 获取重要操作记录
@views_bp.route('/api/operation/user_record', methods=['GET'])
@jwt_required()
def get_user_record():
    '''
    可选参数: page, pageSize
    '''
    user_id = get_jwt_identity()
    check_auth(user_id, admin_auth=False)
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    # 查询
    records = get_admin_operation_record(affected_user_id=user_id, page=page, per_page=per_page)

    return jsonify({'code': 200, 
                    'message': '查询成功', 
                    'records': records['records'], 
                    'total_pages': records['total_pages'], 
                    'total_items': records['total_items']
                    })