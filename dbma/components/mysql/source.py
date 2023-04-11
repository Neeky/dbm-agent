# -*- encoding: utf-8 -*-

"""MySQL 备机相关的操作

作者: 蒋乐兴|neeky@live.com
时间: 2023-04
"""

import time
import logging
from pathlib import Path
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.components.mysql.commons import default_pkg
from dbma.components.mysql.install import install_mysql
from dbma.components.mysql.commons import make_mysql_writable


def install_mysql_source(
    port: int = 3306, pkg: Path = default_pkg, innodb_buffer_pool_size: str = "128M"
):
    """安装 MySQL Source 结点

    Parameters:
    -----------

    """
    #
    logging.info(messages.FUN_STARTS.format(fname()))
    install_mysql(port, pkg, innodb_buffer_pool_size=innodb_buffer_pool_size)

    # sleep
    time.sleep(7)
    make_mysql_writable(port)

    #
    logging.info(messages.FUN_ENDS.format(fname()))
