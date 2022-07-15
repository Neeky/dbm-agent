# -*- encoding: utf-8 -*-
"""
实现所有配置文件的渲染
"""
import copy

import jinja2
from dbma.loggers.loggers import get_logger
from dbma.exceptions import TemplateFileNotFoundError
from dbma.installsoftwares.configrenders.templatefinders import ZookeeperTemplateFileFinder

logger = get_logger(__file__)

class BaseConfigRender(object):
    """
    ConfigRender 只做两件事
    1.接收个性化参数
    2.把参数渲染到配置文件中去
    """
    logger = logger.getChild("BaseConfigRender")
    template_finder = None
    configs_defaults = {}
    configs = {}

    def __init__(self, configs=None):
        if configs is None:
            self.configs = copy.copy(self.configs_defaults)
    
    def __str__(self):
        """
        渲染配置文件
        """
        logger = self.logger.getChild("__str__")

        try:
            content = self.template_finder.load()
            template = jinja2.Template(content)
            return template.render(**self.configs)
        except TemplateFileNotFoundError as err:
            logger.error(err)
            raise err
        

class ZookeeperConfigRender(BaseConfigRender):
    """
    """
    template_finder = ZookeeperTemplateFileFinder()

    configs_defaults = {
        'data_dir': '/data/zookeeper'
    }
