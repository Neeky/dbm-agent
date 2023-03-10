# -*- encoding: utf-8 -*-

"""dbm-agent 周期性任务

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""

import time
import atexit
import requests
from concurrent.futures import ThreadPoolExecutor
from dbma.core.configs import DBMAgentConfig
from dbma.core.configs import DBMCenterUrlConfig
from dbma.loggers.loggers import get_logger

logger = get_logger(__file__)

dbm_center_url_config = DBMCenterUrlConfig()
dbm_agent_config = DBMAgentConfig()
threads = ThreadPoolExecutor(max_workers=2)
keep_threads_running = True

def registor_agent_to_center():
    """注册 agent 的信息到 dbm-center
    """
    while keep_threads_running:
        try:
            response = requests.post(dbm_center_url_config.register_agent_url, json=dbm_agent_config.make_register_data())
            logger.info(response.content)
        except KeyboardInterrupt as err:
           logger.info("gracyfull stop threads") 
        except Exception as err:
            logger.error("registor_agent_to_center fail.")
            logger.exception(err)
        # TODO 把这个 60 调整到配置文件中去
        time.sleep(20)


def _stop_threads():
    """关闭后台任务
    """
    global keep_threads_running
    keep_threads_running = False

def start_cycle_tasks():
    """提交所有后台任务到线程池
    """
    threads.submit(registor_agent_to_center)
    atexit.register(_stop_threads)
