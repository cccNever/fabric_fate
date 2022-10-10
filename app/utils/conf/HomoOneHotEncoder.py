import json
from .base import ConfBase


class HomoOneHotEncoder(ConfBase):
    transformColNames = []

    def __init__(self, module):
        super().__init__(module)

    def generate_conf(self):
        conf = json.loads(open("./app/base_json/" + self.module + "/conf.json", encoding="utf-8").read())
        conf["transform_col_names"] = self.transformColNames
        return conf