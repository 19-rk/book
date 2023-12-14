'''
这里参数应该从环境变量中获取或者以更安全的方式保存，这里为了方便直接写死
'''
# 云数据库连接信息，需要根据实际情况修改
USERNAME = 'test1'
PASSWORD = '1724641846qq.com'
HOSTNAME = 'sh-cynosdbmysql-grp-8xgy3bx0.sql.tencentcdb.com:23626'
DATABASE = 'test'
# JWT 密钥，用于加密 token，这里为了方便随意设置
JWT_SECRET_KEY = '2￥……&Ldm21%*&@LM#(*F?##FMASKMCWIAH@>?$%@#%)+_mlkhjonl'


from datetime import timedelta

class Config:
    JWT_SECRET_KEY = JWT_SECRET_KEY  
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(USERNAME, PASSWORD, HOSTNAME, DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DELTA = timedelta(days=1)
    
