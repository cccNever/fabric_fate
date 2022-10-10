import json
from .base import ConfBase


class HomoLR(ConfBase):
    maxIter = 10
    batchSize = -1
    optimizer = "sgd"
    learningRate = 0.1
    penalty = "L2"
    alpha = 0.01
    earlyStop = "diff"
    decay = 1

    def __init__(self, module):
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
        super().__init__(module)

    def generate_conf(self):
        conf = json.loads(open("./app/base_json/" + self.module + "/conf.json", encoding="utf-8").read())
        conf['max_iter'] = self.maxIter
        conf['batch_size'] = self.batchSize
        conf['optimizer'] = self.optimizer
        conf['learning_rate'] = self.learningRate
        conf['penalty'] = self.penalty
        conf['alpha'] = self.alpha
        conf['early_stop'] = self.earlyStop
        conf['decay'] = self.decay
        return conf

