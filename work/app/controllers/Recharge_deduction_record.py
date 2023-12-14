# class Recharge_deduction_record(db.Model):
#     # 充值扣款记录
#     record_id = db.Column('record_id', db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column('user_id', db.String(10), nullable=False)
#     admin_id = db.Column('admin_id', db.String(20), nullable=False) 
#     value = db.Column('value', db.Numeric(10, 2), nullable=False)
#     date = db.Column('date', db.Date, nullable=False)
#     reason = db.Column('reason', db.String(100), nullable=True)
#     __table_args__ = (
#         ForeignKeyConstraint(['user_id'], ['user.user_id']),
#     )

from datetime import datetime
from app.models.models import Recharge_deduction_record
from app.models.models import User
from app import db

def add_recharge_deduction_record(user_id, admin_id, value:float, reason, commit_now=True):
    recharge_deduction_record = Recharge_deduction_record(user_id=user_id,
                                                            admin_id=admin_id,
                                                            value=value,
                                                            date=datetime.now(),
                                                            reason=reason if reason else None
                                                            )
    try:
        db.session.add(recharge_deduction_record)
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return recharge_deduction_record.record_id

def get_recharge_deduction_record_details(user_id, page=1, per_page=10):
    records = db.session.query(Recharge_deduction_record, User).join(User)
    if user_id != None and user_id != '':
        records = records.filter(Recharge_deduction_record.user_id == user_id)
    records = records.paginate(page=page, per_page=per_page)
    return {
        'records':[ { 'record_id': _.Recharge_deduction_record.record_id,
                      'user_id': _.Recharge_deduction_record.user_id,
                      'admin_id': _.Recharge_deduction_record.admin_id,
                      'value': float(_.Recharge_deduction_record.value),
                      'date': _.Recharge_deduction_record.date.strftime('%Y-%m-%d'),
                      'reason': _.Recharge_deduction_record.reason,
                      'name': _.User.name,
                      'gender': _.User.gender,
                      'type': _.User.type_,
                      'num_limit': _.User.num_limit,
                      'time_limit': _.User.time_limit,
                      'contact': _.User.contact,
                      'balance': float(_.User.balance),} 
                   for _ in records.items],
        'total_pages': records.total,
        'total_items': records.pages,
    }