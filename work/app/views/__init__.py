from flask import Blueprint

# 创建一个 Blueprint 实例，第一个参数是 Blueprint 的名称，第二个参数是包或模块的名称
views_bp = Blueprint('views', __name__)

# 导入 views 模块中的路由处理函数
# from app.views.views import *
from app.views.book import *
from app.views.user import *
from app.views.recharge import *
from app.views.admin import *
from app.views.borrow import *
from app.views.operation import *

