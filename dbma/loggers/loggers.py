import os
import logging

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















