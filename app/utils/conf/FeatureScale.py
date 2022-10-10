import json
from .base import ConfBase


class FeatureScale(ConfBase):
    """
        method : "min_max_scale" and "standard_scale"
        mode : "normal" or "cap"
        feat_upper : 表示某一列的上限，如果mode为cap，feat_upper只能为0-1，表示百分数
        feat_lower：表示某一列的下限
        scale_names : 要进行归一化的列
    """
    method = "standard_scale"
    mode = "normal"
    featUpper = []
    featLower = []
    scaleNames = "None"

    def __init__(self, module):
        self.module = module

    def generate_conf(self):
        conf = json.loads(open("./app/base_json/" + self.module + "/conf.json", encoding="utf-8").read())
        conf["method"] = self.method
        conf["mode"] = self.method
        if self.scaleNames != "None":
            conf["scale_names"] = self.scaleNames
        conf["feat_upper"] = self.featUpper
        conf["feat_lower"] = self.featLower
        return conf


