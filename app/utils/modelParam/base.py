import json
from app.libs.error_code import Forbidden
from app.utils.conf.base import ConfBase
from app.utils.dsl.ml import ModelDsl
from app.utils.dsl.testComponent import TestDsl
from app.utils.dsl.trainComponent import TrainDsl


class ConfBaseParam:
    """
        example:
        {
            "initiator": "9999",
            "guest_param": {
                'guest': "9999",
                'tableName': guest,
                'evaluateTableName': test,
            },
            "hosts_param": [
                {
                    'host': "10000",
                    'tableName': guest,
                    'evaluateTableName': test
                },
                 {
                    'host': "10001",
                    'tableName': guest,
                    'evaluateTableName': test
                }
            ]
            "model_param":{
                'param1': xxxx,
                'param2': xxxx
                ...
            }
            "feature_param":{
                "feature_binning": {

                }，
                ...
            }
        }
    """
    def __init__(self, model_name, initiator, guest_param, hosts_param, model_param, feature_param):
        if model_name == "homo_lr":
            self.model_name = "HomoLR"
        elif model_name == "homo_nn":
            self.model_name = "HomoNN"
        elif model_name == "homo_secureboost":
            self.model_name = "HomoSecureboost"
        self.initiator = initiator
        self.guest_param = guest_param
        self.hosts_param = hosts_param
        self.model_param = model_param
        self.feature_param = feature_param
        self.train_component_list = []
        self.test_component_list = []
        self.dsl = {}
        self.conf = {}
        self.__generate_base_conf()
        self.__generate_base_dsl()

    def setAttrs(self, initiator, guest_param, hosts_param):
        self.initiator = initiator
        self.guest_param = guest_param
        self.hosts_param = hosts_param

    def generate_conf_and_dsl(self):
        for key, value in self.feature_param:
            self.__add_component_conf(key, value)
            self.__add_feature_to_dsl(key, "train")
            self.__add_feature_to_dsl(key, "test")

    def __generate_base_conf(self):
        runConfFile = open("./app/base_json/"+self.model_name+"/train_run_base.json", encoding="utf-8")
        runConfStr = runConfFile.read()
        runConf = json.loads(runConfStr)
        if self.initiator is not None:
            runConf["initiator"]["party_id"] = self.initiator
            runConf["role"]["arbiter"] = runConf["role"]["guest"] = [self.initiator]
        if self.hosts_param is not None or len(self.hosts_param) != 0:
            host_list = []
            runHostFile = open("./app/base_json/train_run_host_base.json", encoding="utf-8")
            runHostStr = runHostFile.read()
            runHostConf = json.loads(runHostStr)
            for idx, host_param in enumerate(self.hosts_param):
                host_list.append(host_param['host'])
                runHostConf["reader_0"]["table"]["name"] = host_param["tableName"]
                runHostConf["reader_1"]["table"]["name"] = host_param["evaluateTableName"]
                host = {
                    str(idx): runHostConf
                }
                runConf["component_parameters"]["role"]["host"].update(host)
            runConf["role"]["host"] = host_list
        if self.guest_param is not None or len(self.guest_param.keys()) != 0:
            runConf["component_parameters"]["role"]["guest"]["0"]["reader_0"]["table"]["name"] = self.guest_param[
                'tableName']
            runConf["component_parameters"]["role"]["guest"]["0"]["reader_1"]["table"]["name"] = self.guest_param[
                'evaluateTableName']
        self.conf = runConf
        self.__add_component_conf(self.model_name, self.model_param)

    def __generate_base_dsl(self):
        component_name = self.model_name.lower() + "_0"
        dslConf = json.loads(open("./app/base_json/dsl_base.json", encoding="utf-8").read())
        component = ModelDsl(self.model_name, "dataio", "dataio")
        dslConf["components"]["component_name"] = component.generate_dsl()
        dslConf["components"][component_name] = dslConf["components"].pop('component_name')
        dslConf["components"]["evaluation_0"] = dslConf["components"].pop("evaluation_0")
        dslConf["components"]["evaluation_0"]["input"]["data"]["data"] = [component_name+".data"]
        self.train_component_list = ["reader", "dataio", self.model_name.lower(), "evaluation"]
        self.test_component_list = ["reader", "dataio", self.model_name.lower()]
        self.dsl = dslConf

    def __add_component_dsl(self, component_name, pre_component, component_type):
        """
        1. 根据type，选择模版
        2. 找到插入位置
        3. 插入，修改input以及下一个组件的output
        :param component_type:
        :param component_name: 模块名 大写
        :param pre_component: 上一个组件的名称 大写
        :return:dsl
        """
        if component_type == "train":
            trainDsl = TrainDsl(component_name, pre_component.lower())
            component_dsl = trainDsl.generate_dsl()
            pre_index = self.train_component_list.index(pre_component.lower())
            next_index = pre_index + 1
            next_component = self.train_component_list[next_index]
            if next_component == self.model_name:
                self.dsl["components"][next_component+"_0"]["input"]["data"]["train_data"] = component_name.lower()+"_0"+".data"
            else:
                self.dsl["components"][next_component + "_0"]["input"]["data"]["data"] = component_name.lower()+"_0"+".data"
            self.train_component_list.insert(next_index, component_name.lower())
            self.dsl["components"][component_name.lower() + "_0"] = component_dsl
        elif component_type == "test":
            testDsl = TestDsl(component_name, pre_component.lower(), component_name.lower())
            component_dsl = testDsl.generate_dsl()
            pre_index = self.test_component_list.index(pre_component.lower()+"_1")
            next_index = pre_index + 1
            next_component = self.test_component_list[next_index]
            if next_component == self.model_name:
                self.dsl["components"][next_component+"_0"]["input"]["data"]["validate_data"] = component_name.lower()+"_1"+".data"
            else:
                self.dsl["components"][next_component + "_1"]["input"]["data"]["data"] = component_name.lower() + "_1" + ".data"
            self.test_component_list.insert(next_index, component_name.lower())
            self.dsl["components"][component_name.lower()+"_1"] = component_dsl

    def __add_feature_to_dsl(self, feature, component_type):
        """

        :param feature: 特征工程名称 大写
        :param component_type: train or test
        :return:
        """
        accept_list = ["DataIo", "FeatureBinning", "Onehot", "FeatureScale"]
        if feature not in accept_list:
            raise Forbidden("unsupported feature engineering")
        for i in range(accept_list.index(feature), -1, -1):
            if accept_list[i].lower() in self.train_component_list or self.test_component_list:
                pre_component = accept_list[i]
                self.__add_component_dsl(feature, pre_component, component_type)

    def __add_component_conf(self, component, params):
        if component not in ConfBase.__subclasses__():
            raise Forbidden("unsupported component")
        conf_module = __import__('app.utils.conf')
        # 获取子类存在的py文件
        component_py = getattr(conf_module, component)
        # 获取子类
        component_class = getattr(component_py, component)
        component_ob = component_class(component)
        getattr(component_ob, 'set_attrs')(params)
        component_conf = getattr(component_ob, 'generate_conf')()
        self.conf['component_parameters']['common'][component.lower()+"_0"] = component_conf
        if component not in ["HomoLR", "HomoNN", "HomoSecureboost"]:
            self.conf['component_parameters']['common'][component.lower() + "_1"] = component_conf

    # def dsl_add_feature(self, feature_types, dsl):
    #     """
    #     :param module_types:list of feature engineering component module
    #     :return: dslConf
    #     """
    #     dslConf = dsl
    #     feature_engineering = [ "ColumnExpand", "Intersection", "LabelTransform", "FederatedSample",
    #                             "HomoOnehotEncoder", "FeatureScale", "HomoFeatureBinning", "HeteroFeatureBinning",
    #                             "HeteroFeatureSelection", "OneHotEncoder", "HomoOneHotEncoder"]
    #     dsl_component_list = ["Reader", "DataIO", "modelName", "Evaluation"]
    #
    #     for tp in feature_types:
    #         if tp in feature_engineering:
    #             dsl_component_list.append(tp)
    #         else:
    #             # return type error
    #             pass
    #     for cmpnt in dsl_component_list:
    #         front= self.find_front(cmpnt, dsl_component_list)
    #         dslConf=self.add_component(self, dsl, cmpnt, front)
    #     return dslConf
    #
    # def find_front(cmpnt, cmpnt_list):
    #     """
    #     按照fate示例规定组件顺序
    #     :param module_types:list of feature engineering component module
    #     :return: dslConf
    #     """
    #     order = ["Reader", "ColumnExpand", "DataIO", "Intersection", "LabelTransform", "FederatedSample",
    #             "HomoOnehotEncoder", "FeatureScale", "HomoFeatureBinning", "HeteroFeatureBinning",
    #             "HeteroFeatureSelection", "OneHotEncoder", "HomoOneHotEncoder", "modelName", "Evaluation"]
    #     front = None
    #     length = len(order)
    #     index = order.index(cmpnt) - 1
    #     while 0 <= index < length:
    #         if order[index] in cmpnt_list:
    #             front = order[index]
    #             break
    #         else:
    #             front = None
    #         index = index - 1
    #     return front
    #
    # def to_dict(self):
    #     return self.__dict__
