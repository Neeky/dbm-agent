# -*- coding: utf-8 -*-

"""MySQL 备机相关的操作

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import time
import logging
from pathlib import Path
from mysql.connector import connect
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.core.configs import dbm_agent_config
from dbma.components.mysql.install import install_mysql
from dbma.components.mysql.commons import get_mysql_version
from dbma.components.mysql.commons import dbma_mysql_cnx


def get_change_source_stmt(version: str = None):
    """根据版本号返回 change master|source 语句

    Parameters:
    -----------
    version: str
        MySQL 版本号

    Return:
    -------
    str
    """
    stmt = "CHANGE REPLICATION SOURCE TO SOURCE_USER='{}', SOURCE_PASSWORD='{}', SOURCE_HOST='{}', SOURCE_PORT={}, SOURCE_AUTO_POSITION=1, SOURCE_SSL=1;"
    if not version.startswith("8.0"):
        stmt = "CHANGE REPLICATION MASTER TO MASTER_USER='{}', MASTER_PASSWORD='{}', MASTER_HOST='{}', MASTER_PORT={}, MASTER_AUTO_POSITION=1, MASTER_SSL=1;"
    return stmt


def get_start_replica_stmt(version: str = None):
    """根据版本号返回 start replica|slave 语句

    Parameters:
    -----------
    version: str
        MySQL 版本号

    Return:
    -------
    str
    """
    stmt = "start replica;"
    if not version.startswith("8.0"):
        stmt = "start slave;"
    return stmt


def change_replica_to(
    port: int = None,
    version: str = None,
    source_ip: str = None,
    source_port: int = None,
):
    """变更复制关系

    Parameters:
    -----------
    port: int
        replica 实例的端口号

    source_host: str
        source 实例的主机号

    source_port: int
        source 实例的端口号

    Returns:
    --------
    None
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    stmt = get_change_source_stmt(version)
    stmt = stmt.format(
        dbm_agent_config.mysql_repl_user,
        dbm_agent_config.mysql_repl_password,
        source_ip,
        source_port,
    )
    with dbma_mysql_cnx(port) as cursor:
        cursor.execute(stmt)
        logging.info(stmt)

    logging.info(messages.FUN_ENDS.format(fname()))


def start_replica(
    port: int = None,
    version: str = None,
    source_ip: str = None,
    source_port: int = None,
):
    """变更复制关系

    Parameters:
    -----------
    port: int
        replica 实例的端口号

    source_host: str
        source 实例的主机号

    source_port: int
        source 实例的端口号

    Returns:
    --------
    None
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    stmt = get_start_replica_stmt(version)
    with dbma_mysql_cnx(port) as cursor:
        cursor.execute(stmt)
        logging.info(stmt)

    logging.info(messages.FUN_ENDS.format(fname()))


def install_mysql_replica(
    port: int = 3306,
    pkg: Path = None,
    innodb_buffer_pool_size: str = "128M",
    source_ip: str = None,
    source_port: int = None,
):
    """安装 MySQL Replica 结点

    Paramters:
    ----------
    port: int
        Replica 实例的端口号

    pkg: Path
        Replica 实例的安装包

    innodb_buffer_pool_size: str
        innodb_buffer_pool_size 的大小

    source_ip: str
        Source 实例的主机 ip

    source_port: int
        Source 实例的端口
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    version = get_mysql_version(pkg.name)

    # 第一步安装 MySQL Replica 结点
    install_mysql(port, pkg, innodb_buffer_pool_size)

    # MySQL 安装之后要 sleep 一下，希望这个时候 MySQL 的监听已经完成
    seconds = 11
    time.sleep(seconds)

    # 第二步执行 change-master-to
    change_replica_to(port, version, source_ip=source_ip, source_port=source_port)

    # 第三步执行 start-replica
    start_replica(port, version, source_ip=source_ip, source_port=source_port)

    logging.info(messages.FUN_ENDS.format(fname()))
