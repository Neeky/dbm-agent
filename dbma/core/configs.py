# -*- encoding: utf-8 -*-

"""dbm-agent 的配置文件

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import json
import atexit
from pathlib import Path
from dataclasses import dataclass, asdict
from dbma.version import VERSION
from dbma.bil.osuser import DBMAUser

# TODO
# 这里之后要改成 dbma.core.version 文件中的 VERSION 值

DBM_AGENT_BASE_DIR = Path("/usr/local/dbm-agent/")
DBM_AGENT_ETC_DIR = DBM_AGENT_BASE_DIR / "etc"
CONFIG_FILE_PATH = DBM_AGENT_BASE_DIR / "etc/dbm-agent.json"


@dataclass
class DBMAgentConfig(object):
    """ """

    host: str = "127.0.0.1"
    port: int = 8086
    version: str = VERSION
    dbmcenter_url_prefix: str = "http://127.0.0.1:8080"
    pid_file: str = "/tmp/dbm-agent.pid"
    log_level: str = "info"
    log_file: str = "/tmp/dbm-agent.log"

    # backends_xxx 后端线程运行周期
    backends_register_time_interval: int = 15

    # 单例模式
    _instance = None

    # MySQL 相关的默认配置
    mysql_datadir_parent: str = "/database/mysql/data/"
    mysql_binlogdir_parent: str = "/database/mysql/binlog/"
    mysql_user_prefix: str = "mysql"
    mysql_default_version: str = "8.0.32"

    mysql_dbma_user: str = "dbma"
    mysql_dbma_password: str = "dbma@0352"
    # mysql_consts
    mysql_repl_user: str = "repl"
    mysql_repl_password: str = "2-4nw9A0-459st36"
    mysql_init_cnf: str = "/tmp/mysql-init.cnf"
    mysql_init_user_sql_file: str = "/tmp/mysql-init-user.sql"

    def make_register_data(self):
        """ """
        return {"host": self.host, "port": self.port, "version": self.version}

    # 保存配置到磁盘
    def sync_to_disk(self):
        """对象的生命周期结束的时候保存信息到磁盘"""
        if CONFIG_FILE_PATH.parent.exists():
            config = asdict(self)
            json_str = json.dumps(config, indent=4)
            with open(CONFIG_FILE_PATH, "w") as c_file:
                c_file.write(json_str)

    # 读取配置文件
    def read_from_disk(self):
        """对象创建的时候从磁盘读取配置文件的内容"""
        if CONFIG_FILE_PATH.exists():
            json_str = ""
            with open(CONFIG_FILE_PATH, "r") as c_file:
                json_str = c_file.read()

            try:
                json_data = json.loads(json_str)
                self.__dict__.update(json_data)
            except Exception as err:
                pass

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    # 从配置文件中读取配置项
    def __post_init__(self):
        """从配置文件中读取配置、如果配置文件不存在就使用默认值"""
        self.read_from_disk()


dbm_agent_config = DBMAgentConfig()


@dataclass
class DBMCenterUrlConfig(object):
    """ """

    register_agent_url = "{0}/{1}".format(
        dbm_agent_config.dbmcenter_url_prefix, "apis/agents/"
    )

    # 单例模式
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance


def _auto_save_to_disk():
    """ """
    if DBM_AGENT_BASE_DIR.exists():
        dbm_user = DBMAUser()
        dbm_user.chown(DBM_AGENT_BASE_DIR)
        dbm_agent_config.version = VERSION
        dbm_agent_config.sync_to_disk()
        dbm_user.chown(DBM_AGENT_BASE_DIR)


# 进退寻出的时候保存配置对象到磁盘
atexit.register(_auto_save_to_disk)
