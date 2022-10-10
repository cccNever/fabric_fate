import json
from .base import DslBase


class TrainDsl(DslBase):
    def __init__(self, module, input_data):
        super().__init__(module)
        self.input_data = input_data

    def generate_dsl(self):
        dsl = json.loads(open("./app/base_json/" + self.module + "/dsl.json", encoding="utf-8").read())
        dsl["module"] = self.module
        dsl["input"]["data"]["data"] = [self.input_data + "_0" + ".data"]
        return dsl
