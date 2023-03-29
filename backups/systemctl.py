"""实现 systemctl 的相关操作
"""

import re
import os
import logging
import shutil
from . import privileges as prv
from . import errors
from .usermanage import LinuxUsers as lus
from .ldconfig import ldconfig
from .dbmaconfig import ConfigMixin
from jinja2 import Environment, FileSystemLoader


logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseSystemctl(ConfigMixin):
    """实现 systemctl 的动态渲染。
    """
    logger = logger.getChild("BaseSystemctl")

    def __init__(self, template_file=""):
        """
        """
        self.template_file = template_file

    def pre_checks(self):
        """
        """
        if self.template_file == "":
            logger.warning("template_file = '' ")
            errors.FileNotExistsError(
                f"template file '{self.template_dir}/{self.template_file}' not exists.")

    def __str__(self):
        """
        """
        tmpl = Environment(loader=FileSystemLoader(
            searchpath=self.template_dir)).get_template(self.template_file)

        tmpl.globals = self.__dict__

        return tmpl.render()

    __repr__ = __str__

    def render_to(self, config_file_full_path=""):
        """
        """
        raise NotImplementedError("请在子类中实现 BaseSystemctl.render_to 方法。")
