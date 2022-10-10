from app.utils.modelParam.base import ConfBaseParam


class ConfSecureBoostParam(ConfBaseParam):
    def __init__(self, model_name, initiator, guest_param, hosts_param, model_param, feature_param):
        super().__init__(model_name, initiator, guest_param, hosts_param, model_param, feature_param)

    def generate_conf(self, **kwargs):
        """

        :param kwargs:
            task_type : classification or regress
            numTrees: 树的个数
            maxDepth: 最大树深
            evalType: 输出类型
        :return:
        """
        runConf = self.generate_base()
        """define usual param"""
        if 'arbiter' in self.model_param.keys():
            runConf["role"]["arbiter"] = self.model_param["arbiter"]
        """user's param"""
        if 'numTress' in self.model_param.keys():
            runConf['component_parameters']['common']['homo_secureboost_0']['num_trees'] = self.model_param['numTress']
        if 'maxDepth' in self.model_param.keys():
            runConf['component_parameters']['common']['homo_secureboost_0']['tree_param']['max_depth'] = self.model_param['maxDepth']
        if 'taskType' in self.model_param.keys():
            runConf['component_parameters']['common']['homo_secureboost_0']['task_type'] = self.model_param['taskType']
            if self.model_param['taskType'] == 'classification':
                runConf['component_parameters']['common']['homo_secureboost_0']['objective_param']['objective'] = 'cross_entropy'
            else:
                if 'objective' in self.model_param.keys():
                    runConf['component_parameters']['common']['homo_secureboost_0']['objective_param']['objective'] = self.model_param['objective']
                else:
                    runConf['component_parameters']['common']['homo_secureboost_0']['objective_param']['objective'] = "lse"
        if 'evalType' in self.model_param.keys():
            runConf['component_parameters']['common']['evaluation_0']['eval_type'] = self.model_param['evalType']
        return runConf
