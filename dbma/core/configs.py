# -*- encoding: utf-8 -*-

"""dbm-agent 的配置文件

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import json
import atexit
from pathlib import Path
from dataclasses import dataclass, asdict
from dbma.unix.version import VERSION
# TODO
# 这里之后要改成 dbma.core.version 文件中的 VERSION 值

DBM_AGENT_BASE_DIR = Path("/usr/local/dbm-agent/")
CONFIG_FILE_PATH = DBM_AGENT_BASE_DIR / "etc/dbm-agent.json"


@dataclass
class DBMAgentConfig(object):
    """
    """
    host: str = "127.0.0.1"
    port: int = 8086
    version: str = VERSION
    dbmcenter_url_prefix: str = "http://127.0.0.1:8080"
    # 单例模式
    _instance = None

    def make_register_data(self):
        """
        """
        return {
            'host': self.host,
            'port': self.port,
            'version': self.version
        }

    # 保存配置到磁盘
    def sync_to_disk(self):
        """对象的生命周期结束的时候保存信息到磁盘
        """
        if CONFIG_FILE_PATH.parent.exists():
            config = asdict(self)
            json_str = json.dumps(config, indent=4)
            with open(CONFIG_FILE_PATH, 'w') as c_file:
                c_file.write(json_str)
    
    # 读取配置文件
    def read_from_disk(self):
        """对象创建的时候从磁盘读取配置文件的内容
        """
        if CONFIG_FILE_PATH.exists():
            json_str = ""
            with open(CONFIG_FILE_PATH, 'r') as c_file:
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
        """从配置文件中读取配置、如果配置文件不存在就使用默认值
        """
        self.read_from_disk()


dbm_agent_config = DBMAgentConfig()


@dataclass
class DBMCenterUrlConfig(object):
    """
    """
    register_agent_url = "{0}/{1}".format(
        dbm_agent_config.dbmcenter_url_prefix, "apis/agents/")

    # 单例模式
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

# 进退寻出的时候保存配置对象到磁盘
atexit.register( lambda : dbm_agent_config.sync_to_disk())