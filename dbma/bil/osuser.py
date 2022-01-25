# -*- coding: utf8 -*-
"""
实现操作系统用户的相关操作
"""

import os
import pwd
import grp

def is_user_exists(user:str)->bool:
    """检查给定的用户名是否存在

    Paramter
    --------
        user: str 用户名(操作系统层面)

    Return
    ------
        bool
    """

    try:
        pwd.getpwnam(user)
        return True
    except KeyError as err:
        return False
    except TypeError as err:
        return False



