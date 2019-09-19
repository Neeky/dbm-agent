"""
实现 dbm-agent 守护进程的所有逻辑
1、读取配置文件、初始化全局配置
2、完成全局日志文件的配置
3、让 dbm-agent 以守护进程的方式进行
4、为不同目的的工作开启不同的线程
"""
# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
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

# 
#from . import __dbma_version
from dbma.daemon import start_daemon,stop_daemon
from dbma.initialization import is_user_exists,get_uid_gid,is_root


# exit 1

# 临时日志、再没有能读取配置文件前
#logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",level=logging.DEBUG)

def get_cnf(cnf_file:str)->dict:
    """
    从 /usr/local/dbm-agent/etc/my.cnf 中读取配置信息
    """
    # 如果配置文件不存在就直接打印配置文件并退出
    if not os.path.isfile(cnf_file):
        print(f"config file '{cnf_file}' not exists.",file=sys.stderr)
        sys.exit(1)
    #打开配置文件读取配置内容
    config = configparser.ConfigParser(allow_no_value=True,inline_comment_prefixes='#')
    config.read(cnf_file)
    return config['dbma']
    

def config_log(log_file:str,log_level='info'):
    """
    """
    logger = logging.getLogger('dbm-agent')
    if log_level.upper() == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level.upper() == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    
    file_handler = logging.handlers.RotatingFileHandler(filename=log_file,maxBytes=1024*1024*20,backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def heartbeat(heartbeat_api="https://127.0.0.1:8080/hosts/heartbeat",heartbeat_interval=300,net_if="ens33"):
    """
    收集主机层面的信息并上报
    """
    logger = logging.getLogger('dbm-agent').getChild(__name__)
    while True:
        try:
            # cpu 核心
            cpu_cores = psutil.cpu_count()

            # mem 大小
            mem_total_size,*_ = psutil.virtual_memory()

            # dbma 版本
            dbma_version = __dbma_version

            # 创建一个新的会话
            logger.info(f"post heartbeat info to dbmc {heartbeat_api}")
            session = requests.Session()
            session.headers.update({'Referer':f'{heartbeat_api}'})
            response = session.get(heartbeat_api,timeout=1)

            data = {
                'csrfmiddlewaretoken':session.cookies['csrftoken'],
                'cpu_cores':cpu_cores,
                'mem_total_size':mem_total_size,
                'dbma_version': __dbma_version
            }

            session.post(heartbeat_api,data=data,timeout=1) 
            logger.info(f"post data = {data}")        

        except Exception as err:
            logger.error(f"Exception ocurr will push heartbeat {str(err)}")
        finally:
            time.sleep(heartbeat_interval)
        







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
        print(f"must use root user to execute this program.",file=sys.stderr)
        sys.exit(1)
    
    # 解析配置文件中的 dbma 节点
    #[dbma]
    #dbmc_site = https://192.168.100.100
    #base_dir = /usr/local/dbm-agent/
    #config_file = etc/dbma.cnf
    #log_file = logs/dbma.log
    #log_level = info
    #user_name = dbma
    
    # 根据命令行参数中指定的 base-dir 和 config-file 打开日志文件
    config_file = os.path.join(args.base_dir,args.config_file)
    config = get_cnf(config_file)

    dbmc_site = config['dbmc_site']
    log_file = os.path.join(config['base_dir'],config['log_file'])
    log_level = config['log_level']
    user_name  = config['user_name']
    pid = config['pid']
    net_if = config['net_if']
    heartbeat_api = os.path.join(dbmc_site,config['heartbeat_api'])
    heartbeat_interval = int(config['heartbeat_interval'])
    
    # 检查配置文件中的 user_name 在操作系统级别是否存在
    if not is_user_exists(user_name):
        print(f" '{user_name}' not exists in current os ")
        sys.exit(2)
    
    # 切换到普通用户
    uid,gid = get_uid_gid(user_name)
    os.setegid(gid)
    os.seteuid(uid)

    # 以守护进程的方式运行
    start_daemon(pid)

    # ~~ v ~~ 以下代码都在守护进程状态下运行

    # 配置日志
    config_log(log_file,log_level)
    #
    logger = logging.getLogger('dbm-agent').getChild(__name__)
    logger.info('dbm-agent start')
    print(f"Successful start and log file save to '{log_file}' ")
    #
    #
    #所有的核心逻辑请在这里实现
    #
    # 

    #
    # 以下是主进程的逻辑、一个死循环不断的向 dbm-center 上报心跳信息
    # 这样守护进程就永远不会退出了
    heartbeat(heartbeat_api,heartbeat_interval,net_if)

    #t_heartbeat = threading.Thread(target=heartbeat,name="heartbeat-worker",daemon=True,
    #                               args=(heartbeat_api,heartbeat_interval,net_if))
    #t_heartbeat.start()
    #
    #time.sleep(300)

    





