# -*- encoding: utf-8 -*-

"""dbm-agent 内部数据接口

"""

from aiohttp import web
from dbma.core.router import routes
from dbma.loggers.loggers import get_logger
from dbma.unix.version import DBM_AGENT_VESION

logger = get_logger(__file__)

@routes.view("/dbm-agent")
class DbmAgentView(web.View):
    """
    dbm-agent http 接口实现
    """
    logger = logger.getChild("DbmAgentView")

    async def get(self):
        """返回 dbm-agent 的版本号信息
        """
        return web.json_response({"name": "dbm-agent", "version": DBM_AGENT_VESION})