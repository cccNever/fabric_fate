# from app.utils.modelParam.feature_engineering.feature_engineering_base import FeatureEngineeringBase
#
#
# class HomoOnehotEncoder(FeatureEngineeringBase):
#     def __init__(self):
#         super().__init__()
#         self.component_name = "homoonehotencoder"
#
#     def generate_conf(self,param):
#         self.conf[self.component_name + '_0'] = {}
#         self.conf[self.component_name + '_1'] = {}
#         if "transform_col_indexes" in param.keys():
#             print("transform_col_indexes")
#             self.conf[self.component_name + '_0']["transform_col_indexes"] = param['transform_col_indexes']
#             self.conf[self.component_name + '_1']["transform_col_indexes"] = param['transform_col_indexes']
#         if "transform_col_names" in param.keys():
#             self.conf[self.component_name + '_0']["transform_col_names"] = param['transform_col_names']
#             self.conf[self.component_name + '_1']["transform_col_names"] = param['transform_col_names']
#         if "need_alignment" in param.keys():
#             self.conf[self.component_name + '_0']["need_alignment"] = param['need_alignment']
#             self.conf[self.component_name + '_1']["need_alignment"] = param['need_alignment']
#         return self.conf