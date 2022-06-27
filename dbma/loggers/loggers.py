# -*- encoding:utf8 -*-

"""
统一的日志入口
"""

import os
import logging


dbm_agent_logger = logging.getLogger('dbm_agent')

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
    /usr/local/python3/lib/xxx/dbma/core/httpserver.py ==> core.httpserver
    """
    if "dbma/" in file_name:
        # 如果是库文件
        _,sub_file = file_name.split("dbma/")
        sub_file = sub_file.replace(".py", "")
        sub_file.replace("/", ".")
        return "dbma" + sub_file 
    
    return "bin"