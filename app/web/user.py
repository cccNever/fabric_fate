from . import web


@web.route('/user/login')
def login():
    return 'hello'


@web.route('/user/register')
def register():
    pass
