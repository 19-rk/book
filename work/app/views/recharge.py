from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.views import views_bp
from app.views.utils import check_auth, check_user_id, check_missing_params

from app.controllers.Recharge_deduction_record import add_recharge_deduction_record , get_recharge_deduction_record_details
from app.controllers.User import update_user, get_user

# 查充值记录
@views_bp.route('/api/recharge/page', methods=['GET'])
@jwt_required()
def get_recharge_deduction_record_page():
    '''
    可选参数: user_id, page, pageSize
    管理员: 无user_id,查询所有用户的充值扣款记录
            有user_id,查询该用户的充值扣款记录
    普通用户只能查询自己的充值扣款记录
    '''
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=False)
    # 获取查询参数
    user_id = request.args.get('user_id', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pageSize', 10, type=int)
    
    user_id = check_user_id(user_id, get_jwt_identity())
    
    # 查询充值扣款记录
    records = get_recharge_deduction_record_details(user_id, page=page, per_page=per_page)
    return jsonify({'code': 200, 
                    'message': '查询成功', 
                    'records': records['records'], 
                    'total_pages': records['total_pages'], 
                    'total_items': records['total_items'],
                    })

# 充值扣款
@views_bp.route('/api/recharge/add', methods=['POST'])
@jwt_required()
def add_recharge_deduction_record_api():
    '''
    接收参数: user_id, value, reason(可选)
    只有管理员可以充值扣款
    '''
    # 鉴权
    check_auth(get_jwt_identity(), admin_auth=True)
    data = request.get_json()
    check_missing_params(data, ['user_id', 'value'])
    # 获取参数
    user_id = data.get('user_id')
    value = float(data.get('value'))
    reason = data.get('reason','无')
    # 添加充值扣款记录
    try:
        user = get_user(user_id)
        update_user(user_id=user_id, balance=float(user.balance)+value, commit_now=False)
        add_recharge_deduction_record(user_id, get_jwt_identity(), value, reason)
        return jsonify({'code': 200, 'message': '充值扣款成功'})
    except Exception as e:
        print('--------Error-添加充值扣款记录--------\n', e, '\n------------------------------')
        raise e
      
