"""
实现一个统一的日志入口

# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""

import os
import logging
from functools import wraps


root_logger = logging.getLogger("dbm-agent")

# 日志格式
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
root_logger.addHandler(stream_handler)

# 根据环境变量调整日志级别
# 1、默认的日志级别是 INFO
# 2、可能通过设置环境变量 “DBMA_LOGGER_LEVEL” 来指定日志级别，如果设置了一个不被支持的级别 dbm-agent 也会自动的调整成 INFO
logger_level = os.environ.get("DBMA_LOGGER_LEVEL","INFO")
logger_level = logger_level.strip().upper()

if logger_level == "INFO":
    root_logger.setLevel(logging.INFO)
elif logger_level == "DEBUG":
    root_logger.setLevel(logging.DEBUG)
elif logger_level == "WARNING":
    root_logger.setLevel(logging.WARNING)
elif logger_level == "ERROR":
    root_logger.setLevel(logging.ERROR)
else:
    root_logger.setLevel(logging.INFO)

# 为不同的模块创建日志对象
install_softwares_logger = root_logger.getChild("installsoftwares")
unix_logger = root_logger.getChild("unix")
loggers_logger = root_logger.getChild("loggers")

# 为方便使用实现函数装饰器、方法装饰器

def desc_instance_method(logger_level=logging.DEBUG):
    """
    实现实例方法的日志装饰器

    
    logger_level:
    ------------
        日志级别

    result:
    -------
        方法装饰器
    """
    def logger_instance_method(fun):
        """
        fun:
        ----
            要被装饰的实例方法

        returns:
        --------
            装饰之后的实例方法
        """
        @wraps(fun)
        def inner(*args,**kwargs):
            """
            """
            self,*_ = args
            self.logger.setLevel(logger_level)
            self.logger.debug(f"enter bound method {self.__class__.__name__}.{fun.__name__} with args self = {self} args = {args} kwargs = {kwargs} .")
            result = fun(*args,**kwargs)
            self.logger.debug(f"leave bound method {self.__class__.__name__}.{fun.__name__} with args self = {self}.")
            return result

        return inner

    return logger_instance_method

















