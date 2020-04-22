"""解决 linux 的用户权限问题、实现 sudo
"""
import os
import logging
import contextlib
import subprocess

from .usermanage import LinuxUsers as lus
from . import errors

logger = logging.getLogger('dbm-agent').getChild(__name__)


@contextlib.contextmanager
def sudo(message="sudo"):
    """
    提升当前进程的权限到 root 以完成特定的操作，操作完成后再恢复权限
    """
    # 日志
    lgr = logging.getLogger("sudo")
    lgr.info("start")
    lgr.debug(message)

    # 得到当前进程的 euid
    old_euid = os.geteuid()

    # 提升权限到 root
    os.seteuid(0)
    lgr.debug(f"seteuid to 0")
    yield message

    # 恢复到普通权限
    lgr.debug(f"seteudi to {old_euid}")
    os.seteuid(old_euid)

    lgr.info("complete")


def chown(full_path="/usr/local/dbm-agent/", user_name='', group_name='', recusive=True):
    """
    """
    lgr = logger.getChild("chown")
    lgr.info("start.")

    # 检查用户是否存在
    if lus.is_user_exists(user_name) == False:
        raise errors.UserNotExistsError(user_name)

    if lus.is_group_exists(group_name) == False:
        raise errors.GroupNotExistsError(group_name)

    # 检查目录是否存在
    if os.path.exists(full_path) == False:
        raise errors.Error(f"file or dir '{full_path}' not eixsts.")

    # 调整用户和组
    with sudo("chown"):
        if recusive == True:
            cmd = f"chown -R {user_name}:{group_name} {full_path}"
        else:
            cmd = f"chown {user_name}:{group_name} {full_path}"

        subprocess.run(cmd, shell=True)

    lgr.info("complete.")
