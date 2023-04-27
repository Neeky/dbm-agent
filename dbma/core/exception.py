# -*- encoding: utf-8 -*-

"""dbm-agent exceptions

"""


class DBMAgentException(Exception):
    """所有 dbm-agent 异常的基类"""

    pass


# region files


class FileExistsException(DBMAgentException):
    """文件不存在异常"""

    pass


class FileNotExistsException(DBMAgentException):
    """文件已经存在异常"""

    pass


# endregion files
