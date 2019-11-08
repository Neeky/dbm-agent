
import os
import time
import requests
import logging
from . import dbmacnf
#from . import gather
from . import version


"""
实现所有由 dbm-agent 向 dbm-center 发信息的功能
"""


cnf = dbmacnf.cnf
_logger = logging.getLogger('dbm-agent').getChild(__name__)


def push_host():
    """
    上传主机信息到 dbmc
    第一步：发起一个无意义的 get 请求用于得到 csrftoken 为之后的 post 做准备
    第二步：收集数据
    第三步：post 数据到 dbmc
    """
    logger = _logger.getChild("push_host")
    logger.debug("prepare push host info")
    try:
        # 第一步
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = os.path.join(cnf.dbmc_site, cnf.api_host)
        session.get(api_url + '?pk=-1')  # pk=-1 是一个没有意义的查询

        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info(
            f"using {api_url + '?pk=-1'} Got csrfmiddlewaretoken = {csrfmiddlewaretoken}")

        host = {'host_uuid': cnf.host_uuid,
                'agent_version': version.agent_version}

        os_version = gather.os_version()
        cup_cores = gather.cpu_cores().counts
        mem_total_size = gather.mem_distri().total
        ifs = gather.net_interfaces()
        mif = None  # 管理网、网卡
        for i in ifs:
            if i.name == cnf.net_if:
                mif = i
                break
        manger_net_ip = mif.address

        host.update({
            'cpu_cores': cup_cores,
            'mem_total_size': mem_total_size,
            'manger_net_ip': manger_net_ip,
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'os_version': os_version,
        })

        logger.info(f"gather host info = {host}")

        logger.info(f"post host info to {api_url}")
        response = session.post(api_url, data=host)
        logger.info(response.json())
        logger.info(f"push host info complete")

    except Exception as err:
        logger.error(str(err))

    finally:
        if hasattr(session, 'close'):
            session.close()


def push_cpu_times():
    """
    上传 CPU 时间片分布信息
    第一步：发起一个次 get 请求用于获取 csrftoken 的值，为 post 做准备
    第二步：收集 cpu 时间片信息
    第三步：发送信息到 dbmc
    """
    try:
        # 第一步
        logger = _logger.getChild("push_cpu_times")
        logger.info("push cpu times info to dbmc")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_cpu_times
        logger.info(f"query {api_url}?pk=-1 for get csrftoken")
        response = session.get(api_url+'?pk=-1')
        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info(f"csrftoken = {csrfmiddlewaretoken}")

        # 第二步
        times = dict(gather.cpu_times()._asdict())
        times.update({'host_uuid': cnf.host_uuid,
                      'csrfmiddlewaretoken': csrfmiddlewaretoken})
        logger.info(f"cpu times = {times}")

        # 第三步
        response = session.post(api_url, data=times)
        logger.info(response.json())
        logger.info("push cpu times info completed.")

    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_cpu_frequence():
    """
    上传当前 cpu 的运行频率
    """
    try:
        logger = _logger.getChild("push_cpu_frequence")
        logger.info("prepare push cpu frequence to dbmc")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_cpu_frequences
        session.get(api_url+'?pk=-1')

        csrfmiddlewaretoken = session.cookies['csrftoken']
        data = gather.cpu_frequence()._asdict()
        data.update({
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        })
        logger.info(data)
        response = session.post(api_url, data=data)
        logger.info(response.json())

    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_net_interfaces():
    """
    上传主机上的网卡信息
    """
    try:
        logger = _logger.getChild("push_net_interfaces")
        logger.info("prepase push net interface info")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_net_interfaces
        session.get(api_url+'?pk=-1')
        logger.info(f"using {api_url}?pk=-1 for go token")

        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info(f"csrftoken = {csrfmiddlewaretoken}")

        infs = gather.net_interfaces()
        logger.info(f"nifs = {infs}")

        for inf in infs:
            data = inf._asdict()
            data.update({'csrfmiddlewaretoken': csrfmiddlewaretoken})

            response = session.post(api_url, data=data)

            csrfmiddlewaretoken = session.cookies['csrftoken']
            logger.info(response.json())

        logger.info("net-interface push complete")

    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_net_io_counter():
    """
    上传网络接口 IO 计数器信息到服务端
    """
    try:
        logger = _logger.getChild("push_net_io_counter")
        logger.info("prepare push net io counter info")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_net_io_counters
        logger.info(f"query {api_url}?pk=-1 for get csrftoken")
        session.get(api_url + '?pk=-1')

        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info(f"csrftoken = {csrfmiddlewaretoken}")

        nic = gather.global_net_io_counter()
        data = nic._asdict()
        data.update({'csrfmiddlewaretoken': csrfmiddlewaretoken})
        logger.info(f"net io counter = {data}")

        response = session.post(api_url, data=data)
        logger.info(response.json())

    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_memory_distribution():
    """
    实现主机内存使用情况上的报
    """
    try:
        logger = _logger.getChild("push_memory_distribution")
        logger.info("prepare push memory distribution info to dbmc")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_memory_distributions
        logger.info(f"query {api_url}?pk=-1 for csrftoken")

        session.get(api_url+'?pk=-1')
        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info("csrftoken  = {csrfmiddlewaretoken}")

        data = {'csrfmiddlewaretoken': csrfmiddlewaretoken}
        md = gather.mem_distri()
        data.update(md._asdict())
        logger.info(f"data = {data}")

        response = session.post(api_url, data=data)
        logger.info(response.json())

    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_disk_usage():
    """
    实现磁盘使用率信息率的上报
    """
    try:
        logger = _logger.getChild("push_disk_usage")
        logger.info("prepare push disk uasge info to dbmc")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_disk_usages
        logger.info(f"query {api_url}?pk=-1 for csrftoken")

        session.get(api_url+'?pk=-1')
        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info(f"csrftoken  = {csrfmiddlewaretoken}")

        for du in gather.disk_usage():
            data = {'csrfmiddlewaretoken': csrfmiddlewaretoken}
            data.update(du._asdict())
            logger.info(f"data = {data}")
            session.post(api_url, data=data)
            csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info("push disk usage info complete")
    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_disk_io_counter():
    """
    实现磁盘IO计数器的上报
    """
    try:
        logger = _logger.getChild("push_disk_io_counter")
        logger.info("prepare push disk io counter to dbmc")
        session = requests.Session()
        session.headers.update({'Referer': cnf.dbmc_site})
        api_url = cnf.api_disk_io_counters
        logger.info(f"query {api_url}?pk=-1 for csrftoken")

        session.get(api_url+'?pk=-1')
        csrfmiddlewaretoken = session.cookies['csrftoken']
        logger.info(f"csrftoken  = {csrfmiddlewaretoken}")

        dio = gather.global_disk_io_counter()
        data = {'csrfmiddlewaretoken': csrfmiddlewaretoken}
        data.update(dio._asdict())
        logger.info(f"data = {data}")

        response = session.post(api_url, data=data)
        logger.info(response.json())
        logger.info("push disk usage info complete")

    except Exception as err:
        logger.error(str(err))
    finally:
        if hasattr(session, 'close'):
            session.close()


def push_system_monitor_item():
    """
    """
    logger = _logger.getChild('push_system_monitor_item')
    while True:
        try:
            push_host()
            push_cpu_times()
            push_cpu_frequence()
            push_net_interfaces()
            push_net_io_counter()
            push_memory_distribution()
            push_disk_usage()
            push_disk_io_counter()
        except Exception as err:
            logger.error(str(err))
        time.sleep(59)


class Pusher(object):
    """
    所有信息由 dbm-agent 上传到 dbm-center 的基类
    """
    logger = logging.getLogger(
        'dbm-agent').getChild(__name__).getChild('Pusher')

    def __init__(self):
        """
        """
        logger = self.logger.getChild('__init__')


class SystemMonitorPusher(Pusher):
    """
    上传操作系统级别的监控项到 dbm-center
    """
    pass
