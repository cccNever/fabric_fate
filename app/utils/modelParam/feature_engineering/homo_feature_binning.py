# from app.utils.modelParam.feature_engineering.feature_engineering_base import FeatureEngineeringBase
#
#
# class HomoFeatureBinning(FeatureEngineeringBase):
#     def __init__(self):
#         super().__init__()
#         self.component_name = 'homofeaturebinning'
#
#     def generate_conf(self,param):
#         self.conf[self.component_name + '_0'] = {}
#         self.conf[self.component_name + '_1'] = {}
#         if "method" in param.keys():
#             self.conf[self.component_name + '_0']["method"] = param['method']
#             self.conf[self.component_name + '_1']["method"] = param['method']
#         if "mode" in param.keys():
#             self.conf[self.component_name + '_0']["mode"] = param['mode']
#             self.conf[self.component_name + '_1']["mode"] = param['mode']
#         if "feat_upper" in param.keys():
#             self.conf[self.component_name + '_0']["feat_upper"] = param['feat_upper']
#             self.conf[self.component_name + '_1']["feat_upper"] = param['feat_upper']
#         if "feat_lower" in param.keys():
#             self.conf[self.component_name + '_0']["feat_lower"] = param['feat_lower']
#             self.conf[self.component_name + '_1']["feat_lower"] = param['feat_lower']
#         if "scale_col_indexes" in param.keys():
#             self.conf[self.component_name + '_0']["scale_col_indexes"] = param['scale_col_indexes']
#             self.conf[self.component_name + '_1']["scale_col_indexes"] = param['scale_col_indexes']
#         if "scale_names" in param.keys():
#             self.conf[self.component_name + '_0']["scale_names"] = param['scale_names']
#             self.conf[self.component_name + '_1']["scale_names"] = param['scale_names']
#         if "with_mean" in param.keys():
#             self.conf[self.component_name + '_0']["with_mean"] = param['with_mean']
#             self.conf[self.component_name + '_1']["with_mean"] = param['with_mean']
#         if "feat_lower" in param.keys():
#             self.conf[self.component_name + '_0']["with_std"] = param['with_std']
#             self.conf[self.component_name + '_1']["with_std"] = param['with_std']
#         return self.conf
