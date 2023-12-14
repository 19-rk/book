from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.views import views_bp
from app.views.utils import check_auth, check_missing_params, check_user_id

from app.controllers.User import add_user, get_user, update_user
from app.controllers.Admin_info import get_admin_info

# 注册
@views_bp.route('/api/user/register', methods=['POST'])
def register():
    '''
    注册必备信息包括：姓名、性别、类型、联系方式、密码, 
    余额默认、借阅数量、借阅时间默认0
    ID 由系统分配，教师 T 开头 6 位，研究生 G 开头 6 位，本科生 B 开头 10 位，其他 O 开头 10 位
    '''
    data = request.get_json()
    check_missing_params(data,['type','name','gender','contact','password'])
    # 添加用户
    try:
        user_id = add_user(   
                 name=data.get('name'),
                 gender=data.get('gender'),
                 type_=data.get('type'),
                 contact=data.get('contact'),
                 password=data.get('password'),
                 num_limit=data.get('num_limit'),
                 time_limit=data.get('time_limit'),
                 balance=data.get('balance'),
                )
        return jsonify({'code': 200, 'message': '注册成功', 'user_id': user_id})
    except Exception as e:
        print('--------Error-注册--------\n', e, '\n--------------------------')
        raise e  

        
# 登录
@views_bp.route('/api/user/login', methods=['POST'])
def login():
    '''
    登录信息: user_id、密码
    返回 token,  每次登录会更新, 需要在请求头中带上, 用于身份(user_id)验证
    '''
    print('---------',request)
    print('---------',request.get_json())
    data = request.get_json()
    check_missing_params(data,['user_id','password'])

    # 查询用户
    user = get_user(data['user_id'])
    admin = get_admin_info(data['user_id'])
    if (not user) and (not admin):
        return jsonify({'code': 400, 'message': '用户不存在'})
    
    password = user.password if user else admin.password
    
    if password != data['password']:
        return jsonify({'code': 400, 'message': '密码错误'})

    token = create_access_token(identity=data['user_id'], expires_delta=False)
    return jsonify({'code': 200, 'message': '登录成功', 'token': token})

# 获取个人信息
@views_bp.route('/api/user/getInfo', methods=['POST'])
@jwt_required()
def get_info():
    '''
    可选参数: user_id,须与登录信息一致， 管理员必选user_id
    获取名字、性别、类型、借阅数量限制、借阅时间限制、联系方式、余额
    '''
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
    except Exception as e:
        data = {}
    check_auth(user_id, admin_auth=False)
    id = check_user_id(data.get('user_id'), user_id, admin_need_user_id=True)

    user = get_user(id)
    if not user:
        return jsonify({'code': 400, 'message': '用户不存在'})
    return jsonify({'code': 200, 'message': '获取个人信息成功', 'data': {
        'user_id': user.user_id,
        'name': user.name,
        'gender': user.gender,
        'type': user.type_,
        'num_limit': user.num_limit,
        'time_limit': user.time_limit,
        'contact': user.contact,
        'balance': user.balance,
    }})
    
# 修改个人信息
@views_bp.route('/api/user/update', methods=['POST'])
@jwt_required()
def update():
    '''
    有id参数则更改对应id用户信息, 仅管理员有权限更改他人信息
    无id则更改当前用户：
        读者能更改名字、性别、联系方式
        管理员能更改名字、类型、性别、借阅数量限制、借阅时间限制、联系方式
    '''
    user_id = get_jwt_identity()
    data = request.get_json()
    # 鉴权
    check_auth(user_id, admin_auth=False)
    id = check_user_id(data.get('user_id'), user_id, admin_need_user_id=True)
     
    # 修改信息
    update_user(user_id=id,
                name=data.get('name'),
                gender=data.get('gender'),
                contact=data.get('contact'),
                type_=data.get('type') if user_id[0] == 'A' or user_id[0] == 'S' else None,
                num_limit=data.get('num_limit') if user_id[0] == 'A' or user_id[0] == 'S' else None,
                time_limit=data.get('time_limit') if user_id[0] == 'A' or user_id[0] == 'S' else None,
                balance=data.get('balance') if user_id[0] == 'A' or user_id[0] == 'S' else None
                )

    return jsonify({'code': 200, 'message': '修改成功'})

    
# 修改密码
@views_bp.route('/api/user/update_password', methods=['POST'])
@jwt_required()
def update_password():
    '''
    接收参数: 旧密码、新密码
    '''
    user_id = get_jwt_identity()
    data = request.get_json()
    check_auth(user_id, admin_auth=False)
    check_missing_params(data,['old_password','new_password'])

    # 查询用户
    user = get_user(user_id)
    if not user:
        return jsonify({'code': 400, 'message': '用户不存在'})
    # 修改密码
    if user.password != data['old_password']:
        return jsonify({'code': 400, 'message': '原密码错误'})
    try:
        update_user(user_id, password=data['new_password'])
        return jsonify({'code': 200, 'message': '修改成功'})
    except Exception as e:
        print('--------Error-修改密码--------\n', e, '\n------------------------------')
        raise e
