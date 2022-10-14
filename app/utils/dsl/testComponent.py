import json
from .base import DslBase


class TestDsl(DslBase):
    def __init__(self, module, input_data, input_model):
        super().__init__(module)
        self.input_data = input_data
        self.input_model = input_model

    def generate_dsl(self):
        dsl = json.loads(open("./app/base_json/" + self.module + "/dsl.json", encoding="utf-8").read())
        dsl["module"] = self.module
        dsl["input"]["data"]["data"] = [self.input_data + "_1" + ".data"]
        dsl["input"]["model"] = [self.input_model + "_0" + ".model"]
        return dsl
