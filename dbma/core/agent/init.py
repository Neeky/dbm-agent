# -*- encoding: utf-8 -*-

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


def init(net_card_name: str, dbm_center_url_prefix: str):
    """安装 dbm-agent"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s] - [%(threadName)s] - [%(pathname)s %(lineno)d line]  ~  %(message)s",
    )
    logging.info("start install dbm-agent .")

    # 检查给定的网卡是否存在
    ip = get_ip_by_card_name(net_card_name)
    if ip is None:
        logging.error("not find any ip on {}".format(net_card_name))
        return

    # 创建用户
    logging.info("prepare create user dbma .")
    dbma_user = DBMAUser()
    dbma_user.create()
    logging.info("create user dbma done .")

    # 创建目录和子目录
    logging.info("prepare create directions .")
    if not DBM_AGENT_BASE_DIR.exists():
        DBM_AGENT_BASE_DIR.mkdir()

    for subdir in ("etc", "pkgs", "logs", "etc/templates"):
        item = DBM_AGENT_BASE_DIR / subdir
        if not item.exists():
            item.mkdir()
    logging.info("create directions done .")

    # 复制模板文件
    logging.info("prepare copy template files .")
    import dbma

    basedir = Path(dbma.__file__).parent
    src = basedir / "static/cnfs/"
    dest = DBM_AGENT_BASE_DIR / "etc/templates"
    shutil.copytree(src, dest, dirs_exist_ok=True)
    logging.info("copy template files done .")

    # 更新配置并保存到磁盘
    dbm_agent_config = DBMAgentConfig()
    dbm_agent_config.host = ip
    dbm_agent_config.dbmcenter_url_prefix = dbm_center_url_prefix
    dbm_agent_config.sync_to_disk()

    ## 权限调整
    dbma_user.chown(DBM_AGENT_BASE_DIR)

    # 给到启动 dbm-agent 的命令提示
    logging.info(
        "install dbm-agent done . \n dbm-agent start \n to start dbm-agent service . "
    )
