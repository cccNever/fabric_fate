"""
    time: 2022-5-23 11:04pm
    author: cpj
    update: 编写delete_head方法
"""
import json
import os, glob

from flask import current_app

from app.libs.error_code import APIError


def delete_head(name):
    """
        删除以name开头的文件
        :param name: 文件的前缀名
        :return:
    """
    for filename in glob.glob("./{}*".format(name)):
        if os.path.exists(filename):
            os.remove(filename)


def is_json(myjson):
    """
    判断<string>myjson是否是json格式
    """
    try:
        print("--------------"+myjson)
        json_object = json.loads(myjson)
    except ValueError as e:
        raise APIError(myjson)
    return True


def String_Split(string, separators):
    """
    string转list,多分隔符
    调用举例:String_Split_Result = String_Split(String_test, ',|/;')
    """
    # 将传进来的列表放入统一的数组中
    result_split = [string]
    # 使用for循环每次处理一种分割符
    for sep in separators:
        # 使用map函数迭代result_split字符串数组
        string_temp = []    # 用于暂时存储分割中间列表变量
        list(
              map(
                 lambda sub_string: string_temp.extend(sub_string.split(sep)),
                 result_split
                 )
             )
        # 经过上面的指令，中间变量string_temp就被分割后的内容填充了，
        # 将分割后的内容赋值给result_split，并作为函数返回值即可
        result_split = string_temp

    return result_split
    