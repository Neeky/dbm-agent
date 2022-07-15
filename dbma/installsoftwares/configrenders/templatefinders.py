# -*- encoding: utf-8 -*-
"""
加载配置文件模板

加载地址：
    1. /usr/local/dbm-agent/etc/templates/

加载算法：
    1. 加载最高版本的配置文件
    2. 加载默认配置文件
"""

import re
from dbma.bil import fs
from dbma.exceptions import TemplateFileNotFoundError

class TemplateFileFinder(object):
    """
    """
    template_file_pattern = ''
    
    def load(self):
        """
        Raise:
        ------
            TemplateFileNotFoundError:
        """
        raise NotImplementedError("finder() not implemented")


class DefaultTemplateFileFinder(TemplateFileFinder):
    """
    像 MySQL 我们要根据不同的版本来加载不同的配置文件，但是 zookeeper 类的我们可以简单的配置下就行了，不用区别版本。这样我们只要加载它的默认配置文件就行了。
    """
    def load(self):
        """
        """
        templates_dir = '/usr/local/dbm-agent/etc/templates/'
        for template_file_name in fs.listdir(templates_dir):
            if self.template_file_pattern.search(template_file_name):
                with open(fs.join(templates_dir, template_file_name)) as f:
                    return f.read()
        
        # 到这里返回说明没有找到
        raise TemplateFileNotFoundError(f"Template file not found with re '{self.template_file_pattern}' ")


class ZookeeperTemplateFileFinder(DefaultTemplateFileFinder):
    """
    """
    template_file_pattern = re.compile("^zoo.cnf.jinja$")

    
