"""
    todo: 建立task视图层类
         添加当前参与人数
"""


def assign_data(task):
    """
    用于assign接口的返回
    :param task: task对象
    :return: dict
    """
    return {
        "taskID": str(task.id),
        "taskName": task.taskName,
        "createTime": task.assignDateTime,
        "modelID": task.modelID,
        "modelName": task.modelName,
        "numberOfPeers": task.numberOfPeers,
        "timeLimit": task.timeLimit,
        "description": task.description,
        "state": 'ASSIGNED'
    }


def participate_data(participate):
    """
    用于参与者的筛选
    :param participate:
    :return:
    """
    return {
        'nickname': participate.nickName,
        'participateDateTime': participate.participateDateTime
    }


def task_data(task):
    """
    用于返回任务列表
    :return:
    """
    dic = {
        "numberOfPeers": task['numberOfPeers'],
        "createTime": task['assignDateTime'],
        "taskName": task['taskName'],
        "timeLimit": task['timeLimit'],
        "isAssigner": 0,
        "state": task['state'],
        "partyID": task['modelAssigner'],
        "currentPeers": len(task['modelTrainer']),
        "modelID": task['modelID']
    }
    return dic


def detail_data(task):
    """
    用于返回任务详情
    :param task:
    :return:
    """
    acceptor_list = []
    for acceptor in task.acceptors:
        acceptor_list.append(participate_data(acceptor))
    dic = {
        "acceptors": acceptor_list,
        "assigner": participate_data(task['assigner']),
        "createTime": task['assignDateTime'],
        "description": task['description'],
        "modelID": task['modelID'],
        "modelName": task['modelName'],
        "state": task['state'],
        "timeLimit": task['timeLimit'],
        "taskName": task['taskName'],
        "labelName": task['labelName'],
        "featureNames": task['featureNames']
    }
    return dic


def accept_data(task):
    """
    用于accept接口的返回
    :param task: task对象
    :return: dict
    """
    return {
        "taskID": str(task.id),
        "taskName": task.taskName,
        "createTime": task.assignDateTime,
        "modelID": task.modelID,
        "modelName": task.modelName,
        "numberOfPeers": task.numberOfPeers,
        "timeLimit": task.timeLimit,
        "description": task.description,
        "state": 'ASSIGNED',
        "modelAssigner": task.assigner,
        "acceptors": task.acceptors
    }


def train_data(task, modelResult):
    """
    用于train成功的返回
    :param task: task对象
    :return: dict
    """
    return {
        "taskID": str(task.id),
        "taskName": task.taskName,
        "createTime": task.assignDateTime,
        "modelID": task.modelID,
        "modelName": task.modelName,
        "numberOfPeers": task.numberOfPeers,
        "timeLimit": task.timeLimit,
        "description": task.description,
        "state": task.state,
        "modelAssigner": task.assigner,
        "acceptors": task.acceptors,
        "result": modelResult
    }


