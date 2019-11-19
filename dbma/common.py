
# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import pwd
import time
import psutil
import shutil
import socket
import logging
import pathlib
import subprocess
import contextlib
import configparser
from . import errors
from . import checkings

"""
为了最小的使用 sudo 、如果不为这个目标的话那 dbm-agent 直接就以 root 用户运行不完了
只有在需要用到的函数中开启 sudo
"""

logger = logging.getLogger('dbm-agent').getChild(__name__)

@contextlib.contextmanager
def sudo(message="sudo"):
    """# sudo 上下文
    提升当前进程的权限到 root 以完成特定的操作，操作完成后再恢复权限
    """
    # 得到当前进程的 euid 
    old_euid = os.geteuid()
    # 提升权限到 root
    os.seteuid(0)
    logger.debug(f"sudo context {message}")
    yield message
    # 恢复到普通权限
    os.seteuid(old_euid)

def create_group(group_name):
    """
    如果给定的“组”不存在就直接创建、已经存在就跳过
    """
    logger.debug(f"enter 'create_group' function {group_name}")
    if not checkings.is_group_exists(group_name):
        logger.debug(f"group not exists in current os {group_name} prepare create it")
        with sudo(f"create group {group_name}"):
            subprocess.run(f'groupadd {group_name}',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    logging.debug(f"exit 'create_group' function")
    
def create_user(user_name):
    """
    如果用户不存在就创建、用户已经存在就跳过创建步骤直接返回
    """
    logger.debug(f"enter 'create_user' function user_name={user_name}")
    if checkings.is_user_exists(user_name):
        logger.debug(f"exit 'create_user' function(user already exists)")
        return
    if 'mysql' in user_name:
        # 如果是要创建 MySQL 用户
        # 检查对应的用户组是不是存在
        if not checkings.is_group_exists('mysql'):
            create_group('mysql')
        with sudo(f"create user {user_name}"):
            subprocess.run(f"useradd -g mysql {user_name}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    elif 'zabbix' in user_name:
        if not checkings.is_group_exists('zabbix'):
            create_group('zabbix')
        with sudo(f"create user {user_name}"):
            subprocess.run(f"useradd -g zabbix {user_name}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    else:
        with sudo(f"create user {user_name}"):
            subprocess.run(f"useradd {user_name}", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    logger.debug(f"exit 'create_user' function")

def create_directory(path:str="/database/mysql/data/3306"):
    """
    """
    logger.debug(f"enter 'create_directory' fucntion path = {path} ")
    if not checkings.is_directory_exists(path):
        with sudo(f"create directory {path}"):
            p = pathlib.Path(path)
            p.mkdir(parents=True)
    logger.debug(f"exit 'create_directory' function ")

def delete_user(user_name):
    """
    """
    logger.debug(f"enter 'delete_user' function user_name={user_name}")
    if checkings.is_user_exists(user_name):
        with sudo(f"delete user {user_name}"):
            subprocess.run(f'userdel -r {user_name}',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    logger.debug(f"exit 'delete_user' function ")

def delete_group(group_name):
    """
    实现删除用户组的逻辑
    """
    logger.debug(f"enter 'delete_group' function group_name={group_name}")
    if checkings.is_group_exists(group_name):
        with sudo(f"delete group {group_name}"):
            subprocess.run(f"groupdel {group_name}",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    logger.debug(f"exit 'delete_group' function ")

def config_path(path="/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/",user_name="mysql3306"):
    """
    配置环境变量
    """
    with sudo("config path in /etc/profile."):
        # config /etc/profile
        is_path_in = False
        with open('/etc/profile','r') as prf_dst:
            for line in prf_dst:
                if f'export PATH={path}:$PATH' in line:
                    is_path_in = True
                    break
        if is_path_in == False:
            with open('/etc/profile','a') as prf_dst:
                prf_dst.write('\n')
                prf_dst.write(f"export PATH={path}:$PATH")
                prf_dst.write('\n')
        # config ~/
        if checkings.is_user_exists(user_name):
            is_path_in = False
            *_,home_dir,_ = pwd.getpwnam(user_name)
            with open(os.path.join(home_dir,'.bashrc')) as prf_dst:
                for line in prf_dst:
                    if f'export PATH={path}:$PATH' in line:
                        is_path_in = True
                        break
            if is_path_in == False:
                with open(os.path.join(home_dir,'.bashrc'),'a') as prf_dst:
                    prf_dst.write(f'\n')
                    prf_dst.write(f"export PATH={path}:$PATH")
                    prf_dst.write('\n')

def enable_service(service_name:str="mysqld-3306"):
    """
    配置 服务开机启动
    """
    with sudo(f"systemctl enable {service_name}"):
        subprocess.run([f'systemctl enable {service_name}'],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def config_mysql_include(version:str="mysql-8.0.17-linux-glibc2.12-x86_64"):
    """
    导出头文件
    """
    with sudo("export header file"):
        link = f"/usr/include/{version}"
        src = f"/usr/local/{version}/lib"
        if not os.path.islink(link):
            os.symlink(src,link)
        subprocess.run('ldconfig',stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def config_mysql_so(version:str="mysql-8.0.17-linux-glibc2.12-x86_64"):
    """
    导出共享库
    """
    soconf = os.path.join(f"/etc/ld.so.conf.d",version) 
    if not checkings.is_file_exists(soconf):
        with open(soconf,'w') as soobj:
            soobj.write(f"/usr/local/{version}/lib/")

def recursive_change_owner(path:str="/usr/local/mysql/",user:str="root",group:str="mysql"):
    """
    递归的设置 user 和 group
    """
    with sudo(f"change owner path={path} user={user} group={group}"):
        if os.path.isdir(path):
            shutil.chown(path,user,group)
            for item in os.listdir(path):
                recursive_change_owner(os.path.join(path,item),user,group)
        else:
            shutil.chown(path,user,group)

def get_all_local_ip()->set:
    """
    返回当前主机上的 IP 集合
    """
    eths = psutil.net_if_addrs()
    ips = set()
    for k,v in eths.items():
        for i in v:
            ips.add(i.address)
    return ips

def resolve_dns(ip:str="127.0.0.1",prefix:str=""):
    """
    在 /etc/hosts 中为 ip 添加一个记录
    """
    has_been_resolved = True
    try:
        socket.gethostbyaddr(ip)
    except socket.herror as err:
        has_been_resolved = False
        logger.warning(f"dns resolve {ip} fail prepare config /etc/hosts inner error {str(err)}")
    # 如果是本机也强制加一条
    if ip in get_all_local_ip():
        has_been_resolved = False
        logger.info(f"{ip} is a local ip force an record")
        # 防止重复加
        with open('/etc/hosts','r') as hosts:
            for line in hosts:
                if line.startswith(ip):
                    has_been_resolved = True

    with sudo('config /etc/hosts for dns'):
        if has_been_resolved == False:
            with open('/etc/hosts','a') as hosts:
                name = ip.replace('.','_')
                hosts.write(f"\n{ip}    {prefix}{name}")

def get_init_pwd(cnf_file:str="/usr/local/dbm-agent/etc/dbma.cnf"):
    """
    查询 dbma 配置文件中的 init_pwd 信息
    """
    parser = configparser.ConfigParser()
    parser.read(cnf_file)
    return parser['dbma']['init_pwd']

def wait_until_tcp_ready(ip:str="127.0.0.1",port:int=3306,timeout=3600):
    """
    检查 TCP 端口直到端口处理可用状态或超时
    """
    wait_seconds = 0
    while True:
        if checkings.is_port_in_use(ip,port) or wait_seconds >= timeout:
            break
        logger.info(f"wait for {ip}:{port} avaiable")
        time.sleep(1)
        wait_seconds = wait_seconds + 1

def config_hostname(name):
    with sudo('config host name'):
        subprocess.run(f"hostnamectl set-hostname {name} ",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)







