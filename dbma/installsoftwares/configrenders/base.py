# -*- encoding: utf-8 -*-
"""
实现所有配置文件的渲染
"""

class BaseConfigRender(object):
    """
    """
    template_file_name = ''
    config_file_name = ''

    def __init__(self, template_file_name, config_file_name):
        self.template_file_name = template_file_name
        self.config_file_name = config_file_name
    
    def render(self, data):
        """
        渲染配置文件
        """
        raise NotImplementedError()




