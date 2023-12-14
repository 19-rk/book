from app import db
from sqlalchemy import func, CheckConstraint, ForeignKeyConstraint

class User(db.Model):
    # user_id = db.Column('user_id', db.BigInteger, primary_key=True)
    user_id = db.Column('user_id', db.String(10), primary_key=True)
    name = db.Column('name', db.String(20), nullable=False)
    gender = db.Column('gender', db.String(1), nullable=False)
    type_ = db.Column('type', db.String(3), nullable=False)
    num_limit = db.Column('num_limit', db.SmallInteger, nullable=True)
    time_limit = db.Column('time_limit', db.SmallInteger, nullable=True)
    contact = db.Column('contact', db.String(20), nullable=False)
    balance = db.Column('balance', db.Numeric(10, 2), nullable=False)
    password = db.Column('password', db.String(20), nullable=True)
    __table_args__ = (
        # 读者编号长度约束
        CheckConstraint(func.LENGTH('user_id').in_([6, 10]), name='ck_user_id_length'),
        # 性别约束
        CheckConstraint("gender IN ('男','女')", name='ck_gender'),
        # 读者类型约束
        CheckConstraint("type IN ('教师','研究生','本科生','其他')", name='ck_type'),
        # 余额非负约束
        CheckConstraint("balance >= 0", name='ck_balance_positive'),
        # 密码长度约束
        CheckConstraint(func.LENGTH('password') >= 8, name='ck_password_length_min'),
        CheckConstraint(func.LENGTH('password') <= 20, name='ck_password_length_max'),
        # 读者类型与编号长度的联合约束
        CheckConstraint("type = '教师' AND func.LENGTH(user_id) = 6 OR "
                        "type = '研究生' AND func.LENGTH(user_id) = 6 OR "
                        "type = '本科生' AND func.LENGTH(user_id) = 10 OR "
                        "type = '其他' AND func.LENGTH(user_id) = 10", name='ck_type_and_id_length')
    )

class Book_category(db.Model):
    code = db.Column('code', db.String(10), primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    __table_args__ = (
        # CheckConstraint("分类编码 LIKE '[A-Z]'", name='ck_category_code'), 不合理
        # CheckConstraint("func.LENGTH(分类名称) > 0", name='ck_category_name')  没必要
    )

class Book_info(db.Model):
    book_id = db.Column('book_id', db.Integer, primary_key=True, autoincrement=True)
    category_code = db.Column('category_code', db.String(10), nullable=False)
    isbn = db.Column('isbn', db.BigInteger, nullable=False)
    title = db.Column('title', db.String(50), nullable=False)
    author = db.Column('author', db.String(20), nullable=False)
    publisher = db.Column('publisher', db.String(20), nullable=False)
    publish_date = db.Column('publish_date', db.Date)
    price = db.Column('price', db.Numeric(10, 2), nullable=False)
    intro = db.Column('intro', db.String(100))
    status = db.Column('status', db.String(2), nullable=False, default='在馆')
    __table_args__ = (
        CheckConstraint('func.LENGTH(ISBN) IN (10, 13)', name='ck_isbn_length'),
        CheckConstraint('price >= 0', name='ck_price_positive'),
        CheckConstraint("status IN ('在馆', '借出', '丢失', '损坏', '下架')", name='ck_status'),
        ForeignKeyConstraint(['category_code'], ['book_category.code']),
    )

class Borrow_info(db.Model):
    borrow_id = db.Column('borrow_id', db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column('book_id', db.Integer, nullable=False)
    # isbn = db.Column('isbn', db.BigInteger, nullable=False) 冗余信息，不符合范式要求
    user_id = db.Column('user_id', db.String(10), nullable=False)
    borrow_date = db.Column('borrow_date', db.Date, nullable=False)
    due_date = db.Column('due_date', db.Date, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['book_id'], ['book_info.book_id']),
        ForeignKeyConstraint(['user_id'], ['user.user_id']),
    )

class Historical_borrowInfo(db.Model):
    borrow_id = db.Column('borrow_id', db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column('book_id', db.Integer, nullable=False)
    # isbn = db.Column('isbn', db.BigInteger, nullable=False) 冗余信息，不符合范式要求
    user_id = db.Column('user_id', db.String(10), nullable=False)
    borrow_date = db.Column('borrow_date', db.Date, nullable=False)
    due_date = db.Column('due_date', db.Date, nullable=True)
    return_date = db.Column('return_date', db.Date, nullable=False)
    __table_args__ = (
        # CheckConstraint('return_date>=due_date', name='ck_actual_return_date'), 不合理，存在逾期情况
        ForeignKeyConstraint(['book_id'], ['book_info.book_id']),
        ForeignKeyConstraint(['user_id'], ['user.user_id']),
    )

class Admin_info(db.Model):
    # admin_id = db.Column('admin_id', db.Integer, primary_key=True)
    # admin_account = db.Column('admin_account', db.String(20), nullable=False)
    admin_id = db.Column('admin_id', db.String(20), primary_key=True)
    password = db.Column('password', db.String(20), nullable=False)
    __table_args__ = (
        CheckConstraint('func.LENGTH(password) >= 5 AND func.LENGTH(password) <= 20', name='ck_password_length'),
        CheckConstraint('func.LENGTH(admin_id) > 0', name='ck_admin_id_length'),
    )

class Recharge_deduction_record(db.Model):
    # 充值扣款记录
    record_id = db.Column('record_id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('user_id', db.String(10), nullable=False)
    admin_id = db.Column('admin_id', db.String(20), nullable=False) 
    value = db.Column('value', db.Numeric(10, 2), nullable=False)
    date = db.Column('date', db.Date, nullable=False)
    reason = db.Column('reason', db.String(100), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.user_id']),
    )

class Admin_operation_record(db.Model):
    # 管理员操作记录
    record_id = db.Column('record_id', db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column('admin_id', db.String(20), nullable=False)
    affected_user_id = db.Column('affected_user_id', db.String(10), nullable=True)
    affected_admin_id = db.Column('affected_admin_id', db.String(20), nullable=True)
    date_time = db.Column('date_time', db.DateTime, nullable=False)
    content = db.Column('content', db.String(50), nullable=False)
    reason = db.Column('reason', db.String(100), nullable=False)
    __table_args__ = (
        CheckConstraint('func.LENGTH(content) > 0', name='ck_operation_content_length'),
        CheckConstraint('func.LENGTH(reason) > 0', name='ck_operation_reason_length'),
        ForeignKeyConstraint(['admin_id'], ['admin_info.admin_id']),
        ForeignKeyConstraint(['affected_user_id'], ['user.user_id']),
        ForeignKeyConstraint(['affected_admin_id'], ['admin_info.admin_id']),
    )
