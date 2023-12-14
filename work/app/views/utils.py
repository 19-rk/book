from app import CustomException

# 检查缺少的参数
def check_missing_params(data, params):
    '''
    Get the missing parameters from the given data.
    Return None if all parameters are provided, otherwise return a json object.
    '''
    res = [param for param in params if not data.get(param)]
    if len(res) > 0:
        raise CustomException('缺少必要参数: ' + ', '.join(res))
        # return jsonify({'code': 400, 'message': '缺少必要参数: ' + ', '.join(res)})
    # return None

# 鉴权
def check_auth(user_id, admin_auth=False):
    '''
    check if the user is logged in and has the permission to access the resource
    return None if the user is logged in and has the permission to access the resource
    '''
    if not user_id:
        raise CustomException('未登录')
        # return jsonify({'code': 500, 'message': '未登录'})
    if admin_auth and (user_id[0] != 'A' and user_id[0] != 'S'):
        raise CustomException('无权限')
        # return jsonify({'code': 500, 'message': '无权限'})
    # return None
    
# 检查user_id和登录信息是否匹配，普通用户必须匹配或没有user_id参数，管理员可选择user_id
def check_user_id(user_id_in_params, user_id_in_jwt, admin_need_user_id=False, allow_return_admin_none=True, allow_return_user_none=False):
    '''
    admin_need_user_id: 管理员是否需要指定user_id
    allow_return_admin_none: 允许管理员返回None, 即可以查询所有用户
    allow_return_user_none: 允许普通用户返回None, 即可以查询所有的信息
    '''
    if user_id_in_params == '':
        user_id_in_params = None
    
    is_admin = user_id_in_jwt[0] == 'A' or user_id_in_jwt[0] == 'S'
    if is_admin and admin_need_user_id and not user_id_in_params:
        raise CustomException('管理员需要指定 user_id')
    if (not is_admin) and user_id_in_params and user_id_in_params != user_id_in_jwt:
        raise CustomException('您无权获取他人信息')
    
    if user_id_in_params:
        return user_id_in_params
    if is_admin and allow_return_admin_none:
        return user_id_in_params
    if (not is_admin) and allow_return_user_none:
        return user_id_in_params
    
    return user_id_in_jwt
    