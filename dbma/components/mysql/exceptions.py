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


class MySQLSystemdFileNotExists(DBMAgentException):
    """ """

    pass
