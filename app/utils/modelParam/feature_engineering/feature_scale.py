# from app.utils.modelParam.feature_engineering.feature_engineering_base import FeatureEngineeringBase
#
#
# class FeatureScale(FeatureEngineeringBase):
#     def __init__(self):
#         super().__init__()
#         self.component_name = "featurescale"
#
#     def generate_conf(self, param):
#         self.conf[self.component_name + '_0'] = {}
#         self.conf[self.component_name + '_1'] = {}
#         if "method" in param.keys():
#             self.conf[self.component_name + '_0']["method"] = param['method']
#             self.conf[self.component_name + '_1']["method"] = param['method']
#         if "bin_indexes" in param.keys():
#             self.conf[self.component_name + '_0']["bin_indexes"] = param['bin_indexes']
#             self.conf[self.component_name + '_1']["bin_indexes"] = param['bin_indexes']
#         if "bin_names" in param.keys():
#             self.conf[self.component_name + '_0']["bin_names"] = param['bin_names']
#             self.conf[self.component_name + '_1']["bin_names"] = param['bin_names']
#         if "sample_bins" in param.keys():
#             self.conf[self.component_name + '_0']["sample_bins"] = param['sample_bins']
#             self.conf[self.component_name + '_1']["sample_bins"] = param['sample_bins']
#         return self.conf