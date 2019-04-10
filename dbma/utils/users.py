"""
linux 用户管理相关的通用工具
"""
import os
import pwd
import grp
import logging
import subprocess
import contextlib
from dbma.log import log_config

__ALL__ = ['is_user_exists','is_group_exists','is_root','get_uid_gid','sudo','create_user_if_not_exists']

def is_user_exists(user_name):
    """
    检查给定的用户是否存在
    """
    try:
        return pwd.getpwnam(user_name)
    except KeyError:
        return False

def is_group_exists(group_name):
    """
    检查给定的用户组是否存在
    """
    try:
        return grp.getgrnam(group_name)
    except KeyError:
        return False

is_root = lambda : os.getuid() == 0 and os.geteuid() == 0

def get_uid_gid(user_name):
    """
    返回给定用户的 (uid,gid) 组成的元组.
    如果用户不存在就返回 None
    """
    try:
        user = pwd.getpwnam(user_name)
        return user.pw_uid,user.pw_gid
    except KeyError as err:
        # 当给定的用户不存在的话会报 KeyError
        return None

@contextlib.contextmanager
def sudo(message="sudo"):
    """# sudo 上下文
    提升当前进程的权限到 root 以完成特定的操作，操作完成后再恢复权限
    """
    lg = logging.getLogger('dbma').getChild('utils.users')
    lg.warning(message)
    # 得到当前进程的 euid 
    old_euid = os.geteuid()
    # 提升权限到 root
    os.seteuid(0)
    yield message
    # 恢复到普通权限
    os.seteuid(old_euid)
    lg.warning('exits from root mode')

def create_group_if_not_exists(group_name='dbm',gid=2048):
    if is_group_exists(group_name) == False:
        with sudo(f'su root for create linux user group {group_name}'):
            cmd = f"groupadd -g{gid} {group_name}"
            subprocess.call(cmd,shell=True)

def create_user_if_not_exists(user_name='dbma',uid=2048,gid=2048,group_name='dbm'):
    """
    默认情况下 dbma 用户的uid 和 gid 都是 2048
    """
    if is_group_exists(group_name) == False:
        # 如果给定的用户组还不存在就先把用户组给创建出来
        create_group_if_not_exists(group_name,gid)
    
    if is_user_exists(user_name) == False:
        # 如果给定的用户不存在就把用户创建出来
        with sudo(f'su root for create linux user {user_name}'):
            cmd = f"useradd -g{gid} -u{uid} -r {user_name}"
            subprocess.call(cmd,shell=True)

def delete_user(user_name):
    """
    如果用户存在的话就删除，如果用户不存在就直接返回
    """
    if is_user_exists(user_name):
        with sudo(f'su root for delete linux user {user_name}'):
            cmd = f"userdel -r {user_name}"
            subprocess.call(cmd,shell=True)

def delete_group(group_name):
    """
    如果用户组存在的话就删除，如果用户组不存在就直接返回
    """
    if is_group_exists(group_name):
        with sudo(f'su root for delete linux group {group_name} '):
            cmd = f'groupdel {group_name}'
            subprocess.call(cmd,shell=True)
