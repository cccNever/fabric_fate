import uuid

from flask import make_response, redirect, render_template, url_for, session
from flask import request, current_app
from flask_login import login_user, login_required, current_user,logout_user

from . import web
from app.forms.auth import RegisterForm, LoginForm, EmailForm, ResetPasswordForm, ChangePasswordForm, GetResetCaptchaForm, GetRegisterCaptchaForm,ResetUserForm
from app.models.user import User
from app.utils.http import success_response,mail_response, user_data
from app.libs.error_code import AuthFailed
from app.libs.error_code import ParameterException
from app import redis_client


@web.route('/api/user/state')
@login_required
def state():
    user = User.objects.filter(email=current_user.email, status=1).first()
    if user:
        return success_response(user_data(user))
    else:
        return success_response()


@web.route('/api/auth/login', methods=['POST', 'GET', 'OPTIONS'])
def login():
    form = LoginForm.init_and_validate()
    if form.validate():
        user = User.objects.filter(email=form.email.data, status=1).first()
        if user and user.status == 1 and user.check_password(form.password.data) and user.confirmed:
            login_user(user, remember=False)
            current_app.logger.info('【login】:'+form.email.data)
            # current_app.logger.info(session.get('session'))
            # data['session'] = session.get('session')
            return success_response(user_data(user))
        else:
            raise ParameterException({'email': '邮箱或密码错误'})


@web.route('/api/auth/logout', methods=['POST', 'GET', 'OPTIONS'])
def logout():
    logout_user()
    return success_response()


@web.route('/api/auth/register/code', methods=['POST', 'OPTIONS'])
def get_register_code():
    form = GetRegisterCaptchaForm.init_and_validate()
    if form.validate:
        captcha = str(uuid.uuid1())[:6].upper()
        from app.libs.email import send_mail
        send_mail(form.email.data, '发来的验证码',
                  'email/captcha.html', person=form.email.data, captcha=captcha, operation='注册')
        redis_client.set(form.email.data, captcha)
        return mail_response()


@web.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register_by_code():
    form = RegisterForm.init_and_validate()
    if form.validate:
        # if User.user_exit(form.email.data):
        user = User()
        user.set_attrs(form.data)
        # if user.valicate_captcha(form.captcha.data.upper()):
        user.confirmed = True
        user.save()
        return success_response()


@web.route('/api/forget/password/code', methods=['POST', 'OPTIONS'])
def get_reset_code():
    form = GetResetCaptchaForm.init_and_validate()
    if form.validate:
        user = User.objects.filter(email=form.email.data, status=1).first()
        captcha = str(uuid.uuid1())[:6].upper()
        from app.libs.email import send_mail
        send_mail(form.email.data, '发来的验证码',
                  'email/captcha.html', person=user.nickname, captcha=captcha, operation='重置密码')
        redis_client.set(form.email.data, captcha)
        return mail_response()


@web.route('/api/forget/password', methods=['POST', 'OPTIONS'])
def reset_password():
    form = ResetPasswordForm.init_and_validate()
    if form.validate():
        user = User.objects.get(email=form.email.data, status=1)
        user.password = form.newPassword.data
        user.save()
        return success_response()


# 以下是token方式
@web.route('/api/auth/register/token', methods=['POST'])
def register():
    form = RegisterForm.init_and_validate()
    if form.validate():
        user = User()
        user.set_attrs(form.data)
        user.save()
        token = user.generate_token()
        from app.libs.email import send_mail
        send_mail(user.email, 'Confirm Your Account',
                  'email/confirm.html', user=user, token=token)
        return mail_response()


# 用于注册验证，需要发送注册验证页面需要前端人员写，email/confirm.html的href需要更改为注册验证页面的url
@web.route('/api/auth/confirm/<token>', methods=['POST'])
def register_confirm(token):
    confirm = User.validate_token(token)
    if confirm:
        return success_response()
    else:
        # return redirect(url_for('web.index'))
        return make_res('AuthError', '', 0, '')


@web.route('/api/reset/password', methods=['POST'])
def forget_password_request():
    form = EmailForm.init_and_validate()
    if form.validate():
        account_email = form.email.data
        user = User.objects(email=account_email).first_or_404()
        from app.libs.email import send_mail
        send_mail(form.email.data, '重置你的密码', 'email/reset_password.html', user=user, token=user.generate_token())
        return mail_response()


# 用于重置密码验证，重置密码页面需要前端人员写
@web.route('/api/reset/password/<token>', methods=['POST'])
def forget_password(token):
    form = ResetPasswordForm.init_and_validate()
    if form.validate():
        result = User.reset_password(token, form.newPassword.data)
        if result:
            # flash('你的密码已更新,请使用新密码登录')
            # return redirect(url_for('web.login'))
            return success_response()
        else:
            # return redirect(url_for('web.index'))
            # return make_res('AuthError', '', 0, "password reset response body")
            raise AuthFailed()


@web.route('/api/change/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm.init_and_validate()
    if request.method == 'POST' and form.validate():
        current_user.password = form.new_newPassword.data
        current_user.save()
        return redirect(url_for('web.personal'))
    return render_template('auth/change_password.html', form=form)


@web.route('/api/set/cookie')
def get_cookie():
    response = make_response('hello mr.7')
    response.set_cookie('name', 'mr.7', 100)
    return response


@web.route('/api/user/reset', methods=['POST'])
@login_required
def reset_user():
    target = request.args.get('target')
    form = ResetUserForm.init_and_validate()
    if request.method == 'POST' and form.validate():
        if target == "nickname":
            current_user.nickname=form.newVal.data
        elif target == "email":
            current_user.email=form.newVal.data
        current_user.save()
    return success_response()
