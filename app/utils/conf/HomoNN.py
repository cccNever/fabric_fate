import json
from .base import ConfBase


class BaseLayer:
    useBias = True
    activation = "relu"
    kernelInitializer = "GlorotUniform"
    biasInitializer = "Zeros"

    def __init__(self, className, name):
        self.className = className
        self.name = name

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def generate_base_conf(self):
        conf = json.loads(open("./app/base_json/" + "HomoNN/" + self.className + ".json", encoding="utf-8").read())
        conf["config"]["name"] = self.name
        conf["config"]["use_bias"] = self.useBias
        conf["config"]["activation"] = self.activation
        conf["config"]["kernel_initializer"]["class_name"] = self.kernelInitializer
        conf["config"]["bias_initializer"]["class_name"] = self.biasInitializer
        return conf


class Dense(BaseLayer):
    units = 1

    def __init__(self, className, name):
        super().__init__(className, name)

    def generate_conf(self):
        conf = self.generate_base_conf()
        conf["config"]["units"] = self.units
        return conf


class Conv1d(BaseLayer):
    stride = 1
    padding = 1
    kernelSize = 2

    def __init__(self, className, name):
        super().__init__(className, name)

    def generate_conf(self):
        conf = self.generate_base_conf()
        conf["config"]["strides"] = self.stride
        conf["config"]["padding"] = self.padding
        conf["config"]["kernel_size"] = self.kernelSize
        return conf


class HomoNN(ConfBase):
    maxIter = 10
    batchSize = -1
    layers = []
    loss = "binary_crossentropy"
    optimizer = "Adam"
    learningRate = 0.1
    earlyStop = "diff"
    encodeLabel = ""
    aggregateEveryNEpoch = 1

    def __init__(self, module):
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
        super.__init__(module)

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if key == "layers":
                for layer_param in value:
                    className = layer_param["class_name"]
                    name = layer_param["name"]
                    conf_module = __import__('app.utils.conf')
                    # 获取子类存在的py文件
                    layer_py = getattr(conf_module, "HomoNN")
                    # 获取子类
                    layer_class = getattr(layer_py, className)
                    layer = layer_class(className, name)
                    getattr(layer, 'set_attrs')(layer_param)
                    self.layers.append(layer)
            if hasattr(self, key) and key != "layers":
                setattr(self, key, value)

    def generate_conf(self):
        conf = json.loads(open("./app/base_json/" + self.module + "/conf.json", encoding="utf-8").read())
        conf['max_iter'] = self.maxIter
        conf['batch_size'] = self.batchSize
        conf['loss'] = self.loss
        conf['early_stop'] = self.earlyStop
        conf['encode_label'] = self.encodeLabel
        conf['aggregate_every_n_epoch'] = self.aggregateEveryNEpoch
        conf['optimizer'] = self.optimizer
        conf['learning_rate'] = self.learningRate
        for layer in self.layers:
            layerConf = layer.generate_conf()
            conf['nn_define']['config']['layers'].append(layerConf)
        return conf
