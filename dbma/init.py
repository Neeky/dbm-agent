"""
用于完成 dbm-agent 的初始化
1、创建 dbmc linux 用户
2、创建 /usr/local/dbm-agent/目录和它的子目录
3、修改 /usr/local/dbm-agent/目录的权限为chomd -R dbma:dbma /usr/local/dbm-agent
"""
import os
import sys
import uuid
import configparser
from dbma.utils import users,directors

def init_dbma(args):
    """
    1、创建用户 dbma
    2、创建目录树 /usr/local/dbm-agent/{etc,logs,pkgs}
    """
    if not users.is_root():
        print(f'must use the root user execute this program.')
        sys.exit(1)
    # 创建 dbma 用户
    users.create_user_if_not_exists(user_name=args.user,uid=2048,gid=2048,group_name='dbm')
    # 创建目录
    directors.create_dbm_agent_directorys(args.basedir)
    uid,gid = users.get_uid_gid(args.user)
    os.setegid(gid)
    os.seteuid(uid)
    init_dbma_cnf_config_file(args)


def init_dbma_cnf_config_file(args):
    """
    根据命令行参数创建配置文件
    """
    parser = configparser.ConfigParser()
    parser['dbma'] = {'dbmc_site':args.dbmc_site,'dbma_uuid':uuid.uuid1(),'log_file':args.log_file}
    if not os.path.exists(args.config_file):
        with open(args.config_file,'w') as config_file_obj:
            parser.write(config_file_obj)
 


    


    