import json
from app.celery_works import celery
from flask import current_app
from app.utils.http import post_form
from app.utils.oshelper import is_json
from app.models.task import Task, AllTask

import pymongo
from app import config


'''celery异步测试'''

@celery.task(bind=True)
def async_task(self):
    res={
        "nickName":"412213111",
        "email":"4123111@qq.com"
    }
    # user_model=celery_db["user-model"]
    # user_model.insert(res)
    celery_mongo_client=pymongo.MongoClient("mongodb://user_ffb:123123@10.99.12.103:27019/?authSource=fabric_fatedb")
    celery_db=celery_mongo_client.fabric_fatedb 
    celery_db.user.insert_one(res)
    print("res111111111111111111111111111111111111111111111")
    ret_msg={'msg': "res"}
    return ret_msg


'''异步assign(还没用)'''
@celery.task(bind=True)
def async_assign(self, assign_api, data):
    assignRes = post_form(assign_api, data=data)
    assignRes_str = assignRes.content.decode()
    try:
        json.loads(assignRes_str)
        return {"assignRes_str": assignRes_str, "status": 'Success','data':data}
    except:
        return {"assignRes_str": assignRes_str, "status": 'Failed'}


'''异步accept'''
@celery.task(bind=True)
def async_accept(self, accept_api, data):
    acceptRes = post_form(accept_api, data=data)  # 类型：response
    acceptRes_str = acceptRes.content.decode()
    while acceptRes_str == "Connection Failed!":
        acceptRes = post_form(accept_api, data=data)  # 类型：response类
        acceptRes_str = acceptRes.content.decode()
    try:
        json.loads(acceptRes_str)
        return {"acceptRes_str": acceptRes_str, "status": 'Success','data':data}
    except:
        return {"acceptRes_str": acceptRes_str, "status": 'Failed'}


'''异步train'''
@celery.task(bind=True)
def async_train(self, train_api, data):
    """
    异步train
    """
    '''----------------调8010:train接口-----------------'''
    trainRes = post_form(train_api, data=data)
    trainRes_str = trainRes.content.decode()
    while trainRes_str=="Connection Failed!":
        current_app.logger.info(trainRes_str)
        trainRes = post_form(train_api, data=data)
        trainRes_str = trainRes.content.decode()
    try:
        json.loads(trainRes_str)

        return {"trainRes_str": trainRes_str, "status": 'Success'}
    except:
        return {"trainRes_str": trainRes_str, "status": 'Failed'}
