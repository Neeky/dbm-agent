"""
实现所有目录相关的操作
"""
import os
from dbma.utils import users

__ALL__ = ['create_dbm_agent_directorys']

def create_directory_if_not_exists(directory_path='/usr/local/dbm-agent',owner='dbma',mode=644):
    """
    如果目录还不存在就创建，如果已经存在了就直接返回
    """
    if not users.is_user_exists(owner):
        # 如果对应的用户不存在就报异常
        raise RuntimeError(f'user {owner} not exists in current system')

    if os.path.isfile(directory_path):
        # 如果给定的路径已经被一个文件占用，那么报不能创建目录的异常
        raise RuntimeError(f'exists file {directory_path} so can\'t create directory {directory_path}')
    
    with users.sudo(f'su root for create direnctory {directory_path}'):
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)
            uid,gid = users.get_uid_gid(owner)
            os.chown(directory_path,uid,gid)

def create_dbm_agent_directorys(basedir='/usr/local/dbm-agent'):
    """
    """
    create_directory_if_not_exists(basedir,owner='dbma')
    # 把当前目录切到 /usr/local/dbm-agent
    os.chdir(basedir)
    # 创建用于保存日志的目录
    create_directory_if_not_exists(os.path.join(basedir,'logs'),owner='dbma')
    create_directory_if_not_exists(os.path.join(basedir,'etc'),owner='dbma',mode=600)
    create_directory_if_not_exists(os.path.join(basedir,'etc/mysqlcnfs'),owner='dbma',mode=600)
    create_directory_if_not_exists(os.path.join(basedir,'pkgs'),owner='dbma')

    print("dbm-agent init compeleted .")


