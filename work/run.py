'''
前后端传输密码时需要将密码明文加密
数据库中存储的密码也需要加密
这里仅用作开发环境测试, 代码未有上述加密操作。
'''
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)

