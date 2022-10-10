"""
  5.23---重写默认的WTF DataRequired, 创建application/form的base类
"""

from flask import request, current_app
from wtforms import Form
from app.libs.error_code import ParameterException
from wtforms.validators import DataRequired as WTFDataRrequired
from werkzeug.datastructures import CombinedMultiDict
import wtforms_json


class DataRequired(WTFDataRrequired):
    """
        重写默认的WTF DataRequired，实现自定义message
        DataRequired是一个比较特殊的验证器，当这个异常触发后，
        后续的验证(指的是同一个validators中的验证器将不会触发。
        但是其他验证器，比如Length就不会中断验证链条。
    """

    def __call__(self, form, field):
        if self.message is None:
            field_text = field.label.text
            self.message = field_text + '不能为空，请填写' + field_text
        super(DataRequired, self).__call__(form, field)


class JsonForm(Form):
    """
        用于json数据校验的基类
    """
    @classmethod
    def init_and_validate(cls):
        wtforms_json.init()
        form = cls.from_json(request.get_json())
        valid = form.validate()
        if not valid:
            raise ParameterException(msg=form.errors)
        return form


class BaseForm(Form):

    """
        用于form数据校验的基类
    """
    def __init__(self):
        data = CombinedMultiDict([request.form, request.files])
        # data = request.get_json()
        args = request.args.to_dict()
        super(BaseForm, self).__init__(**data, **args)

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self

