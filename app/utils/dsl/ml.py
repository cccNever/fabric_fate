import json
from .base import DslBase


class ModelDsl(DslBase):
    def __init__(self, module, train_data, validate_data):
        super().__init__(module)
        self.train_data = train_data
        self.validate_data = validate_data

    def generate_dsl(self):
        dsl = json.loads(open("./app/base_json/" + self.module + "/dsl.json", encoding="utf-8").read())
        dsl["module"] = self.module
        dsl["input"]["data"]["train_data"] = [self.train_data + "_0" + ".data"]
        dsl["input"]["data"]["validate_data"] = [self.validate_data + "_0" + ".data"]
        return dsl
