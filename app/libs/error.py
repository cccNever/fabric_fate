from flask import request, json, jsonify
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    code = 500
    description = 'Sorry, we make a mistake!'
    msg = 'APIException'
    data = ''

    def __init__(self, msg=None, description=None, code=None,  data=None, headers=None):
        if code:
            self.code = code
        if description:
            self.description = description
        if msg:
            self.msg = msg
        if data:
            self.data = data
        super(APIException, self).__init__(description, None)

    def get_body(self, environ=None):
        body = dict(
            code=self.code,
            data=self.data,
            description=self.description,
            msg=self.msg,
            request=request.method + ' ' + self.get_url_no_param()
        )
        return jsonify(body)

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]




