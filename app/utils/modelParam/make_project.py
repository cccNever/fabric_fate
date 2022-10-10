# from app.utils.modelParam.feature_engineering.feature_scale import FeatureScale
# from app.utils.modelParam.feature_engineering.homo_feature_binning import HomoFeatureBinning
# from app.utils.modelParam.feature_engineering.homo_onehot_encoder import HomoOnehotEncoder
# from app.utils.modelParam.secure_boost import ConfSecureBoostParam
# from app.utils.modelParam.homo_logistic_regression import ConfHomoLRParam
# from app.utils.modelParam.homo_nn import ConfNNParam
#
#
# def make_project(type, initiator, guest_param, hosts_param, model_param):
#     if type == "HomoSecureboost":
#         ob = ConfSecureBoostParam("HomoSecureboost", initiator, guest_param, hosts_param, model_param)
#         return ob
#     if type == "HomoLR":
#         ob = ConfHomoLRParam("HomoLR", initiator, guest_param, hosts_param, model_param)
#         return ob
#     if type == "HomoNN":
#         ob = ConfNNParam("HomoNN", initiator, guest_param, hosts_param, model_param)
#         return ob
#
#
# def generate_feature_conf(runConf,feature_param):
#     feature_conf = dict()
#     for module in feature_param.keys():
#         if module == "FeatureScale" and feature_param["FeatureScale"] != {}:
#             feature_conf.update(FeatureScale().generate_conf(feature_param["FeatureScale"]))
#         elif module == "HomoOnehotEncoder" and feature_param["HomoOnehotEncoder"] != {}:
#             feature_conf.update(HomoOnehotEncoder().generate_conf(feature_param["HomoOnehotEncoder"]))
#         elif module == "HomoFeatureBinning" and feature_param["HomoFeatureBinning"] != {}:
#             feature_conf.update(HomoFeatureBinning().generate_conf(feature_param["HomoFeatureBinning"]))
#     runConf["component_parameters"]["common"].update(feature_conf)
#     return runConf