import json
from .base import ConfBase


class SecureBoost(ConfBase):
    numTrees = 2
    maxDepth = 3
    taskType = "classification"
    evalType = "binary"
    objective = "lse"

    def __init__(self, module):
        super().__init__(module)

    def generate_conf(self):
        conf = json.loads(open("./app/base_json/" + self.module + "/conf.json", encoding="utf-8").read())
        conf['num_trees'] = self.numTrees
        conf['max_depth'] = self.maxDepth
        conf['task_type'] = self.taskType
        if self.taskType == "classification":
            conf['objective'] = 'cross_entropy'
        else:
            conf['objective'] = self.objective
        return conf
