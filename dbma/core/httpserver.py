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

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from dbma.bil.daemon import start_daemon, stop_daemon
from dbma.bil.osuser import get_uid_gid, is_root, DBMAUser
from dbma.core.configs import DBMAgentConfig


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
    web.run_app(app, host="0.0.0.0", port=8888, access_log=None)


def start():
    """
    """
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
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'error': logging.ERROR,
        'warn': logging.WARN
    }
    handler = RotatingFileHandler(filename=dbm_agent_config.log_file,
                                  maxBytes=128 * 1024 * 1024, backupCount=8, encoding="utf8")
    logging.basicConfig(handlers=[handler], level=levels[dbm_agent_config.log_level],
                        format="[%(asctime)s %(levelname)s] - [%(threadName)s] - [%(pathname)s %(lineno)d line]  ~  %(message)s")
    
    # 启动 http 服务
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port=8888, access_log=None)
