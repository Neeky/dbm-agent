#!/usr/bin/env python3
import os
import logging
from logging import handlers

__ALL__ = ['get_root_logger','log_config']

def log_config(root_logger_name='dbm-agent',filename="logs/dbma.log",max_bytes=1024*1024*64,backup_count=7):
    """
    """
    
    logger = logging.getLogger(root_logger_name)
    logger.setLevel(logging.DEBUG)
    #当文件大小达到64M时就创建一个新的文件，用于记录日志，留7个备份
    file_handler = handlers.RotatingFileHandler(filename,maxBytes=max_bytes,backupCount=backup_count)
    formater = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s]    %(message)s")
    file_handler.setFormatter(formater)
    logger.addHandler(file_handler)
    return logger

def get_root_logger(logger_name="dbm-agent"):
    """
    """
    return logging.getLogger('dbm-agent')
    