# -*- encoding: utf8 -*-

class DBMABaseException(Exception):
    """
    DBMA 异常类
    """
    pass

class TemplateFileNotFoundError(DBMABaseException):
    """
    配置文件模板不存在
    """