# DEBUG = False
# SERVER_NAME = "0.0.0.0"
# PORT = 88
##SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:123456@localhost:3306/fisher' ##数据库 数据库驱动 用户名 密码 IP地址 端口号 数据库
# SECRET_KEY_PATH = './jwt-key'

MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 994
MAIL_USE_SSL = True        # 写在config
MAIL_USE_TSL = False       # 写在config
MAIL_USERNAME = 'cccnever2021@163.com'
MAIL_PASSWORD = 'SBZTSAIMFEVCMXWZ'
MAIL_SUBJECT_PREFIX = '[bupt]'     # 写在config中
MAIL_SENDER = 'bupt <cccnever2021@163.com>' # 写在config中

REDIS_URL = 'redis://:12345678@10.99.12.103:6379/0' # 写在config中

SECRET_KEY = 'secret_key'
# SESSION_TYPE = 'redis'
# SESSION_REDIS = redis.Redis(host='39.105.102.235', port='6379', password='12345678')
# SESSION_KEY_PREFIX = 'flask'
# SESSION_USE_SIGNER = False
# SESSION_PERMANENT = True

REMEMBER_COOKIE_SAMESITE = 'None'
REMEMBER_COOKIE_NAME = 'user'

CELERY_BROKER_URL = 'redis://:12345678@10.99.12.103:6379/1' # 写在config中
CELERY_RESULT_BACKEND = 'redis://:12345678@10.99.12.103:6379/1' # 写在config中
