import os
from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

from app.libs.error_code import ModelStateError
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn import preprocessing


def get_server_by_partyID(partyID):
    """
    由partyID获得服务器ip
    """
    if partyID == '9999':
        serverip='10.99.12.103'
    elif partyID == '10000':
        serverip='10.99.12.101'
    elif partyID == '9998':
        serverip='10.99.12.104'
    return serverip


def get_partyID_by_server(serverip):
    """
    由server ip获得fate party id
    """
    if serverip == '10.99.12.103':
        partyID = '9999'
    elif serverip == '10.99.12.101':
        partyID = '10000'
    elif serverip == '10.99.12.104':
        partyID = '9998'
    return partyID


def save_files(type,trainfile,evaluatefile):
    """
    用于assign和accept存储数据文件
    type:"assign"或者"accept"
    """
    if type == "assign":   
        train_file_name = "user__" + current_user.nickname + "_" + secure_filename(trainfile.filename)
        train_file_path = current_app.config['UPLOAD_FOLDER_ASSIGN'] + train_file_name
        trainfile.save(train_file_path)

        evaluate_file_name = "user__" + current_user.nickname + "_" + secure_filename(evaluatefile.filename)
        evaluate_file_path = current_app.config['UPLOAD_FOLDER_ASSIGN'] + evaluate_file_name
        evaluatefile.save(evaluate_file_path)
    
    elif type == "accept":
        train_file_name = "user__" + current_user.nickname + "_" + secure_filename(trainfile.filename)
        train_file_path = current_app.config['UPLOAD_FOLDER_ACCEPT'] + train_file_name
        trainfile.save(train_file_path)

        evaluate_file_name = "user__" + current_user.nickname + "_" + secure_filename(evaluatefile.filename)
        evaluate_file_path = current_app.config['UPLOAD_FOLDER_ACCEPT'] + evaluate_file_name
        evaluatefile.save(evaluate_file_path)

def state_verification(state,needed_state):
    if state == needed_state:
        return True
    else:
        raise ModelStateError("模型状态不正确")