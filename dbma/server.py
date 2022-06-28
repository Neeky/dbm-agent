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
from dbma.core.httpserver import start_http_server

def start(args):
    """
    1、检查当前用户是不是 root
    2、切换到普通用户状态
    3、以守护进程方式运行
    4、启动内置的 http 服务器
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
    print(f"Successful start and log file save to '/tmp/dbm-agent.log' ")

    # 所有的核心逻辑请在这里实现
    #
    # the cores .... 
    #
    # 最后一步启动 dbm-agent 内置的 http 服务器
    start_http_server()
