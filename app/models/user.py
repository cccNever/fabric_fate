from flask import current_app
from app.models.base import Base, db
from app.libs.error_code import CaptchaError, ParameterException, AuthFailed
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager, config
from authlib.jose import jwt, JoseError
from app.libs.get_key import get_private_key, get_pub_key
from bson.objectid import ObjectId
from flask import session
from app.utils.http import success_response


class User(UserMixin, Base):
    meta = {
        'abstract': False,
        'collection': 'user'
    }
    # id = db.IntField(primary_key=True)
    nickname = db.StringField(max_length=24, required=True)
    email = db.StringField(max_length=50, required=True)
    role = db.StringField(default='user')
    org = db.StringField(default='org1')
    img_url = db.StringField(max_lenght=200)
    _password = db.StringField(max_lenght=100, required=True)
    confirmed = db.BooleanField(default=False)
    party_id = db.StringField(default=config.get("mongodb", "LOCAL_PARTY_ID"))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    def valicate_captcha(self, captcha):
        if session.get(self.email) is None or session.get(self.email) != captcha:
            raise CaptchaError('验证码错误')
        else:
            return True

    def generate_token(self, **kwargs):
        header = {'alg': 'RS256'}
        private_key = get_private_key()
        data = {'id': str(self.id)}
        data.update(**kwargs)
        return jwt.encode(header=header, payload=data, key=private_key)

    @staticmethod
    def user_exit(email):
        user = User.objects.filter(email=email, status=1).first()
        if user is None:
            raise ParameterException('用户不存在')
        else:
            return True

    @staticmethod
    def validate_token(token):
        public_key = get_pub_key()
        try:
            data = jwt.decode(token, public_key)
        except JoseError:
            return False
        user = User.objects.get(id=data.get('id'))
        if user is None:
            return False
        user.confirmed = True
        user.save()
        return True

    @staticmethod
    def reset_password(token, new_password):
        pub_key = get_pub_key()
        try:
            data = jwt.decode(token, pub_key)
        except JoseError:
            return False
        # user = User.objects(id=data.get('id')).first()
        user = User.objects.get(id=data.get('id'))
        if user is None:
            return False
        # user.update(_password=generate_password_hash(new_password))
        user.password = new_password
        user.save()
        return True


@login_manager.user_loader
def get_user(uid):
    return User.objects.filter(id=ObjectId(uid)).first()


@login_manager.unauthorized_handler
def unauthorized():
    raise AuthFailed()

