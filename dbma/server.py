"""
实现 dbm-agent 守护进程的所有逻辑
1、读取配置文件、初始化全局配置
2、完成全局日志文件的配置
3、让 dbm-agent 以守护进程的方式进行
4、为不同目的的工作开启不同的线程
"""
# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import re
import os
import sys
import time
import psutil
import logging
import argparse
import requests
import threading
import subprocess
import configparser
import mysql.connector
import logging.handlers
from .daemon import start_daemon, stop_daemon
from .initialization import is_user_exists, get_uid_gid, is_root
from .monitor import HostMonitor
#from . import pusher
from . dbmacnf import cnf


def config_log(log_file: str, log_level='info'):
    """
    配置日志
    """
    logger = logging.getLogger('dbm-agent')
    if log_level.upper() == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level.upper() == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file, maxBytes=1024*1024*20, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def start(args):
    """
    1、检查当前用户是不是 root
    2、解析配置文件
    3、切换到普通用户状态
    4、以守护进程方式运行
    5、配置日志(logging)
    """
    # 检查当前的用户是不是 root 如果不是直接退出
    if not is_root():
        print(f"must use root user to execute this program.", file=sys.stderr)
        sys.exit(1)

    # 检查配置文件中的 user_name 在操作系统级别是否存在
    if not is_user_exists(cnf.user_name):
        print(f" '{cnf.user_name}' not exists in current os ")
        sys.exit(2)

    # 切换到普通用户
    uid, gid = get_uid_gid(cnf.user_name)
    os.setegid(gid)
    os.seteuid(uid)

    # 以守护进程的方式运行
    start_daemon(cnf.pid)

    # ~~ v ~~ 以下代码都在守护进程状态下运行

    # 配置日志
    log_file = os.path.join(cnf.base_dir, cnf.log_file)
    config_log(log_file, cnf.log_level)
    logger = logging.getLogger('dbm-agent').getChild(__name__)

    logger.info('dbm-agent start')
    print(f"Successful start and log file save to '{log_file}' ")
    #
    #
    # 所有的核心逻辑请在这里实现
    #
    #
    # 1 、 主机信息上报
    # system_monitor_thread = threading.Thread(
    #    target=pusher.push_system_monitor_item, daemon=True)
    # system_monitor_thread.start()
    # 1、为主机层面的监控单开一个线程
    hostmonitor = HostMonitor()
    hostmonitor.start()

    #
    # 以下是主进程的逻辑、一个死循环
    # 这样守护进程就永远不会退出了
    while True:
        time.sleep(300)
