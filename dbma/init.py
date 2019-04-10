"""
用于完成 dbm-agent 的初始化
1、创建 dbmc linux 用户
2、创建 /usr/local/dbm-agent/目录和它的子目录
3、修改 /usr/local/dbm-agent/目录的权限为chomd -R dbma:dbma /usr/local/dbm-agent
"""
import os

from dbma.utils import users,directors

def init_dbma(basedir="/usr/local/dbm-agent"):
    """
    1、创建用户 dbma
    2、创建目录树 /usr/local/dbm-agent/{etc,logs,pkgs}
    """
    # 创建 dbma 用户
    users.create_user_if_not_exists(user_name='dbma',uid=2048,gid=2048,group_name='dbm')
    # 创建目录
    directors.create_dbm_agent_directorys(basedir='/usr/local/dbm-agent')



    


    