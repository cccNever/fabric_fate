from . import web
from app.libs.error_code import *
from app.utils.http import make_error_res
from werkzeug.exceptions import HTTPException


@web.app_errorhandler(Exception)
def framework_error(e):
    if isinstance(e, APIException):
        return e.get_body()
    if isinstance(e, HTTPException):
        code = e.code
        description = e.get_description()
        return APIException(description, code, 'HTTPException').get_body()
    else:
        return make_error_res(501, e.get_description())
