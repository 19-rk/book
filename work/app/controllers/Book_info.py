from app.models.models import Book_info, Borrow_info, Historical_borrowInfo
from app.models.models import Book_category
from app import CustomException, db


def add_book_info(category_code, isbn, title, author, publisher, publish_date, price, intro, status='在馆', commit_now=True):
    # 添加图书信息
    # category_code: 图书分类编码
    # isbn: ISBN
    # title: 书名
    # author: 作者
    # publisher: 出版社
    # publish_date: 出版日期
    # price: 价格
    # intro: 简介
    # status: 状态
    book = Book_info(category_code=category_code, isbn=isbn, title=title, author=author, publisher=publisher, publish_date=publish_date, price=price, intro=intro, status=status)
    try:
        db.session.add(book)
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return book.book_id

def delete_book_info(book_id, commit_now=True):
    # 删除图书信息
    # book_id: 图书编号
    # 检查图书是否在馆
    book = Book_info.query.filter_by(book_id=book_id).first()
    if not book:
        raise CustomException('图书不存在')
    if book.status != '在馆':
        raise CustomException('图书'+book.status+'，无法删除')
    try:
        db.session.query(Book_info).filter(Book_info.book_id == book_id).delete()
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return None

def get_book_info(book_id):
    # book_id: 图书编号
    book = Book_info.query.filter_by(book_id=book_id).first()
    if not book:
        raise CustomException('图书不存在')
    return  {
        'book_id': book.book_id,
        'category_code': book.category_code,
        'isbn': book.isbn,
        'title': book.title, 
        'author': book.author, 
        'publisher': book.publisher,
        'publish_date': book.publish_date.strftime('%Y-%m-%d'),
        'price': book.price,
        'intro': book.intro,
        'status': book.status
    }


def get_book_info_by_keyword(keyword='', page=1, per_page=10):
    if keyword == None:
        keyword = ''
        
    query = db.session.query(Book_info, Book_category).join(Book_category, Book_info.category_code == Book_category.code)
    query = query.filter(Book_info.status != '下架')
    books = query.filter(Book_info.title.like('%' + keyword + '%') |
                         Book_info.author.like('%' + keyword + '%')|
                         Book_info.publisher.like('%' + keyword + '%') |
                         (Book_info.isbn == keyword) |
                         (Book_info.status == keyword) |
                         (Book_category.code == keyword) |
                         (Book_category.name == keyword)
                         ).paginate(page=page, per_page=per_page)
    return {
        'books': [ { 'book_id': _.book_id,
                    'category_code': _.category_code,
                    'category_name': category.name, # 'category_name': '计算机
                    'isbn': _.isbn,
                    'title': _.title, 
                    'author': _.author, 
                    'publisher': _.publisher,
                    'publish_date': _.publish_date.strftime('%Y-%m-%d'),
                    'price': _.price,
                    'intro': _.intro,
                    'status': _.status
                   } for _, category in books.items],
        'total_pages': books.pages,
        'total_items': books.total
    }



def update_book_info(book_id, category_code=None, isbn=None, title=None, author=None, publisher=None, publish_date=None, price=None, intro=None, status=None, commit_now=True):
    # 修改图书信息
    # book_id: 图书编号
    # category_code: 图书分类编码
    # isbn: ISBN
    # title: 书名
    # author: 作者
    # publisher: 出版社
    # publish_date: 出版日期
    # price: 价格
    # intro: 简介
    # status: 状态
    book = Book_info.query.filter_by(book_id=book_id).first()
    if not book:
        raise CustomException('图书不存在')
    book.category_code = category_code if category_code else book.category_code
    book.isbn = isbn if isbn else book.isbn
    book.title = title if title else book.title
    book.author = author if author else book.author
    book.publisher = publisher if publisher else book.publisher
    book.publish_date = publish_date if publish_date else book.publish_date
    book.price = price if price else book.price
    book.intro = intro if intro else book.intro
    book.status = status if status else book.status
    try:
        if commit_now:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    
# 获取借阅数量+历史借阅数量排名前n的图书
def get_top_book_info(n=10):

    borrow_count = db.session.query(Borrow_info.book_id, db.func.count(Borrow_info.book_id).label('count')).group_by(Borrow_info.book_id).subquery()
    historical_borrow_count = db.session.query(Historical_borrowInfo.book_id, db.func.count(Historical_borrowInfo.book_id).label('count')).group_by(Historical_borrowInfo.book_id).subquery()

    top_book = db.session.query(
    Book_info,
    db.func.coalesce(borrow_count.c.count, 0).label('borrow_count'),
    db.func.coalesce(historical_borrow_count.c.count, 0).label('historical_borrow_count'),
    (db.func.coalesce(borrow_count.c.count, 0) + db.func.coalesce(historical_borrow_count.c.count, 0)).label('all_count')
    ).outerjoin(
        borrow_count, Book_info.book_id == borrow_count.c.book_id
    ).outerjoin(
        historical_borrow_count, Book_info.book_id == historical_borrow_count.c.book_id
    ).order_by(
        (db.func.coalesce(borrow_count.c.count, 0) + db.func.coalesce(historical_borrow_count.c.count, 0)).desc()
    ).limit(n).all()
    
    return [
        {
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'publish_date': book.publish_date.strftime('%Y-%m-%d'),
            'price': book.price,
            'intro': book.intro,
            'borrow_count': borrow_count,
            'historical_borrow_count': historical_borrow_count,
            'all_count': all_count
        } for book, borrow_count, historical_borrow_count, all_count in top_book
    ]