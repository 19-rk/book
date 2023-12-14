from app.models.models import Borrow_info, Book_info, Historical_borrowInfo, User
from app import CustomException, db
def add_borrow_info(book_id, user_id, borrow_date, due_date, commit_now=True):
    # 添加借阅信息
    # book_id: 图书编号
    # user_id: 用户编号
    # borrow_date: 借阅日期
    # due_date: 到期日期
    borrow = Borrow_info(book_id=book_id, user_id=user_id, borrow_date=borrow_date, due_date=due_date)
    try:
        db.session.add(borrow)
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return borrow.borrow_id

def add_history_borrow_info(book_id, user_id, borrow_date, due_date, return_date, commit_now=True):
    # 添加历史借阅信息
    # book_id: 图书编号
    # user_id: 用户编号
    # borrow_date: 借阅日期
    # due_date: 到期日期
    # return_date: 归还日期
    borrow = Historical_borrowInfo(book_id=book_id, user_id=user_id, borrow_date=borrow_date, due_date=due_date, return_date=return_date)
    try:
        db.session.add(borrow)
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return borrow.borrow_id

def delete_borrow_info_by_book(book_id, commit_now=True):
    # 删除借阅信息
    # borrow_id: 借阅编号
    # 检查借阅记录是否存在
    borrow = Borrow_info.query.filter_by(book_id=book_id).first()
    if not borrow:
        raise CustomException('借阅记录不存在')
    try:
        db.session.query(Borrow_info).filter(Borrow_info.book_id == book_id).delete()
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return None

def get_borrow_count_byid(user_id)->int:
    return Borrow_info.query.filter_by(user_id=user_id).count()

def get_borrow_info_by_book(book_id):
    return Borrow_info.query.filter_by(book_id=book_id).first()

def update_borrow_info(borrow_id, due_date=None,  commit_now=True):
    borrow = Borrow_info.query.filter_by(borrow_id=borrow_id).first()
    if not borrow:
        raise CustomException('借阅记录不存在')
    borrow.due_date = due_date if due_date else borrow.due_date
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return None

def get_borrow_info_with_book(user_id=None, due_day=None, keyword=None, page=1, per_page=10):
    # 联合查询
    # due_day代表到期天
    query = db.session.query(Borrow_info, Book_info, User.name).join(Book_info).join(User)
    if keyword != None and keyword != '':
        query = query.filter(Book_info.title.like('%'+keyword+'%')|User.name.like('%'+keyword+'%')|Borrow_info.user_id.like('%'+keyword+'%') )
    if user_id != None and user_id != '':
        query = query.filter(Borrow_info.user_id == user_id)
    if due_day != None:
        query = query.filter(Borrow_info.due_date <= due_day)
    query = query.paginate(page=page, per_page=per_page)
    return {
        'books':[{
                    'borrow_id': _.Borrow_info.borrow_id,
                    'book_id': _.Borrow_info.book_id,
                    'user_id': _.Borrow_info.user_id,
                    'name': _.name,
                    'borrow_date': _.Borrow_info.borrow_date.strftime('%Y-%m-%d'),
                    'due_date': _.Borrow_info.due_date.strftime('%Y-%m-%d'),
                    'category_code': _.Book_info.category_code,
                    'isbn': _.Book_info.isbn,
                    'title': _.Book_info.title,
                    'author': _.Book_info.author,
                    'publisher': _.Book_info.publisher,
                    'publish_date': _.Book_info.publish_date.strftime('%Y-%m-%d'),
                    'price': _.Book_info.price,
                    'intro': _.Book_info.intro,
                    'status': _.Book_info.status  
                  } for _ in query.items],
        'total_pages': query.pages,
        'total_items': query.total
    }
        
def get_history_borrow_info_with_book(user_id=None, keyword=None, page=1, per_page=10):
    # 联合查询
    query = db.session.query(Historical_borrowInfo, Book_info, User.name).join(Book_info).join(User)
    if keyword != None and keyword != '':
        query = query.filter(Book_info.title.like('%'+keyword+'%') | User.name.like('%'+keyword+'%')|Historical_borrowInfo.user_id.like('%'+keyword+'%'))
    if user_id != None and user_id != '':
        query = query.filter(Historical_borrowInfo.user_id == user_id)
    query = query.paginate(page=page, per_page=per_page)
    return {
        'books':[{
                    'borrow_id': _.Historical_borrowInfo.borrow_id,
                    'book_id': _.Historical_borrowInfo.book_id,
                    'user_id': _.Historical_borrowInfo.user_id,
                    'name': _.name,
                    'borrow_date': _.Historical_borrowInfo.borrow_date.strftime('%Y-%m-%d'),
                    'due_date': _.Historical_borrowInfo.due_date.strftime('%Y-%m-%d'),
                    'return_date': _.Historical_borrowInfo.return_date.strftime('%Y-%m-%d'),
                    'category_code': _.Book_info.category_code,
                    'isbn': _.Book_info.isbn,
                    'title': _.Book_info.title,
                    'author': _.Book_info.author,
                    'publisher': _.Book_info.publisher,
                    'publish_date': _.Book_info.publish_date.strftime('%Y-%m-%d'),
                    'price': _.Book_info.price,
                    'intro': _.Book_info.intro,
                    'status': _.Book_info.status  
                  } for _ in query.items],
        'total_pages': query.pages,
        'total_items': query.total
    }

