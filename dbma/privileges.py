"""解决 linux 的用户权限问题、实现 sudo
"""
import os
import logging
import contextlib

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
