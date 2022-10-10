from app.utils.modelParam.base import ConfBaseParam
import json


class BaseLayerParam:
    def __init__(self, layerParam):
        """
        :param className: 层的类型
        :param useBias:
        :param activation:
        :param kernelInitializer:
        :param biasInitializer:
        """
        self.layerParam = layerParam

    def generate_layer_base_conf(self):
        layer_class = self.layerParam["className"]
        runConfFile = open("./app/base_json/"+self.model_name+"/"+layer_class+".json", encoding="utf-8")
        runConfStr = runConfFile.read()
        runConf = json.loads(runConfStr)
        if "className" in self.layerParam.keys():
            runConf["class_name"] = self.layerParam["className"]
        if "name" in self.layerParam.keys():
            runConf["config"]["name"] = self.layerParam["name"]
        if "useBias" in self.layerParam.keys():
            runConf["config"]["use_bias"] = self.layerParam["useBias"]
        if "activation" in self.layerParam.keys():
            runConf["config"]["activation"] = self.layerParam["activation"]
        if "kernelInitializer" in self.layerParam.keys():
            runConf["config"]["kernel_initializer"]["class_name"] = self.layerParam["kernelInitializer"]
        if "biasInitializer" in self.layerParam.keys():
            runConf["config"]["bias_initializer"]["class_name"] = self.layerParam["biasInitializer"]
        return runConf

    def generate_layer_conf(self):
        runConf = self.generate_layer_base_conf()
        "dense"
        if "units" in self.layerParam.keys():
            runConf["config"]["units"] = self.layerParam["units"]
        "conv1d"
        if "strides" in self.layerParam.keys():
            runConf["config"]["strides"] = self.layerParam["strides"]
        if "padding" in self.layerParam.keys():
            runConf["config"]["padding"] = self.layerParam["padding"]
        if "kernelSize" in self.layerParam.keys():
            runConf["config"]["kernel_size"] = self.layerParam["kernelSize"]
        return runConf


class ConfNNParam(ConfBaseParam):
    def __init__(self, model_name, initiator, guest_param, hosts_param, model_param):
        super().__init__(model_name, initiator, guest_param, hosts_param, model_param)

    def generate_conf(self):
        runConf = self.generate_base()
        """
            maxIter:  模型最大更新次数
            batchSize: 
            layers:
            loss: 损失函数
            optimizer: 优化
            learningRate: 学习率
            earlyStop: 早退
            encodeLabel: 是否将标签编码为one-hot向量
            aggregateEveryNEpoch: 多少epoch 聚合一次模型
        """
        if "maxIter" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['max_iter'] = self.model_param['maxIter']
        if "batchSize" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['batch_size'] = self.model_param['batchSize']
        if "loss" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['loss'] = self.model_param['loss']
        if "earlyStop" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['early_stop']['early_stop'] = self.model_param['earlyStop']
        if "encodeLabel" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['encode_label'] = self.model_param['encodeLabel']
        if "aggregateEveryNEpoch" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['aggregate_every_n_epoch'] = self.model_param['aggregateEveryNEpoch']
        if "optimizer" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_nn_0']['optimizer'] = self.model_param['optimizer']
            if "learningRate" in self.model_param.keys():
                runConf['component_parameters']['common']['homo_nn_0']['optimizer']['learning_rate'] = self.model_param['learningRate']
        if "layers" in self.model_param.keys():
            layers = self.model_param['layers']
            for layer in layers:
                layerParam = BaseLayerParam(layer)
                conf = layerParam.generate_layer_conf()
                runConf['component_parameters']['common']['homo_nn_0']['nn_define']['config']['layers'].append(conf)
        return runConf




