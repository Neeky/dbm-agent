# -*- encoding: utf-8 -*-

"""dbm-agent http-server

"""

import os
import sys
from aiohttp import web
from dbma.core.router import routes
from dbma.loggers.loggers import get_logger
from dbma.core.views import dbmagentview as _
from dbma.core.views import javaview as _

def start_http_server():
    """启动 dbm-agent http 服务
    """
    # aiohttp 会向 std out 打印东西，把这个关闭掉
    try:
        devnull = open(os.devnull, 'w')
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        #sys.stdout.close()
    except Exception as err:
        get_logger(__file__).exception(err)
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port=8888, access_log=get_logger(__file__).getChild("aiohttp"))