"""
    time: 2022-5-23 11:04pm
    author: cpj
    update: 编写get_attrs方法
"""
import datetime
from flask_mongoengine import MongoEngine

db = MongoEngine()


class EmbedBase(db.EmbeddedDocument):
    meta = {
        'allow_inheritance': True,
        'abstract': True
    }
    # create_time = db.IntField(db_field="创建时间")
    create_time = db.DateTimeField(default=datetime.datetime.now)
    status = db.IntField(default=1)

    def soft_delete(self):
        self.status = 0

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_attrs(self):
        res = {}
        for key, value in self.__dict__:
            if key != 'id':
                res[key] = value
        return res

    def __getitem__(self, item):  # 重写， 使得对象能够像字典一样获得属性
        return getattr(self, item)


class Base(db.Document):
    meta = {
        'allow_inheritance': True,
        'abstract': True
    }
    # create_time = db.IntField(db_field="创建时间")
    create_time = db.DateTimeField(default=datetime.datetime.now)
    status = db.IntField(default=1)

    def soft_delete(self):
        self.status = 0

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'id' and key != 'captcha':
                setattr(self, key, value)

    def get_attrs(self):
        res = {}
        for key, value in self.__dict__:
            if key != 'id':
                res[key] = value
        return res

    def __getitem__(self, item):  # 重写， 使得对象能够像字典一样获得属性
        return getattr(self, item)