# -*- coding: utf8 -*-

"""
实现操作系统用户的相关操作
"""

import os
import contextlib
from threading import RLock

_user_sudo_lock = RLock()


@contextlib.contextmanager
def sudo(message="sudo"):
    """临时升级权限到 root ."""
    # 对于权限这个临界区的访问要串行化
    with _user_sudo_lock as lk:
        # 得到当前进程的 euid
        old_euid = os.geteuid()
        # 提升权限到 root
        os.seteuid(0)
        yield message
        # 恢复到普通权限
        os.seteuid(old_euid)
