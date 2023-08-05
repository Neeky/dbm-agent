# -*- coding: utf-8 -*-

"""dbm-agent http-server

"""

import os
import logging
from aiohttp import web
from urllib.parse import urlparse
from logging.handlers import RotatingFileHandler
from dbma.bil.daemon import start_daemon, stop_daemon
from dbma.bil.osuser import get_uid_gid, is_root, DBMAUser
from dbma.core.router import routes
from dbma.core.threads import backends
from dbma.core.configs import DBMAgentConfig
from dbma.core.views import dbmagentview as _
from dbma.components.mysql.backends.clears import start_clear_tasks
from dbma.components.mysql.views import defaultsview as _

dbm_agent_config = DBMAgentConfig()
dbm_center_host = urlparse(dbm_agent_config.dbmcenter_url_prefix).hostname


# 是否启动 dbmacenter 安全增强
@web.middleware
async def enforce_token(request: web.Request, handler):
    """验证 dbmcenter_token 值是否正确，如果这个值不对就直接返回 http-511"""
    logging.info("middleware starts enforce_token remoter '{}'".format(request.remote))

    # 只能是 token 对的上我们才处理
    token = request.headers.get("dbmcenter_token", "")
    if token == dbm_agent_config.dbmcenter_token:
        response = await handler(request)
        logging.info("middleware ends enforce_token {}".format(request.remote))
        return response

    message = "enforce_token error , missing dbmcenter_token or dbmcenter_token value error, remote = '{}' ".format(
        request.remote
    )
    # 指示客户端需要进行身份验证才能获得网络访问权限
    logging.warn(message)
    logging.warn("middleware ends enforce_token {}".format(request.remote))
    return web.json_response(
        {"message:": message, "error": message, "data": None}, status=511
    )


def start():
    """ """
    # 检查用户
    if not is_root():
        print("please use root use run this program! ")
        exit(1)

    dbma_user = DBMAUser()
    if not dbma_user.is_exists():
        print("please init dbm-agent before use. ")
        exit(2)

    # 切换到普通用户
    uid, gid = get_uid_gid(dbma_user.name)
    os.setegid(gid)
    os.seteuid(uid)

    # 以服务运行
    # dbm_agent_config = DBMAgentConfig()
    start_daemon(dbm_agent_config.pid_file)
    print("log file '{}' .".format(dbm_agent_config.log_file))

    # aiohttp.server 在启动的时候会向 stdout 打信息这个一点都不友好
    # 先关闭 stdout ，再让 stdout 指向 /dev/null
    os.close(1)
    os.open("/dev/null", os.O_CREAT | os.O_RDWR | os.O_APPEND)

    # 配置日志
    levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "error": logging.ERROR,
        "warn": logging.WARN,
    }
    handler = RotatingFileHandler(
        filename=dbm_agent_config.log_file,
        maxBytes=128 * 1024 * 1024,
        backupCount=8,
        encoding="utf8",
    )
    logging.basicConfig(
        handlers=[handler],
        level=levels[dbm_agent_config.log_level],
        format="[%(asctime)s %(levelname)s] - [%(threadName)s] - [%(pathname)s %(lineno)d line]  ~  %(message)s",
    )

    # 服务启动的日志头
    logging.info("-" * 21)
    logging.info("| start dbm-agent . |")
    logging.info("-" * 21)
    logging.info("logging-level {}".format(dbm_agent_config.log_level))

    # 启动后台线程
    logging.info("start backends threads .")
    backends.start_cycle_tasks()
    start_clear_tasks()

    # 启动 http 服务
    logging.info("going to start dbm-agent http-server bind on 0.0.0.0:8086 .")

    app = web.Application(middlewares=[enforce_token])
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port=8086, access_log=None)


def stop():
    """关闭 dbm-agent 服务"""
    dbm_agent_config = DBMAgentConfig()
    stop_daemon(dbm_agent_config.pid_file)
