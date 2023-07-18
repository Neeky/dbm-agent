# -*- coding: utf-8 -*-

"""Redis 环境的安装"""


import os
import tarfile
import logging
from pathlib import Path
from dbma.core import messages
from dbma.bil.fun import fname
from dbma.bil.osuser import RedisUser
from dbma.components.redis.exceptions import (
    RedisDatabaseDirectoryExistsException,
    RedisPkgFileNotExistsException,
)
from dbma.components.redis.commons import default_redis_pkg, redis_pkg_re_pattern
from dbma.bil.cmdexecutor import exe_shell_cmd
from dbma.components.redis.config import RedisConfig, RedisReplicaConfig
from dbma.components.redis.systemd import RedisSystemdConfig


def create_redis_user(port: int = 6379):
    """创建 redis 用户"""
    logging.info(messages.FUN_STARTS.format(fname()))

    # 根据端口号创建用户
    redis_user = RedisUser(port)
    redis_user.create()

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
    logging.info("going to chown .")
    redis_user.chown(str(database_dir), recursive=True)
    logging.info("chown down.")

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
    chown_database_dir_to_redis_user(port)

    logging.info(messages.FUN_ENDS.format(fname()))


def pkg_to_redis_basedir(pkg: Path = default_redis_pkg):
    """根据 pkg 的内容计算出对应的 basedir 的内容

    Parameters:
    ----------
    pkg : Path, optional
        Redis 的安装包, by default default_redis_pkg

    Returns:
    --------
    Path

    Exceptions:
    -----------
    ValueError: 给定的 pkg 与预先定义的正则对不上
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    # 1. 确认当前 redis 的版本号
    m = redis_pkg_re_pattern.match(pkg.name)
    if m is None:
        logging.error(messages.FUN_ENDS.format(fname()))
        raise ValueError("redis pkg name error pkg-name = '{}'.".format(pkg))
    version = m.group("redis_version")

    # 2. 返回 redis 版本应该对应的 basedir
    logging.info(messages.FUN_ENDS.format(fname()))
    return Path("/usr/local/redis-{}".format(version))


def pkg_to_redis_version(pkg: Path = default_redis_pkg):
    """_summary_

    Parameters
    ----------
    pkg : Path, optional
        Redis 的安装包程序, by default default_redis_pkg
    """
    return redis_pkg_re_pattern.match(pkg.name).group("redis_version")


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
    flag_file = pkg_to_redis_basedir(pkg) / ".dbm-agent-decompression.txt"
    if flag_file.exists():
        logging.info(messages.FUN_ENDS.format(fname()))
        return

    # 2. 检查 pkg 文件是否存在
    if not pkg.exists():
        msg = "redis pkg file '{}' not exists. ".format(str(pkg))
        logging.error(msg)
        raise RedisPkgFileNotExistsException(msg)

    # 3. 解压
    with tarfile.open(pkg) as tf:
        tf.extractall("/usr/local/")

    # 4. 创建标识文件
    with open(flag_file, "w") as flag_object:
        flag_object.write("dbma-agent")

    logging.info(messages.FUN_ENDS.format(fname()))


def start_redis(port: int = 6379):
    """启动 Redis

    Parameters
    ----------
    port : int, optional
        Redis 的端口号, by default 6379
    """
    exe_shell_cmd("systemctl start redisd-{}".format(port))


def stop_redis(port: int = 6379):
    """关闭 Redis

    Parameters
    ----------
    port : int, optional
        Redis 端口号, by default 6379
    """
    exe_shell_cmd("systemctl stop redisd-{}".format(port))


def install_redis(
    port: int = 6379, pkg: Path = default_redis_pkg, redis_config: RedisConfig = None
):
    """安装 Redis 并让其监控到指定端口

    Parameters:
    -----------
    port : int, optional
        Redis 要监听的端口号, by default 6379
    pkg : Path, optional
        Redis 的安装包, by default default_redis_pkg

    Exceptions:
    -----------

    """
    try:
        # 第一步：创建用户
        create_redis_user(port)
        # 第二步：创建数据目录
        create_redis_database_dir(port)
        # 第三步：解压
        decompression_redis_pkg(pkg)
        # 第四步：生成配置
        redis_config.generate_config_file()
        # 第五步：生成 systemd 配置
        redis_systemd_config = RedisSystemdConfig(port, pkg_to_redis_basedir(pkg))
        redis_systemd_config.generate_systemd_config()
        # 第六步：启动 redis
        start_redis(port)
    except Exception as err:
        msg = str(err)
        logging.exception(err)
        raise err


def install_resdis_master(port: int = 6379, pkg: Path = default_redis_pkg):
    """安装 Redis master 结点

    Parameters
    ----------
    port : int, optional
        Redis 端口号, by default 6379
    pkg : Path, optional
        Redis 安装包, by default default_redis_pkg
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    redis_master_config = RedisConfig(port)
    install_redis(port, pkg=pkg, redis_config=redis_master_config)

    logging.info(messages.FUN_ENDS.format(fname()))


def install_redis_replica(
    port: int = 6379, replicaof: str = "127.0.0.1 6379", pkg: Path = default_redis_pkg
):
    """安装 Redis replica 结点

    Parameters
    ----------
    port : int, optional
        Redis 结点的端口号, by default 6379
    master : str, optional
        Redis Master 结点的标识("host port"), by default "127.0.0.1 6379"
    pkg : Path, optional
        Redis 的安装包, by default default_redis_pkg
    """
    logging.info(messages.FUN_STARTS.format(fname()))
    logging.info("redis-port={}, redis-master={}, pkg={}".format(port, replicaof, pkg))

    redis_replica_config = RedisReplicaConfig(port=port, replicaof=replicaof)
    install_redis(port, pkg=pkg, redis_config=redis_replica_config)

    logging.info(messages.FUN_ENDS.format(fname()))
