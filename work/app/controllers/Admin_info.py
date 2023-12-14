from app.models.models import Admin_info
from app import CustomException, db

def get_admin_info(admin_id):
    # 获取管理员信息
    # admin_id: 管理员编号
    return Admin_info.query.filter_by(admin_id=admin_id).first()

def add_admin_info(password):
    # 分配管理员编号,最后一位管理员编号+1，6位
    last_admin_id = Admin_info.query.order_by(Admin_info.admin_id.desc()).filter(Admin_info.admin_id.like('A%')).first()
    admin_id = int(last_admin_id.admin_id[1:])+1 if last_admin_id else 1
    admin_id = 'A' + str(admin_id).zfill(5)

    admin_info = Admin_info(admin_id=admin_id, password=password)
    try:
        db.session.add(admin_info)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return admin_info.admin_id

def get_all_admin_info(keyword=None, page=1, per_page=10):
    # 获取管理员信息
    # admin_id: 管理员编号
    # page: 页码
    # per_page: 每页数量
    query = Admin_info.query
    if keyword:
        query = query.filter(Admin_info.admin_id.like('%' + keyword + '%'))
    return query.paginate(page=page, per_page=per_page)

def delete_admin_info(admin_id, commit_now=True):
    # 删除管理员信息
    # admin_id: 管理员编号
    # 检查管理员是否存在使用记录
    admin = Admin_info.query.filter_by(admin_id=admin_id).first()
    if not admin:
        raise CustomException('管理员不存在')
    try:
        db.session.query(Admin_info).filter(Admin_info.admin_id == admin_id).delete()
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return None

def update_admin_info(admin_id, password=None, commit_now=True):
    admin = Admin_info.query.filter_by(admin_id=admin_id).first()
    if not admin:
        raise CustomException('管理员不存在')
    admin.password = password if password else admin.password
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e