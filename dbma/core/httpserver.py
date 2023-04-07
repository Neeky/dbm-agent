# -*- encoding: utf-8 -*-

"""dbm-agent http-server

"""

import os
import logging
from aiohttp import web
from logging.handlers import RotatingFileHandler
from dbma.bil.daemon import start_daemon, stop_daemon
from dbma.bil.osuser import get_uid_gid, is_root, DBMAUser
from dbma.core.router import routes
from dbma.core.threads import backends
from dbma.core.configs import DBMAgentConfig
from dbma.core.views import dbmagentview as _
from dbma.components.mysql.views import defaultsview as _


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
    dbm_agent_config = DBMAgentConfig()
    start_daemon(dbm_agent_config.pid_file)
    print("log file '{}' .".format(dbm_agent_config.log_file))

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

    # 启动 http 服务
    logging.info("going to start dbm-agent http-server bind on 0.0.0.0:8086 .")
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port=8086, access_log=None)


def stop():
    """关闭 dbm-agent 服务"""
    dbm_agent_config = DBMAgentConfig()
    stop_daemon(dbm_agent_config.pid_file)
