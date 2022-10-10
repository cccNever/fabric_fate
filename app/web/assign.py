"""
    time: 2022-5-23 11:04pm
    author: cpj
    update: 优化文件路径
            构建task模型
            通过taskid查看任务
            查看自己的任务 待续
    time: 2022-5-24 3:54pm
    author: cpj
    update: 封装返回数据函数，放在viewmodels下
            优化模型类结构，添加EmbeddedDocument
            查看的任务

    todo: 构造model模型类，查看自己创建的任务详情、参与的任务详情
          请求改成异步的
          构造视图层 task, assign
"""
import os
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.utils.task import save_files

from . import web
from app.forms.task import AssignForm
from app.models.task import Task, Participant, MyTask, AllTask
from app.utils.oshelper import delete_head, is_json
from app.utils.http import success_response, post_form
from app.viewmodels.task_res import assign_data
from flask import current_app
from mongoengine.queryset.visitor import Q


@web.route('/api/task/assign_test', methods=['POST', 'OPTIONS'])
@login_required
def assign_test():
    form = AssignForm()
    if form.validate_for_api():
        # 创建文件夹
        os.makedirs('./data/assign', exist_ok=True)
        # 首先删除上次保存的用户文件
        delete_head("data/assign/user")

        train_file = form.trainFile.data
        """
            todo: current_user.nickname 双引号去掉
        """
        train_file_name = "user__" + current_user.nickname + "_" + secure_filename(train_file.filename)
        train_file.save(current_app.config['UPLOAD_FOLDER_ASSIGN'] + train_file_name)
        evaluate_file = form.evaluateFile.data
        evaluate_file_name = "user__" + current_user.nickname + "_" + secure_filename(evaluate_file.filename)
        evaluate_file.save(current_app.config['UPLOAD_FOLDER_ASSIGN'] + evaluate_file_name)
        base_path = current_app.config['BASE_UPLOAD_FOLDER'] + "assign/"  # 这里改了BASE_UPLOAD_FOLDER

        # # 封装了save_files函数，不过还没测试
        # train_file = form.trainFile.data
        # evaluate_file = form.evaluateFile.data
        # save_files("assign",train_file,evaluate_file)

        # 发送post请求
        trainDataConf = {
            "head": 1,
            "drop": 1,
            "partition": 5,
            "file": base_path + train_file_name,
            "namespace": "experiments",
            "table_name": os.path.splitext(train_file.filename)[0]  # 改动:去掉文件类型后缀
        }
        evaluateDataConf = {
            "head": 1,
            "drop": 1,
            "partition": 5,
            "file": base_path + evaluate_file_name,
            "namespace": "experiments",
            "table_name": os.path.splitext(evaluate_file.filename)[0]  # 改动:去掉文件类型后缀
        }
        data = {
            "modelName": form.modelName.data,
            "modelAssigner": current_app.config["LOCAL_PARTY_ID"],  # 改了这个
            "numberOfPeers": form.numberOfPeers.data,
            "timeLimit": form.timeLimit.data,
            "trainDataConf": str(trainDataConf).replace("'", '"'),
            "evaluateDataConf": str(evaluateDataConf).replace("'", '"'),
            "restrict": form.taskName.data
        }
        # 获取接口返回结果

        res = post_form(current_app.config['LOCAL_FATE_IP']+'assign', data=data)
        res_str = res.content.decode()
        if is_json(res_str):  # 加了json判断，如果返回值不是json就说明调用api失败，直接将失败信息返回给前端
            jsonData = res.json()
            current_app.logger.info("【Assign的返回:】" + str(type(res)))
            current_app.logger.info(jsonData)
            # 构造assigner
            assigner = Participant(
                nickName=current_user.nickname,
                partyID=jsonData['modelAssigner'],
                # participateDateTime=jsonData['assignDateTime'], # 6.8 删除
                trainTableName=trainDataConf['table_name'],  # 新增
                evaluateTableName=evaluateDataConf['table_name']  # 新增
            )
            # 构造task对象

            attrs_data = {
                "assigner": assigner,
                "taskName": jsonData['restrict'],
                "createTime": assigner.participateDateTime,
                "modelID": jsonData['modelID'],
                "modelName": jsonData['modelName'],
                "numberOfPeers": jsonData['numberOfPeers'],
                "description": form.description.data,
                "timeLimit": jsonData['timeLimit'],
                "state": 'ASSIGNED'
            }
            task = Task()
            task.set_attrs(attrs_data)
            task.save()
            '''更新本地服务器user-model表中的MyTask对象'''  # 6.2 新增
            mytask = MyTask.objects.filter(nickName=current_user.nickname).first()
            if mytask:
                mytask.assignModelList.append(jsonData['modelID'])
                mytask.save()
            else:
                mytask_table = {
                    "nickName": current_user.nickname,
                    "assignModelList": jsonData['modelID']
                }
                mytask = MyTask()
                mytask.set_attrs(mytask_table)
                mytask.save()
            # 6.30 add
            allTask = AllTask.objects.filter(Q(modelID=jsonData['modelID']) & Q(status=1)).first()
            if allTask:
                allTask.isParticipated = 1
                allTask.save()
            return success_response(data=assign_data(task))






