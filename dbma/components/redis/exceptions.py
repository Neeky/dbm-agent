# -*- coding: utf-8 -*-

"""Resdis 相关的异常"""

from dbma.core.exception import (
    FileExistsException,
    FileNotExistsException,
    DirectoryExistsException,
)


class RedisConfigTemplateFileNotExistsException(FileNotExistsException):
    """Redis 配置文件模板不存在"""

    pass


class RedisPkgFileNotExistsException(FileNotExistsException):
    """Redis 的安装包文件不存在"""

    pass


class RedisDatabaseDirectoryExistsException(DirectoryExistsException):
    """Redis 的数据目录已经存在"""

    pass
