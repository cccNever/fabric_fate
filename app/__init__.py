from flask import Flask


def create_app():
    """
    创建app对象
    :return: void
    """
    app = Flask(__name__)
    # app.config.from_object('app.secure')
    # app.config.from_object('app.setting')
    register_blueprint(app)
    # db.init_app(app)
    # db.create_all(app=app)
    return app


def register_blueprint(app):
    """
    将蓝图注册到app对象中
    :param app: app对象
    :return: void
    """
    from app.web.user import web
    app.register_blueprint(web)
