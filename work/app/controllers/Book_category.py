from app.models.models import Book_category

# class Book_category(db.Model):
#     code = db.Column('code', db.String(10), primary_key=True)
#     name = db.Column('name', db.String(100), nullable=False)
#     __table_args__ = (
#         # CheckConstraint("分类编码 LIKE '[A-Z]'", name='ck_category_code'), 不合理
#         # CheckConstraint("func.LENGTH(分类名称) > 0", name='ck_category_name')  没必要
#     )

def get_all_book_category():
    # 获取所有图书分类信息
    return Book_category.query.all()