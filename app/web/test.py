from . import web
from flask import current_app
import os


@web.route('/v1/task/test4', methods=['POST', 'OPTIONS'])
def test():
    dir = os.path.dirname(__file__)
    redis = current_app.config['REDIS_URL']
    ip = os.getenv('SERVER_IP')
    res = {
        "1": dir,
        "2": redis,
        "3": ip
    }
    return res
