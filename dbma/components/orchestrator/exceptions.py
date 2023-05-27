# -*- coding: utf-8 -*-

"""orchestrator 组件用到的异常对象
"""

from dbma.core.exception import DBMAgentException


class OrchHasBeenInstalledException(DBMAgentException):
    """orch 已经安装过了"""

    pass


class OrchPkgNotExistsException(DBMAgentException):
    """orch 安装包不存在"""

    pass
