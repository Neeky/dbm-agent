# -*- encoding: utf-8 -*-

""" dbm-agent 版本号管理
"""

DBM_AGENT_MAJOR_VERSION = 8
DBM_AGENT_MINOR_VERSION = 32
DBM_AGENT_PATCH_VERSION = 3


def _get_version_string():
    """
    返回字符串格式的版本号
    """
    return f"{DBM_AGENT_MAJOR_VERSION}.{DBM_AGENT_MINOR_VERSION}.{DBM_AGENT_PATCH_VERSION}"


# dbm-agent 版本号
DBM_AGENT_VESION = _get_version_string()
DBM_VERSION_NUMBER = DBM_AGENT_VESION
VERSION = DBM_AGENT_VESION
