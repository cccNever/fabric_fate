class DslBase:
    def __init__(self, module):
        self.module = module

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def generate_dsl(self):
        """
        生成conf
        :return:
        """
        dsl = {}
        return dsl