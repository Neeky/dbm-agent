"""
实现若干检查项
"""
# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import re
import os
import sys
import grp
import pwd
import socket
import logging
from . import errors

logger = logging.getLogger('dbm-agent').getChild(__name__)

def is_port_in_use(ip:str="127.0.0.1",port:int=3306)->bool:
    """
    检查对应的 IP 和端口是否已经被占用
    """
    global logger
    logger.debug(f"check {(ip,port)} is in use or not")
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((ip,port))
        sock.close()
        return True
    except ConnectionRefusedError as err:
        return False
    return False

def is_user_exists(user_name:str='root')->bool:
    """
    检查对应的用户名在操作系统中是否存在
    """
    global logger
    logger.debug(f"check user '{user_name}' exists in current os ")
    try:
        pwd.getpwnam(user_name)
        return True
    except KeyError as err:
        return False

def is_group_exists(group_name:str='root')->bool:
    """
    检查对应经的组名在操作系统中是否存在
    """
    global logger
    logger.debug(f"check group '{group_name}' exists in current os ")
    try:
        grp.getgrnam(group_name)
        return True
    except KeyError as err:
        return False

def is_file_exists(file_path:str="/etc/my.cnf")->bool:
    """
    检查对应的文件是否存在
    """
    global logger
    logger.debug(f"check file '{file_path}' exists or not")
    return os.path.isfile(file_path)

def is_directory_exists(directory_path:str='/tmp/'):
    """
    检查对应的目录是否存在
    """
    global logger
    logger.debug(f"check directory '{directory_path}' exists or not")  
    return os.path.isdir(directory_path)

def is_an_supported_mysql_version(pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz")->bool:
    """
    检查给定的 mysql 版本是否被支持
    """
    global logger
    logger.debug(f"check mysql version '{pkg}' is supported or not")

    if not re.search(r"[\d]\.[\d].[\d]{1,2}-linux-glibc2.12-x86_64",pkg):
        # 8.0.17-linux-glibc2.12-x86_64 这样的形式都匹配不了，那绝对是 False
        return False
    # 8.0 的最小支持版本为 8.0.17 
    return re.search(r"([\d]\.[\d].[\d]{1,2})-linux-glibc2.12-x86_64",pkg).group(1) >= '8.0.17'
    










    