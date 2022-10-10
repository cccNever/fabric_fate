import json
from app.utils.modelParam.base import ConfBaseParam


class ConfLRParam(ConfBaseParam):
    def __init__(self, model_name, initiator, guest_param, hosts_param, model_param):
        super().__init__(model_name, initiator, guest_param, hosts_param, model_param)

    def generate_lr_base(self, **kwargs):
        """
        :param
            maxIter:
            batchSize:
            optimizer:
            learningRate:
            penalty:L1 or L2
            alpha: 正则强度系数
            earlyStop: 早退
            decay: 学习率衰减系数
        :return:
        """
        runConf = self.generate_base()
        if "maxIter" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['max_iter'] = self.model_param['maxIter']
        if "batchSize" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['batch_size'] = self.model_param['batchSize']
        if "optimizer" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['optimizer'] = self.model_param['optimizer']
        if "learningRate" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['learning_rate'] = self.model_param['learningRate']
        if "penalty" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['penalty'] = self.model_param['penalty']
        if "alpha" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['alpha'] = self.model_param['alpha']
        if "earlyStop" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['early_stop'] = self.model_param['earlyStop']
        if "decay" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['decay'] = self.model_param['decay']
        return runConf


class ConfHomoLRParam(ConfLRParam):
    def __init__(self, model_name, initiator, guest_param, hosts_param, model_param):
        super().__init__(model_name, initiator, guest_param, hosts_param, model_param)

    def generate_conf(self):
        runConf = self.generate_lr_base()
        if "aggregateIters" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['aggregate_iters'] = self.model_param['aggregateIters']
        if "useProximal" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['use_proximal'] = self.model_param[
                'use_proximal']
        if "mu" in self.model_param.keys():
            runConf['component_parameters']['common']['homo_lr_0']['mu'] = self.model_param[
                'mu']
        return runConf



