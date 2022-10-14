"""
    time: 2022-5-23 11:04pm
    author: cpj
    update: 重写set_attrs方法

    time: 2022-5-24 4:01pm
    author: cpj
    update: 优化task模型类,添加EmbeddedDocument

    time: 2022-5-26 21:25
    author: lxk
    update: Participant添加trainTableName和evaluateTableName

    time: 2022-6-7 8:19 pm
    author: cpj
    update: BaseTask,AllTask
"""
import json

from app import config
from app.models.base import Base, db, EmbedBase
from datetime import datetime, timezone, timedelta


class Participant(EmbedBase):
    """
        参与者模型类
    """
    meta = {
        'abstract': True
    }
    nickName = db.StringField(max_length=50, required=True)
    participateDateTime = db.StringField(required=True, default=datetime.today().astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%dT%H:%M:%S.%f%z'))
    partyID = db.StringField(default=config.get("mongodb", "LOCAL_PARTY_ID"))
    trainTableName = db.StringField(required=True)          # 新增
    evaluateTableName = db.StringField(required=True)       # 新增


class BaseTask(Base):
    meta = {
        'abstract': True
    }
    modelID = db.StringField(max_length=50)
    state = db.StringField(default="None")
    modelName = db.StringField(max_length=50)
    timeLimit = db.IntField(default=1000)
    numberOfPeers = db.IntField(default=1)
    minPeers = db.IntField(default=0)
    taskName = db.StringField(max_length=50)


class AllTask(BaseTask):
    """
        用于存储所有任务
    """
    meta = {
        'abstract': False,
        'collection': 'all_task'
    }
    assignDateTime = db.StringField(default='')
    acceptDateTime = db.StringField(default='')
    trainDateTime = db.StringField(default='')
    finishDateTime = db.StringField(default='')
    result = db.StringField(default='')
    modelTrainer = db.ListField(db.StringField(), default=[])
    modelAssigner = db.StringField(default='')
    modelAggregator = db.StringField(default='')
    # currentNumber = db.IntField(default=0)  # 6.14 删除
    isParticipated = db.IntField(default=0)  # 6.30 add

    def set_attrs(self, attrs):
        """
        用作接受接口返回的任务列表
        :param attrs:
        :return:
        """
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
            if key == 'restrict':
                setattr(self, 'taskName', value)
            if key == 'modelTrainer':
                if value == '':
                    setattr(self, key, [])
                else:
                    value_dic = json.loads(value)
                    setattr(self, key, value_dic['modelTrainer'])

    def copy_attrs(self, obj):  # 7.6新增
        for key in obj.__dir__():
            if hasattr(self, key) and key != 'id' and key.startswith('_') is False:
                setattr(self, key, getattr(obj, key))


class Task(BaseTask):
    meta = {
        'abstract': False,
        'collection': 'assigned_model'
    }
    description = db.StringField(max_length=50, required=True)
    assigner = db.EmbeddedDocumentField(Participant)
    acceptors = db.ListField(db.EmbeddedDocumentField(
        Participant))
    assignDateTime = db.StringField(required=True)
    modelParam = db.StringField()
    featureParam = db.StringField()
    labelName = db.StringField()
    featureNames = db.ListField(db.StringField(max_length=50))

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'acceptors':
                setattr(self, key, value)
            if key == 'acceptors':
                self.acceptors.append(value)


class MyTask(Base):
    meta = {
        'abstract': False,
        'collection': 'user_model'
    }
    # nickname、modelID、assigner_partyID、role
    nickName = db.StringField(max_length=50, required=True)
    assignModelList = db.ListField(db.StringField(max_length=50))
    acceptModelList = db.ListField(db.StringField(max_length=50))

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'assignModelList' and key != 'acceptModelList':
                setattr(self, key, value)
            if key == 'assignModelList':
                self.assignModelList.append(value)
            if key == 'acceptModelList':
                self.acceptModelList.append(value)


class SimpleParticipant(EmbedBase):
    """
        参与者模型类
    """
    meta = {
        'abstract': True
    }
    nickName = db.StringField(max_length=50, required=True)
    role = db.StringField(max_length=50, required=True)


class SimpleTask(Base):
    meta = {
        'abstract': False,
        'collection': 'simple_model'
    }
    # nickname、modelID、assigner_partyID、role
    nickName = db.StringField(max_length=50, required=True)
    modelID = db.StringField(max_length=50, required=True)
    assignerPartyID = db.StringField(max_length=50, required=True)
    users = db.ListField(db.EmbeddedDocumentField(SimpleParticipant))

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'users':
                setattr(self, key, value)
            if key == 'users':
                self.users.append(value)


class ModelResult(Base):
    meta = {
        'abstract': False,
        'collection': 'model_result'
    }
    modelID = db.StringField(max_length=50, required=True)
    modelResult = db.StringField(required=True)