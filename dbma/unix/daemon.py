"""
实例 unix | linux 下守护进程

1、实现守护进程的所有功能
2、当应用以守护进程模式运行时把 stderro 的转出重新定向到文件
"""

import logging
from logging.handlers import RotatingFileHandler
from dbma.loggers import root_logger,stream_handler

def change_logger_handler(log_file_path:str="/usr/local/dbm-agent/logs/dbma.log"):
    """
    把 root_logger 设置成向文件打日志

    log_file_path
    -------------
        str: 日志文件的全路径
    """
    # 不再向 stdout 打日志。
    root_logger.removeHandler(stream_handler)

    # 
    rfh = logging.RotatingFileHandler(log_file_path,maxBytes=1024*1024*64,backupCount=10,encoding='utf8')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    rfh.setFormatter(formatter)
    root_logger.addHandler(rfh)

