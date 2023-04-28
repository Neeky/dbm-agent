# -*- encoding: utf-8 -*-

"""Resdis 单机环境的安装"""


import os
import re
import shutil
import tarfile
import logging
from pathlib import Path
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.bil.osuser import RedisUser
from dbma.components.redis.exceptions import RedisDatabaseDirectoryExistsException
from dbma.components.redis.commons import (
    default_redis_pkg,
    redis_pkg_re_pattern,
    default_redis_port,
)


def create_redis_user(port: int = 6379):
    """创建 redis 用户"""
    logging.info(messages.FUN_STARTS.format(fname()))

    # 根据端口号创建用户
    redis_user = RedisUser(port)
    redis_user.create()

    logging.info(messages.FUN_ENDS.format(fname()))


def create_redis_database_dir(port: int = 6379):
    """创建 Redis 数据的工作目录
    Paramters:
    ----------
    port: int
        Redis 端口号

    Exceptions:
    -----------
    RedisDatabaseDirectoryExistsException
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    database_dir = Path("/database/redis/{}".format(port))
    if database_dir.exists():
        message = "redis database directory '{}' exists .".format(database_dir)
        raise RedisDatabaseDirectoryExistsException(message)
    # 创建数据目录
    os.makedirs(database_dir)

    logging.info(messages.FUN_ENDS.format(fname()))


def chown_database_dir_to_redis_user(port: int = 6379):
    """更新数据目录属组到 Redis 用户

    Parameters
    ----------
    port : int, optional
        Redis 端口号, by default 6379
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    redis_user = RedisUser(port)
    database_dir = Path("/database/redis/{}".format(port))
    redis_user.chown(str(database_dir))

    logging.info(messages.FUN_ENDS.format(fname()))


def pkg_to_redis_basedir(pkg: Path = default_redis_pkg):
    """根据 pkg 的内容计算出对应的 basedir 的内容

    Parameters:
    ----------
    pkg : Path, optional
        Redis 的安装包, by default default_redis_pkg

    Returns:
    --------
    str

    Exceptions:
    -----------
    ValueError: 给定的 pkg 与预先定义的正则对不上
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    # 1. 确认当前 redis 的版本号
    m = redis_pkg_re_pattern.match(pkg)
    if m is None:
        logging.error(messages.FUN_ENDS.format(fname()))
        raise ValueError("redis pkg name error .")
    version = m.group("redis-version")

    logging.info(messages.FUN_ENDS.format(fname()))
    return "/usr/local/redis-{}".format(version)


def decompression_redis_pkg(pkg: Path = default_redis_pkg):
    """解压 Redis 安装到 /usr/local/

    1、检查有没有解压过，如果有的话就路过
    2、检查给定的安装包是否存在、如果不存在就报错
    3、解压
    4、写入标识文件

    Parameters
    ----------
    pkg : Path, optional
        redis 安装包的全路径, by default default_redis_pkg
    """
    logging.info(messages.FUN_STARTS.format(fname()))
    # 1. 检查标识文件是否存在、如果存在说明解压过了，那么现在可以跳过这步解压的过程。
    #
    logging.info(messages.FUN_ENDS.format(fname()))
