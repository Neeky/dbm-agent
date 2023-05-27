# -*- coding: utf-8 -*-

"""在 MySQL 实例层面相关的函数

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

from pathlib import Path
from mysql.connector import connect
from dbma.core.configs import dbm_agent_config


def is_instance_exists(port: int = None):
    """检查给定端口的实例在当前的机器上是否存在(只要 datadir 存在就算是这个实例存在)

    Paramters:
    ----------
    port: int
        MySQL 端口

    Return:
    -------
    bool

    Exceptions:
    -----------
    Exception
    """
    datadir = Path(dbm_agent_config.mysql_datadir_parent) / str(port)
    return datadir.exists()
