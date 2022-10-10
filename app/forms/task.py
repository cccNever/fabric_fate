"""
    todo:queryByModelID发送至本机服务器
"""

from wtforms import StringField, IntegerField, FileField, FloatField, FieldList 
from wtforms.validators import Length
from app.forms.base import BaseForm, DataRequired
from app.models.task import Task, MyTask, AllTask
from flask_login import current_user
from app.libs.error_code import ParameterException, Forbidden
from app import config


class ParticipantForm(BaseForm):
    modelID = StringField('modelID', validators=[DataRequired()])
    nickName = StringField('nickName', validators=[DataRequired(), Length(1, 64)])
    # participateDateTime = StringField('participateDateTime', validators=[DataRequired()])
    partyID = StringField('partyID', validators=[DataRequired()])
    trainTableName = StringField('trainTableName', validators=[DataRequired()])
    evaluateTableName = StringField('evaluateTableName', validators=[DataRequired()])

    def validate_modelID(self, field):
        task = Task.objects.filter(modelID=field.data).first()
        if task is None:
            raise ParameterException("modelID不存在")


class AssignForm(BaseForm):
    modelName = StringField('modelName', validators=[DataRequired(), Length(1, 64)])
    minPeers = IntegerField('minPeers', validators=[DataRequired()])
    timeLimit = IntegerField('timeLimit', validators=[DataRequired()], default=1209600)
    trainFile = FileField('trainFile', validators=[DataRequired()])
    evaluateFile = FileField('evaluateFile', validators=[DataRequired()])
    # partition = IntegerField('partition', validators=[DataRequired()])   # 6.6改动：删除
    description = StringField('description', validators=[DataRequired(), Length(1, 64)])
    taskName = StringField('taskName', validators=[DataRequired(), Length(1, 64)])
    modelParam = StringField('modelParam', validators=[DataRequired()])
    featureParam = StringField('featureParam', validators=[DataRequired()])


class TrainForm(BaseForm):
    modelID = StringField('modelID', validators=[DataRequired(), Length(1, 64), DataRequired(message='字段不能为空')])
    # modelAndEvaluation = StringField('modelAndEvaluation', validators=[DataRequired(), DataRequired(message='字段不能为空')])


class AcceptForm(BaseForm):
    modelID = StringField('modelID', validators=[DataRequired(), Length(1, 64), DataRequired(message='字段不能为空')])
    trainFile = FileField('trainFile', validators=[DataRequired(), DataRequired(message='文件不能为空')])
    evaluateFile = FileField('evaluateFile', validators=[DataRequired(), DataRequired(message='文件不能为空')])
    # currentNumber = StringField('currentNumber', validators=[DataRequired(), Length(1, 64), DataRequired(message='字段不能为空')])
    # partition = IntegerField('partition', validators=[DataRequired(), DataRequired(message='字段不能为空')]) # 6.6 改动：删除

    # def validate_modelID(self, field):  # 7.6 add validate number before accept
    #     task = AllTask.objects.filter(modelID=field.data, status=1).first()
    #     if task is None:
    #         raise Forbidden("任务不存在")
    #     elif config.get("mongodb", "LOCAL_PARTY_ID") == task.modelAssigner or config.get("mongodb", "LOCAL_PARTY_ID") in task.modelTrainer:
    #         raise Forbidden('任务无法接受')
    #     elif task.state !='ASSIGNED':
    #         raise Forbidden('任务无法接受')
    #     elif len(task.modelTrainer) >= task.numberOfPeers:
    #         raise Forbidden("当前任务人数已满")

    
    # # 方便前端对接accept接口,所以注释掉了,后续要放开
    # def validate_modelID(self, field):
    #     mytask = MyTask.objects.filter(nickName="current_user.nickname").first()
    #     if mytask and field.data in mytask.acceptModelList:
    #         raise Forbidden("无法再次接受该任务")

    #     task = Task.objects.filter(modelID=self.modelID.data).first()
    #     if task and task.assigner.nickName == "current_user.nickname":  # 不能接受自己发布的任务  
    #         raise Forbidden("无法参与自己发布的任务")


class PreProcessForm(BaseForm):
    csvFile = FileField('csvFile', validators=[DataRequired()])
    old_y= StringField('old_y', validators=[DataRequired(), Length(1, 64)])
    old_id= StringField('old_id',default=None)
    test_percent= FloatField('test_percent',default=0)
    split_train_num= IntegerField('split_train_num',default=1) 