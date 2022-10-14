"""
    todo: 查看任务的历史记录， 重写数据库查询方法
            参与者参与任务的时候判断是否已经参与该任务

    2022.6.20 lxk update:获取模型结果/task/getResult
                            下载结果文件:/task/resultDownload

    2022.7.11 assign、accept、train改异步
"""
import threading

from . import web
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app, request, send_file
from flask_login import login_required, login_user, current_user
from mongoengine.queryset.visitor import Q
from threading import Thread
import time

from app.forms.task import ParticipantForm, AssignForm, AcceptForm, TrainForm, PreProcessForm
from app.models.task import Participant, Task, MyTask, AllTask, ModelResult
from app.viewmodels.task_res import task_data, detail_data, assign_data
from app.requestModels.task_request import assign_request
from app.utils.modelParam.base import ConfBaseParam
from app.utils.http import success_response, forward_response, post_form
from app.utils.hardware_status import get_cpu_status, get_memory_status
from app.utils.oshelper import delete_head, is_json
from app.utils.task import state_verification, get_server_by_partyID, save_files
from app.libs.server_identify import get_server_ip
from app.libs.error_code import APIError
from app.celery_works.tasks import async_task, async_train, async_accept
from app import redis_client
from app import scheduler


def _all_task_update():
    task_list = post_form(current_app.config['LOCAL_FATE_IP'] + 'queryModel').json()
    time.sleep(1)
    # current_app.logger.info(task_list)
    if task_list[0] != 'No More Transaction':
        for task in task_list:
            task_dict = json.loads(task)
            # current_app.logger.info("*******************************")
            # current_app.logger.info(task_dict)
            record = AllTask.objects(modelID=task_dict['modelID']).first()
            if record:
                record.delete()
            new_record = AllTask()
            new_record.set_attrs(task_dict)
            new_record.save()


# @scheduler.task('interval', id='data_update', seconds=60, misfire_grace_time=900)
# def job1():
#     with scheduler.app.app_context():
#         _all_task_update()

# 定时测速
# @scheduler.task('interval', id='get_speed', seconds=180, misfire_grace_time=900)
# def scheduler_get_speed():
#     with scheduler.app.app_context():
#         speedRes=get_test_speed() # downloadSpeed,uploadSpeed
#         redis_client.set("_speed", speedRes)


@web.before_request
def update_database():
    current_app.logger.info('【request before】')
    if request.path in ['/api/task/assign', '/api/task/accept', '/api/task/train', '/api/task/allTask',
                        '/api/task/mytask']:
        _all_task_update()
    return None


@web.after_request
def set_database(environ):
    """
    请求拦截器
    :param environ:
    :return:
    """
    current_app.logger.info('【request after】')
    if request.path in ['/api/task/assign', '/api/task/accept', '/api/task/train', '/api/task/allTask',
                        '/api/task/mytask']:
        _all_task_update()
        # scheduler.pause_job('data_update')
    return environ


@web.route('/acceptor/update', methods=['POST', 'OPTIONS'])
def update():
    """
    供其他服务器调用,以更新本服务器上的assigned-model数据库
    """
    form = ParticipantForm()
    current_app.logger.info(form.data)
    if form.validate_for_api():
        participant = Participant()
        participant.set_attrs(form.data)
        # 接受acceptor发来的信息，更新本地数据库
        task = Task.objects.filter(modelID=form.modelID.data).first()
        task.acceptors.append(participant)
        task.save()
        return success_response()


@web.route('/query/<model_id>', methods=['POST'])
def query(model_id):
    """
    服务器之间互相获取mongoddb中的assigned_model信息???
    :param model_id
    :return: acceptors和assigner
    """
    task = Task.objects.filter(modelID=model_id).first()
    return success_response(detail_data(task))


"""-------------------以下接口对外暴露----------------------"""

'''获取训练好的模型结果'''


@web.route('/api/task/getResult', methods=['GET', 'POST', 'GET'])
@login_required
def getResult():
    """
    需要从前端获得:modelID
    """
    modelID = request.args.get('modelID')
    findresult = ModelResult.objects.filter(modelID=modelID).first()
    if not findresult:  # 数据库里没存该模型结果
        '''调103:8010/queryByModelID接口获取最新一条记录'''
        queryByModelID_api = current_app.config["LOCAL_FATE_IP"] + "queryByModelID"
        data = {"modelID": modelID}
        res = post_form(queryByModelID_api, data=data)
        res_str = res.content.decode()
        res_json = json.loads(res_str)
        num = str(len(res_json) - 1)
        record = json.loads(res_json[num])  # 最新一条记录

        # 判断模型状态
        state = record["state"]
        if state_verification(state, "FINISHED"):
            # 获取模型结果
            result = record["result"]
            result_json = json.loads(result)
            result_json.pop('retcode')
            result_json.pop('retmsg')
            result_str = json.dumps(result_json)
            # 保存模型结果json形式进数据库
            attrs_data = {
                "modelID": modelID,
                "modelResult": result_str
                # "modelResult": str(result_json).replace("'", '"')
            }
            modelresult = ModelResult()
            modelresult.set_attrs(attrs_data)
            modelresult.save()
    else:
        result_json = findresult.modelResult
    return success_response(data=str(result_json))


@web.route('/api/task/resultDownload', methods=['POST', 'GET', 'OPTIONS'])
@login_required
def resultDownload():
    """
    下载模型结果文件
    需要从前端获得:modelID
    """
    modelID = request.args.get('modelID')
    queryByModelID_api = current_app.config["LOCAL_FATE_IP"] + "queryByModelID"
    data = {"modelID": modelID}
    res = post_form(queryByModelID_api, data=data)
    res_str = res.content.decode()
    res_json = json.loads(res_str)
    num = str(len(res_json) - 1)
    record = json.loads(res_json[num])  # 最新一条记录

    # 判断模型状态
    state = record["state"]
    if state_verification(state, "FINISHED"):
        result_file_name = "resultModel_" + modelID + ".json"
        # 这个路径拼不对，目前写成固定的了
        # result_file_path = os.path.join(current_app.config['DOWNLOAD_FOLDER_RESULT_MODEL'],result_file_name)
        result_file_path = "/home/web/data/modelResult/" + result_file_name
        current_app.logger.info(result_file_path)
        if not os.path.exists(result_file_path):  # 若文件不存在
            findresult = ModelResult.objects.filter(modelID=modelID).first()
            result_json = json.loads(findresult.modelResult)

            os.makedirs('./data/modelResult', exist_ok=True)
            result_file = open(result_file_path, 'w')
            json.dump(result_json, result_file)
            result_file.close()

        return send_file(result_file_path, as_attachment=True)  # 成功


@web.route('/api/task/allTask', methods=['GET'])
@login_required
def all_task():
    """
        获取所有任务列表
    :return:
    """
    accept_list = AllTask.objects.filter(state='ASSIGNED')
    # 筛选一下 返回
    res_data = []
    for item in accept_list:
        current_app.logger.info(current_user.party_id)
        current_app.logger.info(item['modelAssigner'])
        current_app.logger.info(len(item['modelTrainer']))
        if current_user.party_id != item['modelAssigner'] and current_user.party_id not in item['modelTrainer']:
            res_data.append(task_data(item))
    sort_data = sorted(res_data, key=lambda k: (k.get('assignDateTime', '')), reverse=True)
    return success_response(sort_data)


@web.route('/api/task/mytask', methods=['GET'])
@login_required
def my_task():
    """
        获取自己的任务列表
        :return:
    """
    mytask = MyTask.objects.filter(nickName=current_user.nickname).first()
    res_list = []
    if mytask:
        for modelID in mytask.assignModelList:
            task = AllTask.objects(modelID=modelID).first()
            current_app.logger.info(task['modelTrainer'])
            if task:
                task_dic = task_data(task)
                task_dic['isAssigner'] = 1
                res_list.append(task_dic)
        for modelID in mytask.acceptModelList:
            task = AllTask.objects.filter(modelID=modelID).first()
            current_app.logger.info(len(task['modelTrainer']))
            if task:
                task_dic = task_data(task)
                task_dic['isAssigner'] = 0
                res_list.append(task_dic)
    # 筛选一下 返回
    sort_data = sorted(res_list, key=lambda k: (k.get('assignDateTime', '')), reverse=True)
    return success_response(sort_data)


@web.route('/api/task/detail', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def task_detail():
    model_id = request.args.get('modelID')
    server_id = request.args.get('serverID')
    ip_addr = get_server_ip(server_id)
    # 发出查询请求
    res_data = post_form(ip_addr + 'query/' + model_id).json()
    return success_response(data=res_data['data'])


@web.route('/api/task/assign', methods=['POST', 'OPTIONS'])
@login_required
def assign():
    """
    :param:
        modelName : 模型类型
        minPeers : 参与节点数
        trainFile : 训练集
        evaluateFile : 测试集
        description: 任务描述
        taskName: 任务名
        modelParam: 模型参数
        featureParam: 特征工程参数
    :return:
    """
    current_app.logger.info('【--------------------------assign--------------------------】')
    form = AssignForm()
    if form.validate_for_api():
        # 创建文件夹
        os.makedirs('./data/assign', exist_ok=True)
        # 首先删除上次保存的用户文件
        delete_head("data/assign/user")
        # 保存文件
        train_file = form.trainFile.data
        train_file_name = "user__" + current_user.nickname + "_" + secure_filename(train_file.filename)
        train_file.save(current_app.config['UPLOAD_FOLDER_ASSIGN'] + train_file_name)
        evaluate_file = form.evaluateFile.data
        evaluate_file_name = "user__" + current_user.nickname + "_" + secure_filename(evaluate_file.filename)
        evaluate_file.save(current_app.config['UPLOAD_FOLDER_ASSIGN'] + evaluate_file_name)
        base_path = current_app.config['BASE_UPLOAD_FOLDER'] + "assign/"  # 这里改了BASE_UPLOAD_FOLDER

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
            "minPeers": form.minPeers.data,
            "numberOfPeers": 1,
            "timeLimit": form.timeLimit.data,  # 改动:变成定值了
            "trainDataConf": str(trainDataConf).replace("'", '"'),
            "evaluateDataConf": str(evaluateDataConf).replace("'", '"'),
            "restrict": form.taskName.data,
            "modelParam": form.modelParam.data,
            "featureParam": form.featureParam.data,
            "labelName": form.labelName.data,
            "featureNames": form.featureNames.data
        }
        current_app.logger.info("assign!!!!!!!!!!!!!!!!")
        current_app.logger.info(str(data))
        assign_api = current_app.config["LOCAL_FATE_IP"] + "assign"
        thread = Thread(target=send_async_assign, args=[current_app._get_current_object(), assign_api, data],
                        kwargs={'nickname': current_user.nickname, 'description': form.description.data})
        thread.start()
        return forward_response(str(thread.ident), description='Model starts assigning')


def send_async_assign(app, assign_api, data, **kwargs):
    id = str(threading.currentThread().ident)
    with app.app_context():
        redis_client.set(id, "ASSIGNING")
        assign_res_body = post_form(assign_api, data=assign_request(data)).content.decode()
        current_app.logger.info("【assign_res_body】:")
        current_app.logger.info(assign_res_body)
        try:
            jsonData = json.loads(assign_res_body)
            _all_task_update()  # 7.6 add
            trainDataConf = json.loads(data['trainDataConf'])
            evaluateDataConf = json.loads(data['evaluateDataConf'])
            # 构造assigner
            assigner = Participant(
                nickName=kwargs['nickname'],
                partyID=jsonData['modelAssigner'],
                # participateDateTime=jsonData['assignDateTime'], # 6.8 删除
                trainTableName=trainDataConf['table_name'],  # 新增
                evaluateTableName=evaluateDataConf['table_name']  # 新增
            )
            '''更新assign-model'''
            # 构造task对象
            attrs_data = {
                "assigner": assigner,
                "taskName": jsonData['restrict'],
                "assignDateTime": assigner.participateDateTime,
                "modelID": jsonData['modelID'],
                "modelName": jsonData['modelName'],
                "minPeers": data['minPeers'],
                "description": kwargs['description'],
                "timeLimit": jsonData['timeLimit'],
                "state": 'ASSIGNED',
                "modelParam": data['modelParam'],
                "featureParam": data["featureParam"],
                "labelName": data["labelName"],
                "featureNames": data["featureNames"]
            }
            task = Task()
            task.set_attrs(attrs_data)
            task.save()
            '''更新本地服务器user-model表中的MyTask对象'''  # 6.2 新增
            mytask = MyTask.objects.filter(nickName=kwargs['nickname']).first()
            if mytask:
                mytask.assignModelList.append(jsonData['modelID'])
                mytask.save()
            else:
                mytask_table = {
                    "nickName": kwargs['nickname'],
                    "assignModelList": jsonData['modelID']
                }
                mytask = MyTask()
                mytask.set_attrs(mytask_table)
                mytask.save()
            redis_client.set(id, "FINISHED")
        except:
            '''回滚alltask数据库'''
            allTask = AllTask.objects.filter(modelID=data['modelID'])
            # current_app.logger.info(allTask)
            for task in allTask:
                task.delete()
            redis_client.set(id, "ERROR")
            raise APIError('创建任务失败')


@web.route('/api/task/async_result', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def get_result():
    id = request.args.get('jobID')
    current_app.logger.info(id)
    return success_response(str(redis_client.get(id), 'utf-8'))


@web.route('/api/task/accept', methods=['POST'])
@login_required
def accept():
    """
    form需要传的:
    modelID : assign后返回的modelID
    trainFile:训练数据文件
    evalueFile:验证数据文件
    """
    current_app.logger.info('【--------------------------accept--------------------------】')
    form = AcceptForm()
    # current_app.logger.info(form.data)
    if form.validate_for_api():
        '''调用accept接口接收任务'''

        # 获取并存储traindata和evaluatedata文件
        os.makedirs('./data/accept', exist_ok=True)
        # 首先删除上次保存的用户文件
        delete_head("data/accept/user")
        train_file = form.trainFile.data
        evaluate_file = form.evaluateFile.data
        save_files("accept", train_file, evaluate_file)

        modelTrainer = current_app.config["LOCAL_PARTY_ID"]
        base_path = current_app.config['BASE_UPLOAD_FOLDER'] + "accept/"
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
        data = {
            "modelID": form.modelID.data,
            "modelTrainer": modelTrainer,
            "trainDataConf": str(trainDataConf).replace("'", '"'),
            "evaluateDataConf": str(evaluateDataConf).replace("'", '"'),
        }
        current_app.logger.info("accept!!!!!!!!!!!!")
        current_app.logger.info(str(data))
        accept_api = current_app.config["LOCAL_FATE_IP"] + "accept"
        thread = Thread(target=send_async_accept, args=[current_app._get_current_object(), accept_api, data],
                        kwargs={'nickname': current_user.nickname})
        thread.start()
        return forward_response(str(thread.ident), description='Model starts accepting')


def send_async_accept(app, accept_api, data, **kwargs):
    id = str(threading.currentThread().ident)
    with app.app_context():
        redis_client.set(id, "ACCEPTING")
        acceptRes_str = post_form(accept_api, data=data).content.decode()
        while acceptRes_str == "Connection Failed!":
            acceptRes_str = post_form(accept_api, data=data).content.decode()
        current_app.logger.info("【acceptRes_str】:")
        current_app.logger.info(acceptRes_str)
        try:
            jsonRes = json.loads(acceptRes_str)
            _all_task_update()  # 7.6 add
            trainDataConf = json.loads(data['trainDataConf'])
            evaluateDataConf = json.loads(data['evaluateDataConf'])
            task = Task.objects.filter(modelID=data['modelID']).first()
            if task:  # 本地服务器有这个task的相关记录（assigner是本地服务器）
                par_attrs = {
                    "nickName": kwargs['nickname'],
                    "partyID": data['modelTrainer'],
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
            else:  # assigner是其他服务器
                modelAssigner = jsonRes["modelAssigner"]
                serverIP = get_server_by_partyID(modelAssigner)
                # 调用assigner所在服务器的接口来更新task数据

                update_data = {
                    "modelID": jsonRes['modelID'],
                    "nickName": kwargs['nickname'],
                    "partyID": data['modelTrainer'],
                    "trainTableName": trainDataConf['table_name'],
                    "evaluateTableName": evaluateDataConf['table_name']
                }
                update_api = 'http://' + serverIP + ':88/acceptor/update'
                update_res = post_form(update_api, data=update_data)

            '''更新本地服务器user-model表中的MyTask对象'''

            mytask = MyTask.objects.filter(nickName=kwargs['nickname']).first()
            if mytask:
                mytask.acceptModelList.append(jsonRes['modelID'])
                mytask.save()
            else:
                mytask_table = {
                    "nickName": kwargs['nickname'],
                    "acceptModelList": jsonRes['modelID']
                }
                mytask = MyTask()
                mytask.set_attrs(mytask_table)
                mytask.save()
            redis_client.set(id, "FINISHED")
            _all_task_update()
        except:
            '''回滚alltask数据库'''
            # time.sleep(5)
            # allTask = AllTask.objects.filter(modelID=data['modelID'], status=1)
            # current_app.logger.info(allTask)
            # for task in allTask:
            #     task.delete()
            redis_client.set(id, "ERROR")
            raise APIError('接收任务失败')


@web.route('/api/task/train', methods=['POST', 'OPTIONS'])
@login_required
def train():
    """
    modelID
    modelAndEvaluation:要用户输入的json,训练模型和评估的组件配置
    """
    current_app.logger.info('【--------------------------train--------------------------】')
    form = TrainForm()
    if form.validate_for_api():
        modelID = form.modelID.data
        local_party_ID = current_app.config["LOCAL_PARTY_ID"]
        task = Task.objects.filter(modelID=modelID).first()

        initiator = int(local_party_ID)
        guest_param = {
            "guest": int(task.assigner.partyID),
            "tableName": task.assigner.trainTableName,
            "evaluateTableName": task.assigner.evaluateTableName
        }
        hosts_param = []
        for acceptor in task.acceptors:
            item = {
                "host": int(acceptor.partyID),
                "tableName": acceptor.trainTableName,
                "evaluateTableName": acceptor.evaluateTableName
            }
            hosts_param.append(item)
        model_param = json.loads(task.modelParam)
        feature_param = json.loads(task.featureParam)
        labelName = task.labelName
        model_setting = ConfBaseParam(task.modelName, labelName, initiator, guest_param, hosts_param, model_param, feature_param)
        model_setting.generate_conf_and_dsl()
        dslConf = model_setting.dsl
        runConf = model_setting.conf

        dslConfStr = json.dumps(dslConf)
        runConfStr = json.dumps(runConf)
        current_app.logger.info('【dslConfStr】:')
        current_app.logger.info(dslConfStr)
        current_app.logger.info('【runConfStr】:')
        current_app.logger.info(runConfStr)

        task = Task.objects.filter(modelID=modelID).first()
        if task:
            task.state = 'TRAINED'
            task.save()

        train_api = current_app.config["LOCAL_FATE_IP"] + "train"
        data = {"modelID": modelID, "dslConf": dslConfStr, "runConf": runConfStr}
        current_app.logger.info(str(data))
        thread = Thread(target=send_async_train, args=[current_app._get_current_object(), train_api, data])
        thread.start()
        return forward_response(str(thread.ident), description='Model starts training')


def send_async_train(app, train_api, data, **kwargs):
    id = str(threading.currentThread().ident)
    with app.app_context():
        current_app.logger.info('id--------------')
        current_app.logger.info(id)
        redis_client.set(id, "TRAINING")
        trainRes_str = post_form(train_api, data=data).content.decode()
        while trainRes_str == "Connection Failed!" or trainRes_str == "org.hyperledger.fabric.gateway.ContractException: Failed to send transaction to the orderer":
            current_app.logger.info("【trainRes_str】:")
            current_app.logger.info(trainRes_str)
            trainRes_str = post_form(train_api, data=data).content.decode()
        current_app.logger.info("【trainRes_str】:")
        current_app.logger.info(trainRes_str)
        try:
            jsonData = json.loads(trainRes_str)
            _all_task_update()  # 7.6 add
            '''---------------模型状态改为finished-----------------'''
            task = Task.objects.filter(modelID=data['modelID']).first()
            if task:
                task.state = 'FINISHED'
                task.save()
            redis_client.set(id, "FINISHED")
            time.sleep(5)
            _all_task_update()
        except:
            '''回滚alltask数据库'''
            redis_client.set(id, "ERROR")
            raise APIError('训练失败')


@web.route('/api/task/query', methods=['POST', 'GET', 'OPTIONS'])
@login_required
def task_query():
    """
    从AllTask数据库中查询某模型

    :return:
    """
    modelID = request.args.get('modelID')
    state = AllTask.objects.filter(modelID=modelID).first()
    current_app.logger.info("【/api/task/query】")
    current_app.logger.info(modelID)
    current_app.logger.info(state)
    return success_response(data=state)


@web.route('/api/status/hardware', methods=['POST', 'GET'])
@login_required
def hardware():
    current_app.logger.info("【--------------------------/api/status/hardware--------------------------】")
    cpu_status = get_cpu_status()
    memory_status = get_memory_status()
    response = {
        'cpuStatus': {
            'physicalCores': cpu_status['physicalCores'],
            'logicalCores': cpu_status['logicalCores'],
            'percentage': cpu_status['percentage']
        },
        'memoryStatus': {
            'total': memory_status['total'],
            'used': memory_status['used'],
            'free': memory_status['free'],
            'percentage': memory_status['percentage']
        }
    }
    current_app.logger.info(response)
    return success_response(data=response)


@web.route('/api/status/getSpeed', methods=['POST', 'GET'])
@login_required
def getSpeed():
    res_str = redis_client.get("_speed")
    current_app.logger.info("----------getSpeed---------")
    current_app.logger.info(res_str)
    res = json.loads(res_str)
    return success_response(data=res)


@web.route('/api/test', methods=['POST', 'GET'])
def test3():
    celery_result = async_task.delay()
    '''将modelID,异步任务id存在redis里'''
    return celery_result.id


@web.route('/api/get_test_return/<task_id>', methods=['GET', 'POST'])
def get_test_return(task_id):
    # result = AsyncResult(celery_id, app=celery_app)
    task = async_task.AsyncResult(task_id)

    if task.state == 'PENDING':  # 在等待
        response = {
            'state': task.state
        }
        return response
    response = {
        'state': task.state
    }
    return response


@web.route('/api/task/async_accept_result', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def async_accept_result():
    """
    获取Celery异步accept的结果
    :return:
    """
    modelID = request.args.get('modelID')
    task_id = redis_client.get(modelID)
    current_app.logger.info(task_id)
    task = async_accept.AsyncResult(task_id)
    if task.state == 'PENDING':  # 在等待
        response = {
            'state': task.state
        }
        return success_response(data=response, description='model is accepting')
    elif task.state != 'FAILURE':  # 没有失败
        acceptRes_str = task.info.get('acceptRes_str')
        current_app.logger.info("【accept的返回:】")
        current_app.logger.info(acceptRes_str)
        current_app.logger.info("【accept的返回type:】")
        current_app.logger.info(type(acceptRes_str))
        # try: #成功
        if is_json(acceptRes_str):
            jsonRes = json.loads(acceptRes_str)
            _all_task_update()
            data = task.info.get('data')
            '''更新assign-model表中的task对象'''

            task = Task.objects.filter(modelID=data['modelID']).first()
            if task:  # 本地服务器有这个task的相关记录（assigner是本地服务器）
                par_attrs = {
                    "nickName": current_user.nickname,
                    # "participateDateTime": jsonRes['acceptDateTime'], # 6.8 删除
                    "partyID": data['modelTrainer'],
                    "trainTableName": data['trainDataConf']['table_name'],
                    "evaluateTableName": data['evaluateDataConf']['table_name']
                }
                participant = Participant()
                participant.set_attrs(par_attrs)
                acceptData = {
                    "acceptors": participant
                }
                task.set_attrs(acceptData)
                task.save()
                current_app.logger.info("【更新成功】")
            else:  # assigner是其他服务器
                modelAssigner = jsonRes["modelAssigner"]
                serverIP = get_server_by_partyID(modelAssigner)
                # 调用assigner所在服务器的接口来更新task数据
                trainDataConf = json.loads(data['trainDataConf'])
                evaluateDataConf = json.loads(data['evaluateDataConf'])
                update_data = {
                    "modelID": modelID,
                    "nickName": current_user.nickname,
                    "partyID": data['modelTrainer'],
                    "trainTableName": trainDataConf['table_name'],
                    "evaluateTableName": evaluateDataConf['table_name']
                }
                update_api = 'http://' + serverIP + ':88/acceptor/update'
                update_res = post_form(update_api, data=update_data)

            '''更新本地服务器user-model表中的MyTask对象'''

            mytask = MyTask.objects.filter(nickName=current_user.nickname).first()
            if mytask:
                mytask.acceptModelList.append(modelID)
                mytask.save()
            else:
                mytask_table = {
                    "nickName": current_user.nickname,
                    "acceptModelList": modelID
                }
                mytask = MyTask()
                mytask.set_attrs(mytask_table)
                mytask.save()

            return success_response(data='', description='Accept Success')
        # except:
        #     raise APIError('接收任务失败'+acceptRes_str)


@web.route('/api/task/async_train_result', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def async_train_result():
    """
    获取Celery异步train的结果
    :return:
    """
    modelID = request.args.get('modelID')
    task_id = redis_client.get(modelID)
    current_app.logger.info(task_id)
    task = async_train.AsyncResult(task_id)
    if task.state == 'PENDING':  # 在等待
        response = {
            'state': task.state
        }
        return success_response(data=response, description='model starts training')
    elif task.state != 'FAILURE':  # 没有失败
        trainRes_str = task.info.get('trainRes_str')
        current_app.logger.info("【train的返回:】")
        current_app.logger.info(trainRes_str)
        current_app.logger.info("【train的返回type:】")
        current_app.logger.info(type(trainRes_str))

        try:
            trainResJson = json.loads(trainRes_str)
            '''---------------模型状态改为finished-----------------'''
            task = Task.objects.filter(modelID=modelID).first()
            if task:
                task.state = 'FINISHED'
                task.save()
                response = {
                    'state': task.state  # 状态
                }
                return success_response(data=response, description='model starts training')
        except:
            task = Task.objects.filter(modelID=modelID).first()
            if task:
                task.state = 'ERROR'
                task.save()
            all_task = AllTask.objects.filter(modelID=modelID).first()
            if all_task:
                all_task.state = 'ERROR'
                all_task.save()
            response = {
                'state': task.state  # 状态
                # 'msg': 'Train error!'
            }
            return success_response(data=response, description='model starts training')

    else:
        response = {
            'state': task.state
            # 'msg': str(task.info) # 报错的具体异常
        }
        return success_response(data=response, description='model starts training')
