"""
    time: 2022-5-24 11:02am
    author: lxk
    accept之后将acceptor写入mongo对应task
    accept之后调服务器接口更新assigner所在服务器的详细表,更新本地服务器的简单表:nickname、modelID、assigner_partyID、role
    调assign所在服务器的接口,更新mongo
    todo:
    加判断nickname,不能自己assign自己accept
"""

import os
import json
from werkzeug.utils import secure_filename

from app.utils.task import get_server_by_partyID, save_files

from . import web
from flask import current_app, request
from flask_login import login_required, current_user
from app.forms.task import AcceptForm
from app.models.task import Task, Participant, MyTask, AllTask
from app.viewmodels.task_res import accept_data
from app.utils.oshelper import delete_head, is_json
from app.utils.http import success_response, post_form
from app.libs.error_code import Forbidden
from mongoengine.queryset.visitor import Q


@web.route('/api/task/accept_test', methods=['POST'])
@login_required
def accept_test():
    """
    form需要传的:
    modelID : assign后返回的modelID
    trainFile:训练数据文件
    evalueFile:验证数据文件
    """
    form = AcceptForm()
    # current_app.logger.info(form.data)
    if form.validate_for_api():

        # '''调103:8010/queryByModelID接口获取该model的相关信息,用来判断人数超了没，时间超了没'''

        # queryByModelID_api = 'http://10.99.12.{}:8010/queryByModelID'.format('103')
        # modelID=form.modelID.data
        # data = {"modelID": modelID}
        # res = post_form(queryByModelID_api, data=data)
        # res_str = res.content.decode()
        # res_json = json.loads(res_str)
        # num = str(len(res_json) - 1)
        # record = json.loads(res_json[num])  # 最新一条记录


        '''调用accept接口接收任务'''

        # 获取并存储traindata和evaluatedata文件
        os.makedirs('./data/accept', exist_ok=True)
        # 首先删除上次保存的用户文件
        delete_head("data/accept/user")
        train_file = form.trainFile.data
        evaluate_file = form.evaluateFile.data
        save_files("accept", train_file, evaluate_file)

        accept_api = 'http://10.99.12.{}:8010/accept'.format('103')
        modelTrainer = current_app.config["LOCAL_PARTY_ID"]
        base_path = current_app.config['BASE_UPLOAD_FOLDER'] + "accept/"
        # current_app.logger.info("【type】")
        # current_app.logger.info(type(current_app.config['BASE_UPLOAD_FOLDER']))
        # current_app.logger.info(base_path)
        trainDataConf = {
            "head": 1,  # 指定数据文件是否包含表头
            "drop": 1,
            "partition": 5,  # 指定用于存储数据的分区数
            "file": base_path + "user__" + current_user.nickname + "_" + train_file.filename,
            "namespace": "experiments",  # 存储数据表的标识符号
            "table_name": os.path.splitext(train_file.filename)[0]  # 存储数据表的标识符号
        }
        evaluateDataConf = {
            "head": 1,
            "drop": 1,
            "partition": 5,  
            "file": base_path + "user__" + current_user.nickname + "_" + evaluate_file.filename,
            "namespace": "experiments",
            "table_name": os.path.splitext(evaluate_file.filename)[0]
        }
        # current_app.logger.info("【trainDataConf】")
        # current_app.logger.info(trainDataConf)
        data = {
            "modelID": form.modelID.data,
            "modelTrainer": modelTrainer,
            "trainDataConf": str(trainDataConf).replace("'", '"'),
            "evaluateDataConf": str(evaluateDataConf).replace("'", '"'),
        }
        # current_app.logger.info(str(data))
        res = post_form(accept_api, data=data)  # 类型：response类
        content_str = res.content.decode()
        while content_str=="Connection Failed!":
            res = post_form(accept_api, data=data)  # 类型：response类
            content_str = res.content.decode()
        current_app.logger.info("【Accept的返回:】" + content_str)
        if is_json(content_str):
            jsonRes = json.loads(content_str)

            '''更新assign-model表中的task对象'''

            task = Task.objects.filter(modelID=form.modelID.data).first()
            if task:  # 本地服务器有这个task的相关记录（assigner是本地服务器）
                par_attrs = {
                    "nickName": current_user.nickname,
                    # "participateDateTime": jsonRes['acceptDateTime'], # 6.8 删除
                    "partyID": modelTrainer,
                    "trainTableName": trainDataConf['table_name'],
                    "evaluateTableName": evaluateDataConf['table_name']
                }
                participant = Participant()
                participant.set_attrs(par_attrs)
                acceptData = {
                    "acceptors": participant
                    }
                task.set_attrs(acceptData)
                task.save()
                current_app.logger.info("【更新成功】" )
            else:  # assigner是其他服务器
                modelAssigner = jsonRes["modelAssigner"]
                serverIP = get_server_by_partyID(modelAssigner)
                # 调用assigner所在服务器的接口来更新task数据
                update_data = {
                    "modelID": form.modelID.data,
                    "nickName": current_user.nickname,
                    "partyID": current_app.config['LOCAL_PARTY_ID'],
                    "trainTableName": trainDataConf['table_name'],
                    "evaluateTableName": evaluateDataConf['table_name']
                }
                update_api='http://'+serverIP+':88/acceptor/update'
                update_res = post_form(update_api, data=update_data)    
                # update_res_str = update_res.content.decode()
                # current_app.logger.info("【update_API的返回:】update_res.data" )
                # current_app.logger.info(update_res.data)   # AttributeError: 'Response' object has no attribute 'data'

                # current_app.logger.info("【update_API的返回:】update_res.code" )
                # current_app.logger.info(update_res.code)

            '''更新本地服务器user-model表中的MyTask对象'''

            mytask = MyTask.objects.filter(nickName=current_user.nickname).first()
            if mytask:
                mytask.acceptModelList.append(form.modelID.data)
                mytask.save()
            else:
                mytask_table = {
                    "nickName": current_user.nickname,
                    "acceptModelList": form.modelID.data
                }
                mytask = MyTask()
                mytask.set_attrs(mytask_table)
                mytask.save()

            # 6.30 add
            allTask = AllTask.objects.filter(Q(modelID=form.modelID.data) & Q(status=1)).first()
            if allTask:
                allTask.isParticipated = 1
                allTask.save()
            # 详细返回        
            # return make_res('Success', data=jsonRes, message=1, description='')
            # # 简单返回

            return success_response()


@web.route('/task/testt', methods=['POST'])
def testt():
    update_api='http://10.99.12.103:88/acceptor/update'
    update_data = {
                "modelID": "1654075026819",
                "nickName": "current_user",
                "trainTableName": "guesst",
                "evaluateTableName": "test"
            }
    update_res = post_form(update_api, data=update_data)    
    # update_res_str = update_res.content.decode()
    current_app.logger.info("【update_API的返回:】" )
    current_app.logger.info(update_res)
    return 'ok'
