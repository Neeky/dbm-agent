# -*- coding: utf-8 -*-

"""dbm-agent 周期性任务

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""


import time
import atexit
import logging
import requests
from requests.exceptions import ConnectionError
from concurrent.futures import ThreadPoolExecutor
from dbma.core.configs import DBMAgentConfig, DBMCenterUrlConfig

keep_threads_running = True
dbm_center_url_config = DBMCenterUrlConfig()
dbm_agent_config = DBMAgentConfig()
threads = ThreadPoolExecutor(max_workers=8, thread_name_prefix="backends")


def registor_agent_to_center():
    """注册 agent 的信息到 dbm-center"""
    while keep_threads_running:
        try:
            logging.info(
                "agent ifo  = {} .".format(dbm_agent_config.make_register_data())
            )
            response = requests.post(
                dbm_center_url_config.register_agent_url,
                json=dbm_agent_config.make_register_data(),
            )
            data = response.json()
            if data["message"].startswith(
                "UNIQUE constraint failed: agents_agent.host"
            ):
                logging.info("agent has been registed. ")
        except ConnectionError as err:
            logging.info(
                "register agent info to dbm-center '{}' got ConnectionError. maybe dbm-center is done. .".format(
                    dbm_center_url_config.register_agent_url
                )
            )
        except Exception as err:
            logging.error(
                "registor_agent_to_center fail err-type {}.".format(type(err))
            )
            logging.exception(err)
        # 默认 15 分钟注册一次
        time.sleep(dbm_agent_config.backends_register_time_interval)


def _stop_threads():
    """关闭后台任务"""
    global keep_threads_running
    keep_threads_running = False


def start_cycle_tasks():
    """提交所有后台任务到线程池"""
    threads.submit(registor_agent_to_center)
    atexit.register(_stop_threads)
