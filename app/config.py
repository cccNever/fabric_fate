import os


class BaseConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "dev key")

    LOCAL_PARTY_ID = os.getenv("LOCAL_PARTY_ID")
    LOCAL_IP = "http://" + os.getenv("SERVER_IP") + ":" + os.getenv("FLASK_PORT") + "/"
    LOCAL_FATE_IP = "http://" + os.getenv("SERVER_IP") + ":" + os.getenv("FATE_PORT") + "/"

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_SSL = True
    MAIL_USE_TSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("SBZTSAIMFEVCMXWZ")
    MAIL_SUBJECT_PREFIX = '[bupt]'  # 写在config中
    MAIL_SENDER = 'bupt <cccnever2021@163.com>'  # 写在config中

    REDIS_URL = 'redis://:' + os.getenv("PASSWORD") + '@' + os.getenv("SERVER_IP") + ":" + os.getenv("REDIS_PORT") + "/0"

    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_NAME = 'user'

    CELERY_BROKER_URL = 'redis://:' + os.getenv("PASSWORD") + '@' + os.getenv("SERVER_IP") + ":" + os.getenv("REDIS_PORT") + "/1"
    CELERY_RESULT_BACKEND = 'redis://:' + os.getenv("PASSWORD") + '@' + os.getenv("SERVER_IP") + ":" + os.getenv("REDIS_PORT") + "/1"

    # 供celery操作的mongo用户
    CELERY_MONGO_URI = "mongodb://user_ffb:123123@10.99.12.103:27019/fabric_fatedb"

    # 用于flask容器中保存用户上传的数据
    UPLOAD_FOLDER_ASSIGN = './data/assign/'
    UPLOAD_FOLDER_ACCEPT = './data/accept/'
    DOWNLOAD_FOLDER_RESULT_MODEL = './data/modelResult/'
    DOWNLOAD_FOLDER_RESULT_DATA = './data/dataResult/'
    UPLOAD_FOLDER_PREPROCESS_CSV = './data/preprocessCSV/'

    # 用于fabric-app 容器中保存用户上传的数据
    BASE_UPLOAD_FOLDER = os.getenv("BASE_UPLOAD_FOLDER")
    # 用于定时
    SCHEDULER_API_ENABLED = True



class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


setting = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
