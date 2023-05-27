# -*- coding: utf-8 -*-

"""MySQL 克隆插件备份逻辑

CLONE LOCAL DATA DIRECTORY [=] 'clone_dir';
"""


import os
import logging
from pathlib import Path
from datetime import datetime
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.bil.osuser import MySQLUser
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.commons import dbma_mysql_cnx


def backup_format(backup_type: str = None):
    """备份目录最后一级"""
    now = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    if backup_type.lower() == "clone":
        return "{}-backup-{}".format("clone", now)


def clone_local_data(port: int = 3306):
    """数据本机上的 MySQL 实例到本机上的磁盘

    Parameters:
    -----------
    port: int
        MySQL 端口号

    Returns:
    --------
    备份文件保存的目录
    """
    logging.info(messages.FUN_STARTS.format(fname()))
    backup_dir = (
        Path(dbm_agent_config.mysql_backupdir_parent)
        / str(port)
        / backup_format("clone")
    )
    logging.info("backup_di = '{}' ".format(backup_dir))

    if not backup_dir.parent.exists():
        logging.info("dir '{}' not exists .".format(backup_dir.parent))
        user = MySQLUser(port=port)
        os.makedirs(backup_dir.parent)
        user.chown(str(backup_dir.parent))
        logging.info("dir '{}' create complete. ".format(backup_dir.parent))

    with dbma_mysql_cnx(port) as cursor:
        sql = "CLONE LOCAL DATA DIRECTORY '{}';".format(str(backup_dir))
        logging.info("going go execute sql = '{}' ".format(sql))
        cursor.execute(sql)
    return str(backup_dir)
