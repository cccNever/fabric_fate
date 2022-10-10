from flask import Flask
from app.models.base import db
from flask_login import LoginManager
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_cors import CORS
from flask_apscheduler import APScheduler
import logging
from logging.handlers import TimedRotatingFileHandler
import configparser
from celery import Celery
from app.config import setting

logging.basicConfig(level=logging.NOTSET)
filehandler = TimedRotatingFileHandler("flask.log", "M", 1, 0)

logging.getLogger().addHandler(filehandler)
login_manager = LoginManager()
mail = Mail()
redis_client = FlaskRedis()

scheduler = APScheduler()

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")


def create_app():
    """
    创建app对象
    :return: void
    """

    app = Flask(__name__,  static_folder='statics', static_url_path="/statics", template_folder='templates')
    CORS(app, supports_credentials=True)
    # app.config.from_object('app.secure')
    app.config.from_object(setting['development'])
    # app.config.from_object('app.setting')
    app.config.from_mapping(
        MONGODB_SETTINGS={
            'db': 'fabric_fatedb',
            'host': '10.99.12.103',
            'port': 27019,
            'connect': True,
            'username': 'fabric_fatedb_admin',
            'password': '123123',
            'authentication_source': 'fabric_fatedb'
        }
    )
    register_blueprint(app)

    redis_client.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message = '请先登录和注册'

    mail.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    return app


def register_blueprint(app):
    """
    将蓝图注册到app对象中
    :param app: app对象
    :return: void
    """
    from app.web import web
    app.register_blueprint(web)


def make_celery_app(app=None):
    app = Flask(__name__)
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery

