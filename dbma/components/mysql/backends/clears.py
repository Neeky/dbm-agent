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
import time
import logging
from pathlib import Path
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from dbma.bil.fun import fname
from dbma.bil.fs import truncate_or_delete_file, get_file_size
from dbma.core import messages
from dbma.core.configs import dbm_agent_config


clear_tasks = deque(maxlen=1024)

backup_dir_re_pattern = re.compile(
    r"(?P<port>[0-9]{4,4})-backup-(?P<dt>\d{4}-\d{1,2}-\d{1,2}T\d{1,2}-\d{1,2}-\d{1,2}-\d{4,6})"
)


@dataclass
class ClearTask(object):
    """
    清理任务对象
    """

    path: Path

    @property
    def rename_at(self):
        """根据目录名，计算出目录备份的时间点"""
        # 目录的后缀是 “2023-05-29T20-23-32-472128” 这个格式，也就是说它不是一个正确的时间日期格式
        # 如果我们要得到 datetime 对象，还要给它整一下才行
        match = backup_dir_re_pattern.search(str(self.path))
        dt_str = match.group("dt")
        date_str, tm_str = dt_str.split("T")
        hour, minte, seconde, ms = tm_str.split("-")
        datetime_str = "{} {}:{}:{}.{}".format(date_str, hour, minte, seconde, ms)
        return datetime.fromisoformat(datetime_str)

    def is_expired(self, now=None):
        """
        检查 rename 文件是否已经过期了
        """
        match = backup_dir_re_pattern.search(str(self.path))
        # 用传好格式构造 datetime 对象
        if match:
            now = datetime.now() if now is None else now
            delta = now - self.rename_at
            if delta.days >= 3:
                return True
        # 没有匹配到正则、或是没有超过 3 天
        return False


def scan_data_dir_gen_task():
    """只扫描 binlog 目录和 data 目录；至于 backup 目录这个是交由备份子系统完成

    Returns:
    --------
    [ClearTask,ClearTask ...]
    """
    logging.info(messages.FUN_STARTS.format(fname()))

    result = []
    target_dirs = [
        dbm_agent_config.mysql_datadir_parent,
        dbm_agent_config.mysql_binlogdir_parent,
    ]
    for path in target_dirs:
        # 处理一下路径的格式，让它可以满足 glob.glob 的要求
        if path.endswith("/"):
            target = path + "*"
        else:
            target = path + "/*"

        logging.info("scan dir '{}' .".format(target))

        # 逐个比较找到 ${port}-backup-xxx 格式的备份目录
        for instance_path in glob.glob(target):
            if backup_dir_re_pattern.search(instance_path):
                logging.info("find '{}' .".format(instance_path))
                # 构造 ClearTask 对象
                result.append(ClearTask(instance_path))

    logging.info(messages.FUN_ENDS.format(fname()))
    return result


def clear_instance(task: ClearTask = None):
    """
    根据 ClearTask 中指定的目录进行清理动作
    """
    logging.info(messages.FUN_STARTS.format(fname()))
    logging.info(
        "task.path = '{}'  is_expire = '{}' ".format(task.path, task.is_expired)
    )
    files = []
    dirs = []

    for item in glob.glob(task.path, recursive=True):
        path = Path(item)
        if path.is_dir():
            dirs.append(dirs)
        else:
            files.append(path)

    # 先清理文件
    for path in files:
        # 准备清理
        while True:
            # 如果文件比较大，那么就一直 truncate 到 0 为止
            logging.info(
                "prepare clear '{}' size = {}".format(path), get_file_size(path)
            )
            chunck = truncate_or_delete_file(path, 16 * 1024 * 1024)
            logging.info("done clear '{}' size = {}".format(path), get_file_size(path))
            if chunck == 0:
                break
        # 清理完成
        time.sleep(1)

    # 清理目录
    # TODO

    logging.info(messages.FUN_ENDS.format(fname()))
