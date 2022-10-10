"""
    time: 2022-5-25 5:25pm
    author: cpj
    update: 设置响应头，解决跨域问题

    todo: 使用before_request 设置请求拦截器
          使用after_request 设置响应头，解决跨域问题
"""

import json
import requests
from flask import jsonify, request, make_response, current_app
from app.config import BaseConfig

baseConfig = BaseConfig()
CODE_LIST = {
    "Success": 0,  # 成功
    # "ParamError": 40000,  #请求参数错误
    # "NullError": 40001,  #请求数据为空
    "NoLoginError": 40100 #未登录
    # "AuthError": 40101 #无权限
}

Headers = {
    'Content-Type': 'application/json'
}


def user_data(user):
    return {
        'nickname': user.nickname,
        'email': user.email,
        'role': user.role,
        'org': user.org,
        'avatarUrl': user.img_url,
        'partyID': user.party_id
    }


def success_response(data='', description='', **kwargs):
    """

    :param data: 数据
    :param message: 消息类型
    :param description: 消息描述
    :return:
    """
    res = make_response(
        jsonify(
            {
                "code": 0,
                "data": data,
                "msg": "success",
                "description": description
            }
        ),
        200,
        Headers
    )
    return res


def mail_response(data=''):
    """
    邮件消息返回体
    :param data:
    :return:
    """
    res = make_response(
        jsonify(
            {
                "code": 0,
                "data": data,
                "msg": "a confirm email is send",
                "description": ""
            }
        ),
        200,
        Headers
    )
    return res


def forward_response(jobId, description='a task starts', **kwargs):
    res = make_response(
        jsonify(
            {
                "code": 0,
                "data": {"queryURL": baseConfig.LOCAL_IP + 'api/task/async_result?jobID=' + jobId},
                "msg": "success",
                "description": description
            }
        ),
        200,
        Headers
    )
    return res


def make_error_res(code, description):
    res = make_response(
        jsonify(
            {
                "code": code,
                "description": description,
                "msg": 'error'
            }
        ),
        CODE_LIST.get(code),
        Headers
    )
    return res


def post_form(url, data=''):
    header = {
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    res = requests.post(url, data=data, headers=header)
    return res
