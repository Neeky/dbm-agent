# -*- coding: utf-8 -*-

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


# region directorys
class DirectoryExistsException(DBMAgentException):
    """目录已经存在"""

    pass


class DirectoryNotExistsException(DBMAgentException):
    """目录不存在的异常"""

    pass


# endregion directorys


# region netcards
class NetCardNotExistsException(DBMAgentException):
    """网卡不存在"""

    pass


# endregion netcards
