# -*- encoding: utf-8 -*-

"""dbm-agent 收到操作请求(task)之后，如果请求中没有带 task_id ，说明要求同步执行；如果有带 task_id 那么我们要把 task 放到后台线程中执行。

"""

import logging
from pathlib import Path
from typing import Callable
from dbma.bil.sudos import sudo
from dbma.components.mysql.install import install_mysql


def update_task_state_callback(task_id: int = None, state: str = None, message: str = None):
    """调用 dbm-center 的接口更新回调任务的状态
    """
    logging.info("starts update task state callback .")
    # TODO 调用更新接口ends
    logging.info("task_id = {}".format(task_id))
    logging.info("ends update task state callback .")


def install_mysql_task_handler(port: int = 3306, ibps: str = "128M", pkg: Path = None, task_id: int = None):
    """让安装 MySQL 的逻辑放后台执行

    Parameters:
    -----------

    port: int
        MySQL 端口号

    ibps: str
        innodb_buffer_pool_size 的大小， et 128M, 2G, 8G ...

    pkg: str
        MySQL 安装包全路径

    Return:
    -------
    None
    """
    logging.info("starts install mysql task handler .")
    try:
        # 提升后台线程的权限到 root
        with sudo("install mysql task handler"):
            install_mysql(port=port, innodb_buffer_pool_size=ibps, pkg=pkg)
        logging.info("install mysql complete")

        # 是否更新任务信息到 dbm-center
        if not task_id is None:
            logging.warn(
                "install mysql task handler's callback function is None, skip callback")
        else:
            update_task_state_callback(task_id, 200, "install mysql complete")

    except Exception as err:
        logging.error("install mysql task handler got error ")
    logging.info("ends install mysql task handler .")
