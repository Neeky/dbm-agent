# -*- coding: utf-8 -*-

"""dbm-agent 安装

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import shutil
import logging
import atexit
from pathlib import Path
from dbma.bil.osuser import DBMAUser
from dbma.core.configs import DBM_AGENT_BASE_DIR, DBMAgentConfig
from dbma.bil.net import get_ip_by_card_name
from dbma.core.exception import NetCardNotExistsException


def has_net_card_exists(net_card_name: str):
    """
    检查给定的网卡是否存在
    返回 True 说明给定的网卡存在，如果网卡不存在那么就会报异常 NetCardNotExistsException

    Parameters:
    -----------
    net_card_name: str

    Returns:
    --------
    bool

    Exceptions:
    -----------
    NetCardNotExistsException
    """
    ip = get_ip_by_card_name(net_card_name)
    if ip is None:
        logging.error("not find any ip on {}".format(net_card_name))
        raise NetCardNotExistsException(
            "net card '{}' not exists".format(net_card_name)
        )
    return True


def create_dbma_user():
    """
    创建 dbma 用户
    """
    logging.info("prepare create user dbma .")
    dbma_user = DBMAUser()
    dbma_user.create()
    logging.info("create user dbma done .")
    return dbma_user


def create_dbm_agent_and_database_directorys():
    """
    创建 /usr/local/dbm-agent/*
        /database/mysql/*
        /database/redis/*
    这三个目录和它的子目标
    """
    logging.info("prepare create directions .")
    if not DBM_AGENT_BASE_DIR.exists():
        DBM_AGENT_BASE_DIR.mkdir()

    for subdir in ("etc", "pkgs", "logs", "etc/templates"):
        item = DBM_AGENT_BASE_DIR / subdir
        if not item.exists():
            logging.info("go to create dir {} .".format(item))
            item.mkdir()

    # 创建 MySQL+Redis 会用的的一些公共目录
    DATABASE_DIR = Path("/database")
    if not DATABASE_DIR.exists():
        DATABASE_DIR.mkdir()

    for subdir in ("mysql", "mysql/data", "mysql/binlog", "redis"):
        item = DATABASE_DIR / subdir
        if not item.exists():
            logging.info("go to create dir {} .".format(item))
            item.mkdir()

    logging.info("create directions done .")


def init(net_card_name: str, dbm_center_url_prefix: str):
    """安装 dbm-agent"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s] - [%(threadName)s] - [%(pathname)s %(lineno)d line]  ~  %(message)s",
    )
    logging.info("start install dbm-agent .")

    # 检查给定的网卡是否存在
    has_net_card_exists(net_card_name)

    # 创建用户
    dbma_user = create_dbma_user()

    # 创建目录和子目录
    create_dbm_agent_and_database_directorys()

    # # 复制模板文件
    # logging.info("prepare copy template files .")
    # import dbma

    # basedir = Path(dbma.__file__).parent
    # src = basedir / "static/cnfs/"
    # dest = DBM_AGENT_BASE_DIR / "etc/templates"
    # shutil.copytree(src, dest, dirs_exist_ok=True)
    # logging.info("copy template files done .")

    # 更新配置并保存到磁盘
    dbm_agent_config = DBMAgentConfig()
    dbm_agent_config.host = get_ip_by_card_name(net_card_name)
    dbm_agent_config.dbmcenter_url_prefix = dbm_center_url_prefix
    dbm_agent_config.sync_to_disk()

    ## 权限调整
    dbma_user.chown(DBM_AGENT_BASE_DIR)

    # 给到启动 dbm-agent 的命令提示
    logging.info(
        "install dbm-agent done . \n dbm-agent start \n to start dbm-agent service . "
    )
