import json
from .base import ConfBase


class HomoFeatureBinning(ConfBase):
    method = "quantile"
    binIndexes = -1
    sampleBins = 100

    def __init__(self, module):
        super().__init__(module)

    def generate_conf(self):
        conf = json.loads(open("./app/base_json/" + self.module + "/conf.json", encoding="utf-8").read())
        conf["method"] = self.method
        conf["bin_indexes"] = self.binIndexes
        conf["sample_bins"] = self.sampleBins
        return conf
