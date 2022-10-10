from app.libs.error import APIException


class ServerError(APIException):
    code = 500
    description = 'sorry, we made a mistake (*￣︶￣)!'


class ClientTypeError(APIException):
    # 400 401 402 403 404
    # 500
    # 200 201 204
    # 301 302
    code = 400
    description = 'client is invalid'


class ParameterException(APIException):
    code = 400
    description = 'invalid parameter'


class NotFound(APIException):
    code = 404
    description = 'the resource are not found O__O...'


class AuthFailed(APIException):
    code = 401
    description = 'authorization failed'


class Forbidden(APIException):
    code = 403
    description = 'forbidden, not in scope'


class CaptchaError(APIException):
    code = 402
    description = 'captcha error'


class EmailSendError(APIException):
    code = 405
    description = '邮件发送失败'


class APIError(APIException):
    code = 4006
    description = 'API error'


class DataBaseError(APIException):
    code = 407
    description = 'database error'


class ModelStateError(APIException):
    code = 40002
    description = 'model state error'