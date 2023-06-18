# -*- coding: utf-8 -*-

"""
背景: 
    当我们卸载一个对应的 MySQL 实例之后、它的数据目录、Binlog 目录、配置文件都应该被清理掉。把个比较它之前的数据目录可能是 
    '/database/mysql/data/3306' 当我们执行卸载操作之后并不会真正的删除数据，而是给它 rename 成了 '3306-backup-2023-06-17T14-45-21-949788'
    由于使用的是 rename 所以回退的时候还是比较方便的
    
    但是这个又带来了一个问题，对于类似 '3306-backup-2023-06-17T14-45-21-949788' 的目录我们什么时候清理呢？默认是 3 天之后在后台线程中清理它；这里
    我们就来实现这个功能。
    
    一个线程定期的检查有哪些实例可以清理，生成任务丢到队列里面去；
    另一个线程从队列中取出任务，然后慢慢的删除对应的文件
    
"""

import re
import glob
from pathlib import Path
from collections import deque
from dataclasses import dataclass
from dbma.core.configs import dbm_agent_config


@dataclass
class ClearTask(object):
    """
    清理任务对象
    """

    # is_cnf_cleared: bool
    # is_binlog_cleared: bool
    # is_data_cleared: bool

    dir_path: Path


clear_tasks = deque(maxlen=1024)

backup_dir_re_pattern = re.compile(
    r"(?P<port>[0-9]{4,4})-backup-(?P<dt>\d{4}-\d{1,2}-\d{1,2}T\d{1,2}-\d{1,2}-\d{1,2}-\d{4,6})"
)


def scan_data_dir_gen_task():
    """只扫描 binlog 目录和 data 目录；至于 backup 目录这个是交由备份子系统完成

    Returns:
    --------
    ClearTask
    """
    result = []
    # 检查 data 目录下的备份
    data_dir_path = (
        dbm_agent_config.mysql_datadir_parent + "*"
        if dbm_agent_config.mysql_datadir_parent.endswith("/")
        else dbm_agent_config.mysql_datadir_parent + "/*"
    )
    for instance_path in glob.glob(data_dir_path):
        match = backup_dir_re_pattern.search(instance_path)
        if match:
            result.append(instance_path)

    # 检查 binlog 目录下的备份
    binlog_dir_path = (
        dbm_agent_config.mysql_binlogdir_parent + "*"
        if dbm_agent_config.mysql_binlogdir_parent.endswith("/")
        else dbm_agent_config.mysql_binlogdir_parent + "/*"
    )
    for binlog_path in glob.glob(binlog_dir_path):
        match = backup_dir_re_pattern.search(binlog_path)
        if match:
            result.append(binlog_path)
    return result
