# -*- encoding: utf-8 -*-

"""aqua-agent http-server

"""

from aiohttp import web
from dbma.loggers.loggers import get_logger_name

async def hello_dbm_agent(request):
    log_file = get_logger_name(__file__)
    return web.Response(text=f"hello-dbm-agent {log_file}")

app = web.Application()
app.add_routes([web.get('/', hello_dbm_agent)])

def start_http_server():
    """启动 dbm-agent http 服务
    """
    web.run_app(app, host="0.0.0.0", port=8888)