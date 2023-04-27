# -*- encoding: utf-8 -*-

"""Resdis 相关的异常"""

from dbma.core.exception import FileExistsException, FileNotExistsException


class RedisConfigTemplateFileNotExistsException(FileNotExistsException):
    """Redis 配置文件模板不存在"""

    pass
