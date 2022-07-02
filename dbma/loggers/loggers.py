# -*- encoding:utf8 -*-

"""
统一的日志入口
    1、创建日志对象
    1、如果配置文件存在就使用配置文件中配置的日志级别 TODO
"""

import os
import logging
from logging.handlers import RotatingFileHandler


dbm_agent_logger = logging.getLogger('dbm-agent')
dbm_agent_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d line - %(threadName)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler(filename="/tmp/dbm-agent.log", maxBytes=100 * 1024 * 1024, backupCount=10)
handler.setFormatter(formatter)
dbm_agent_logger.addHandler(handler)

def get_logger_name(file_name: str):
    """
    根据得到的 python 源文件名返回 logger 对象

    Paramater:
    ----------
    file_name: str

    Return:
    ------
      str

    Exsample:
    ---------
    /usr/local/python3/lib/xxx/dbma/core/httpserver.py ==> dbma.core.httpserver
    """
    if "dbma/" in file_name and ".py" in file_name:
      s = file_name.split(os.path.sep)
      index = s.index("dbma")
      name = ".".join(s[index:])
      if name.endswith(".py"):
        name = name[:-3]
      return name
    else:
      return os.path.basename(file_name)

def get_logger(file_name: str):
    """
    Paramater:
    ----------
        file_name: str
    Return:
    ------
      logging.Logger
    """
    return dbm_agent_logger.getChild(get_logger_name(file_name))