# -*- coding: utf-8 -*-

"""异常树"""

from dbma.core.exception import DBMAgentException


class MySQLTemplateFileNotExistsException(DBMAgentException):
    """MySQL 配置文件模板不存在"""

    pass


class MySQLPkgFileNotExistsException(DBMAgentException):
    """MySQL 安装包文件模板不存在"""

    pass


class InstanceHasBeenInstalledException(DBMAgentException):
    """给定实例已经安装过了"""

    pass


class MySQLSystemdTemplateFileNotExists(DBMAgentException):
    """ """

    pass


class MySQLSystemdFileNotExists(DBMAgentException):
    """ """

    pass


class MySQLSystemdFileExists(DBMAgentException):
    pass


class MySQLDataDirectoryExists(DBMAgentException):
    """MySQL 数据目录已经存在"""

    pass


class NotSuportMySQLDirectoryType(DBMAgentException):
    """不支持的 MySQL 目录类型"""

    pass
