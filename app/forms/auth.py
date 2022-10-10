from app.forms.base import JsonForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User
from app import redis_client


class EmailForm(JsonForm):
    email = StringField('email', validators=[DataRequired(), Length(1, 64), Email(message='邮箱格式不符合规范')])


class LoginForm(EmailForm):
    password = PasswordField('password', validators=[
        DataRequired(message='密码不可以为空，请输入你的密码')])

    def validate_email(self, field):
        user = User.objects.filter(email=self.email.data, status=1).first()
        if user is None:
            raise ValidationError('邮箱或密码错误')


class GetRegisterCaptchaForm(EmailForm):
    def validate_email(self, field):
        user = User.objects.filter(email=self.email.data, status=1).first()
        if user:
            raise ValidationError('电子邮件已被注册')


class GetResetCaptchaForm(EmailForm):
    def validate_email(self, field):
        user = User.objects.filter(email=self.email.data, status=1).first()
        if user is None:
            raise ValidationError('用户不存在，请检查您的邮箱是否正确')


class RegisterForm(GetRegisterCaptchaForm):
    nickname = StringField('nickname', validators=[DataRequired(), Length(1, 16, message='昵称长度不得超过16')])

    password = PasswordField('password', validators=[
        DataRequired(message='密码不可以为空，请输入你的密码'),
        EqualTo('checkPassword', message='两次输入的密码不相同')])
    checkPassword = PasswordField('checkPassword', validators=[
        DataRequired(), Length(6, 20)])

    captcha = StringField('captcha', validators=[DataRequired(), Length(6, 6, message='验证码错误')])

    def validate_nickname(self, field):
        user = User.objects(nickname=field.data).first()
        if user and user.status == 1:
            raise ValidationError('昵称已存在')

    def validate_captcha(self, field):
        if str(redis_client.get(self.email.data),'utf-8') is None or str(redis_client.get(self.email.data),'utf-8') != field.data.upper():
            raise ValidationError('验证码错误')


class ResetPasswordForm(GetResetCaptchaForm):
    newPassword = PasswordField('newPassword', validators=[
        DataRequired(), Length(6, 20, message='密码长度至少需要在6到20个字符之间'),
        EqualTo('newCheckPassword', message='两次输入的密码不相同')])
    newCheckPassword = PasswordField('newCheckPassword', validators=[
        DataRequired(), Length(6, 20)])
    captcha = StringField('captcha', validators=[DataRequired(), Length(6, 6, message='验证码错误')])

    def validate_captcha(self, field):
        if str(redis_client.get(self.email.data),'utf-8') is None or str(redis_client.get(self.email.data),'utf-8') != field.data.upper():
            raise ValidationError('验证码错误')


class ChangePasswordForm(JsonForm):
    old_password = PasswordField('old_password', validators=[DataRequired()])
    new_password1 = PasswordField('new_password1', validators=[
        DataRequired(), Length(6, 10, message='密码长度至少需要在6到20个字符之间'),
        EqualTo('new_password2', message='两次输入的密码不一致')])
    new_password2 = PasswordField('new_password2', validators=[DataRequired()])


class ResetUserForm(JsonForm):
    newVal = StringField('newVal', validators=[DataRequired()],default=None)