class ConfBase:
    def __init__(self, module):
        self.module = module

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def generate_conf(self):
        """
        生成conf
        :return:
        """
        conf = {}
        return conf