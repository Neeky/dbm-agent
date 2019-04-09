"""
linux 用户管理相关的通用工具
"""
import os
import pwd
import logging
import subprocess
import contextlib

__ALL__ = ['is_user_exists','is_root','get_uid_gid','sudo','create_user_if_not_exists']

# 查询指定的用户是否存在
is_user_exists = lambda user_name: True if pwd.getpwnam(user_name) else False

# 查询当前用户是不 root 用户
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
    # 得到当前进程的 euid 
    old_euid = os.geteuid()
    # 提升权限到 root
    os.seteuid(0)
    yield message
    # 恢复到普通权限
    os.seteuid(old_euid)


def create_user_if_not_exists(user_name='dbma',uid=2049,gid=2049,group_name='dbm'):
    """
    默认情况下 dbma 用户的uid 和 gid 都是 2049
    """
    with sudo():
        cmd = f"groupadd -g{gid} {group_name} && useraddd -u{uid} -r {user_name}"
        subprocess.call(cmd,shell=True)
