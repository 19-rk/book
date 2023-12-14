from datetime import datetime
from app.models.models import Admin_operation_record
from app.models.models import Admin_info
from app.models.models import User

from  app import db

def add_admin_operation_record(admin_id, affected_user_id, affected_admin_id, content, reason, commit_now=True):
    # 添加管理员操作记录
    # admin_id: 操作管理员的管理员号
    # affected_user_id: 受影响的用户的用户号
    # affected_admin_id: 受影响的管理员的管理员号
    # content: 操作内容
    # reason: 操作原因
    record = Admin_operation_record(admin_id=admin_id, 
                                    affected_user_id=affected_user_id, 
                                    affected_admin_id=affected_admin_id,
                                    date_time = datetime.now(), 
                                    content=content, 
                                    reason=reason)
    try:
        db.session.add(record)
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return record.record_id

def get_admin_operation_record(record_id=None, admin_id=None, affected_user_id=None, affected_admin_id=None, page=1, per_page=10):
    # 获取管理员操作记录
    # record_id: 操作记录号
    # admin_id: 操作管理员的管理员号
    # affected_user_id: 受影响的用户的用户号
    # affected_admin_id: 受影响的管理员的管理员号
    # page: 页码
    # per_page: 每页数量
    query = Admin_operation_record.query
    if record_id:
        query = query.filter_by(record_id=record_id)
    if admin_id:
        query = query.filter_by(admin_id=admin_id)
    if affected_user_id:
        query = query.filter_by(affected_user_id=affected_user_id)
    if affected_admin_id:
        query = query.filter_by(affected_admin_id=affected_admin_id)

    query = query.paginate(page=page, per_page=per_page)
    
    return {
        'records':[ {         
                    'record_id': _.record_id,
                    'admin_id': _.admin_id,
                    'affected_admin_id': _.affected_admin_id,
                    'affected_user_id': _.affected_user_id,
                    'date_time': _.date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': _.content,
                    'reason': _.reason,
                } for _ in query.items],
        'total_pages': query.pages, 
        'total_items': query.total
        
        
    }