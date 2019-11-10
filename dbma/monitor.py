import os
import time
import distro
import psutil
import logging
import requests
import threading
from mysql import connector
from datetime import datetime
from collections import namedtuple
from . import dbmacnf
from . import version

"""
各项性能指标的采集
"""

NetInterface = namedtuple('NetInterface', ['name', 'speed', 'isup', 'address'])


class ItemSenderMixin(object):
    """
    实现将采集到的信息发送 dbmc
    """

    def _create_session(self) -> "Session":
        """
        创建一个 http(s) 会话
        """
        logger = self.logger.getChild("_create_session")

        try:
            session = requests.Session()
            session.headers.update({'Referer': self.cnf.dbmc_site})
            api_url = os.path.join(self.cnf.dbmc_site, self.cnf.api_host)
            session.get(api_url + '?pk=-1')

            self.session = session

        except Exception as err:
            logger.warning(f"connect to {self.cnf.dbmc_site} fail")
            self.session = None

    def _send_host(self):
        """
        发送主机信息到 dbm-center
        """
        logger = self.logger.getChild('_send_host')
        if self.session is None:
            logger.debug(
                f"session object is None, can not send monitor item to {self.dbmc_site}")
            return

        # 准备数据
        csrfmiddlewaretoken = self.session.cookies['csrftoken']
        host_uuid = self.cnf.host_uuid

        # 准备数据 2
        # 从主机所有的 IP 地址中过滤出管理网 IP
        for interface in self.net_interfaces:

            # 过滤
            if interface.name == self.cnf.net_if:
                manger_net_ip = interface.address
                break
        else:
            logger.error(
                "manger_net_ip can not find in host's ip list;skip sender")

            # 指定的管理网卡不存在，不再发送数据到 dbmc
            return

        # 准备数据 3
        cpu_cores = self.cpu_cores
        mem_total_size = self.mem_total
        os_version = self.os_version

        # 组装数据
        data = {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'host_uuid': host_uuid,
            'cpu_cores': cpu_cores,
            'mem_total_size': mem_total_size,
            'os_version': os_version,
            'agent_version': version.agent_version,
            'manger_net_ip': manger_net_ip,
        }

        api_url = os.path.join(self.cnf.dbmc_site, self.cnf.api_host)
        logger.info(f"send host item '{data}' to {api_url}")

        response = self.session.post(api_url, data=data)
        logger.info(response.json())

    def _send_cpu_times(self):
        """
        发送 cpu 时间片信息到 dbmc
        """
        logger = self.logger.getChild('_send_cpu_times')
        if self.session is None:

            # 如果 session 是 None 就跳过向 dbm-center 发送信息的流程
            logger.error("session object is None ,skip send cpu_time to dbmc")
            return

        # 准备数据
        csrfmiddlewaretoken = self.session.cookies['csrftoken']
        data = {
            'user': self.cpu_time_user,
            'system': self.cpu_time_system,
            'idle': self.cpu_time_idle,
            'nice': self.cpu_time_nice,
            'iowait': self.cpu_time_iowait,
            'irq': self.cpu_time_irq,
            'softirq': self.cpu_time_softirq,
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'host_uuid': self.cnf.host_uuid,
        }
        logger.info(f'prepare send cpu times to dbmc {data}')

        # 发送数据
        response = self.session.post(self.cnf.api_cpu_times, data=data)

        logger.info(response.json())

    def _send_cpu_frequence(self):
        """
        上传 cpu 主频信息
        """
        logger = self.logger.getChild('_send_cpu_frequence')

        if self.session is None:

            # 如果 sesssion 是 None 就跳过数据上报逻辑
            logger.error("session is None ,skip send cpu frequence ")
            return

        # 准备数据
        csrfmiddlewaretoken = self.session.cookies['csrftoken']
        data = {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'current': self.cpu_frequence,
        }
        logger.info(f"prepare send cpu frequence {data}")

        # 发送数据
        response = self.session.post(
            self.cnf.api_cpu_frequences, data=data)
        logger.info(response.json())

    def _send_mem_distribution(self):
        """
        上传内存使用情况到 dbmc
        """
        logger = self.logger.getChild('_send_mem_distribution')

        if self.session is None:

            # 如果 session 是 None 那么直接退出
            logger.error("session is None,skip send mem info")
            return

        # 准备数据
        csrfmiddlewaretoken = self.session.cookies['csrftoken']
        data = {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'total': self.mem_total,
            'used': self.mem_used,
            'available': self.mem_available,
            'free': self.mem_free,
            'host_uuid': self.cnf.host_uuid,
        }
        logger.info(f"prepare send mem info {data}")

        # 发送数据
        response = self.session.post(
            self.cnf.api_memory_distributions, data=data)
        logger.info(response.json())

    def _send_disk_usage(self):
        """
        上传各个关键目录的磁盘使用情况
        """

        logger = self.logger.getChild('_send_disk_usage')

        if self.session is None:

            # 如果 session 是 None 那么直接退出
            logger.error("session is None,skip send disk usage info")
            return

        mounts = ['root', 'binlog', 'backup', 'database', 'user_local']

        for mount in mounts:

            # 循环各个要收集的挂载点
            if hasattr(self, f'disk_{mount}'):

                # 执行到这里说明有对应的目录
                # 准备数据
                du = getattr(self, f'disk_{mount}')
                csrfmiddlewaretoken = self.session.cookies['csrftoken']
                data = {
                    'csrfmiddlewaretoken': csrfmiddlewaretoken,
                    'host_uuid': self.cnf.host_uuid,
                    'mount_point': self.paths[mount],
                    'total': du.total,
                    'used': du.used,
                    'free': du.free,
                }
                logger.info(
                    f"prepare send disk usage info '{self.paths[mount]}' {data}")

                # 在送数据
                response = self.session.post(
                    self.cnf.api_disk_usages, data=data)
                logger.info(response.json())

    def _send_global_disk_io_counter(self):
        """
        上传主机层面的磁盘读写计数器到 dbmc
        """
        logger = self.logger.getChild('_send_global_disk_io_counter')

        if self.session is None:

            # Session 是 None 就跳过发送环节
            logger.info("session is None,skip send disk io counter info")
            return

        # 准备数据
        csrfmiddlewaretoken = self.session.cookies['csrftoken']
        data = {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'host_uuid': self.cnf.host_uuid,
            'read_count': self.global_disk_read_count,
            'write_count': self.global_disk_write_count,
            'read_bytes': self.global_disk_read_bytes,
            'write_bytes': self.global_disk_write_bytes,
        }
        logger.info(f'prepare send global disk io counter {data}')

        # 发送数据
        response = self.session.post(self.cnf.api_disk_io_counters, data=data)
        logger.info(response.json())

    def _send_net_interfaces(self):
        """
        """
        logger = self.logger.getChild('_send_net_interface')

        if self.session is None:

            # Session 是 None 就跳过发送环节
            logger.info("session is None,skip send net interface info")
            return

        # 数据准备
        data = None
        for interface in self.net_interfaces:

            csrfmiddlewaretoken = self.session.cookies['csrftoken']
            data = {
                'name': interface.name,
                'isup': interface.isup,
                'speed': interface.speed,
                'address': interface.address,
                'csrfmiddlewaretoken': csrfmiddlewaretoken,
                'host_uuid': self.cnf.host_uuid,
            }
            logger.info(f"prepare send net interface info {data}")

            # 发送数据
            response = self.session.post(
                self.cnf.api_net_interfaces, data=data)
            logger.info(response.json())

    def _send_global_net_io_counter(self):
        """
        上传全局网络 IO 计数据器
        """
        logger = self.logger.getChild('_send_global_net_io_counter')

        if self.session is None:

            # Session 是 none 就跳过发送环节
            logger.error("session is None,skip send global net io counter")
            return

        # 数据准备
        csrfmiddlewaretoken = self.session.cookies['csrftoken']
        data = {
            'bytes_sent': self.global_net_bytes_sent,
            'bytes_recv': self.global_net_bytes_recv,
            'host_uuid': self.cnf.host_uuid,
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
        }
        logger.info(f"prepare send global net counter {data}")
        # 发送数据
        response = self.session.post(self.cnf.api_net_io_counters, data=data)
        logger.info(response.json())

    def send_host_monitor_item(self):
        """
        封闭所有主机监控的发送逻辑
        """
        logger = self.logger.getChild('send_host_monitor_item')
        logger.info('send host monitor item...')

        self._create_session()
        if self.session is None:

            # session 是 None 说明连接不上，直接跳过上报逻辑
            logger.error(f"create session faile {self.cnf.dbmc_site}")
            return

        # 依次发送主机层面的监控信息
        # 1、主机的基本硬件配置与操作系统信息
        # 2、cpu 时间片分布情况
        # 3、cpu 运行频率信息
        # 4、内存使用情况
        # 5、磁盘使用情况
        # 6、全局磁盘读写计数器
        # 7、网卡信息
        # 8、全局网络计数器
        self._send_host()
        self._send_cpu_times()
        self._send_cpu_frequence()
        self._send_mem_distribution()
        self._send_disk_usage()
        self._send_global_disk_io_counter()
        self._send_net_interfaces()
        self._send_global_net_io_counter()

    def send_mysql_monitor_item(self):
        """
        """
        logger = self.logger.getChild('send_mysql_monitor_item')


class HostMonitor(threading.Thread, ItemSenderMixin):
    """
    实现主机级别的监控
    """
    logger = logging.getLogger(
        'dbm-agent').getChild(__name__).getChild('HostMonitor')

    def __init__(self, name: str = "host-monitor", daemon=True, interval=60):
        """

        """
        logger = self.logger.getChild('__init__')

        # 配置线程的名字和属性
        threading.Thread.__init__(self, name=name, daemon=daemon)

        # dbma 配置文件对象
        self.cnf = dbmacnf.cnf

        # 每 interval 秒运行一次
        self.interval = interval

        self.paths = {
            'user_local': '/usr/local/',
            'database': '/database/',
            'backup': '/backup/',
            'binlog': '/binlog/',
            'root': '/',
        }

        logger.info("init host monitor thread")

        # 主机层面要收集的维度信息
        self.os_version = None
        self.cpu_cores = None
        self.cpu_frequence = None

        self.cpu_time_user = None
        self.cpu_time_nice = None
        self.cpu_time_system = None
        self.cpu_time_idle = None
        self.cpu_time_iowait = None
        self.cpu_time_irq = None
        self.cpu_time_softirq = None

        self.mem_total = None
        self.mem_available = None
        self.mem_used = None
        self.mem_free = None

        self.disk_user_local = None
        self.disk_database = None
        self.disk_backup = None
        self.disk_binlog = None
        self.disk_root = None

        self.global_disk_read_count = None
        self.global_disk_write_count = None
        self.global_disk_read_bytes = None
        self.global_disk_write_bytes = None

        self.net_interfaces = None

        self.global_net_bytes_sent = None
        self.global_net_bytes_recv = None

        # 每检查一次都要更新这个时间
        self.last_gather_time = None

        # 把 _is_completed  把这个值设置为 True 、进程将在下次执行时退出
        self._is_completed = False

    def _get_os_version(self):
        """
        实现对 os 版本的信息收集
        """
        logger = self.logger.getChild('_get_os_version')
        self.os_version = '-'.join(distro.linux_distribution())
        logger.debug(f"os version = {self.os_version}")

    def _get_cpu_cores(self):
        """
        实现对 cpu 信息的收集
        """
        logger = self.logger.getChild('_get_cpu_cores')
        self.cpu_cores = psutil.cpu_count()
        logger.debug(f"cpu cores = {self.cpu_cores}")

    def _get_cpu_frequence(self):
        """
        实现对 cpu 主频的信息收集
        """
        logger = self.logger.getChild('_get_cpu_frequence')
        self.cpu_frequence = psutil.cpu_freq()
        logger.debug(f"cpu frequence = {self.cpu_frequence}")

    def _get_cpu_times(self):
        """
        实现对 cpu 时间片分布的收集工作
        """
        logger = self.logger.getChild("_get_cpu_times")

        # 收集 cpu 时间片信息并记录当前能收集到的维度
        # linux 可以收集到 10 个维度，Mac 只有四个维度
        times = psutil.cpu_times()
        total = sum(times)
        logger.debug(f"times include {len(times)} items")
        logger.debug(f"cpu times = {times}")

        # 按收集到的维度分类讨论
        if len(times) == 10:

            # linux 环境下是 10 维的数据
            user, nice, system, idle, iowait, irq, softirq, *_ = times
            self.cpu_time_user = user / total
            self.cpu_time_nice = nice / total
            self.cpu_time_system = system / total
            self.cpu_time_idle = idle / total
            self.cpu_time_iowait = iowait / total
            self.cpu_time_irq = irq / total
            self.cpu_time_softirq = softirq / total
        else:

            # mac 环境下
            user, nice, system, idle, *_ = times
            self.cpu_time_user = user / total
            self.cpu_time_nice = nice / total
            self.cpu_time_system = system / total
            self.cpu_time_idle = idle / total

    def _get_mem_distribution(self):
        """
        实现对内存使用分布(各位部分的使用情况)的检查
        """
        logger = self.logger.getChild('_get_mem_distribution')

        mem = psutil.virtual_memory()
        total, available, _, used, free, *_ = mem
        logger.debug(f"memory distribution {mem}")

        self.mem_total = total
        self.mem_available = available
        self.mem_used = used
        self.mem_free = free

    def _get_disk_usage(self):
        """
        检测磁盘的使用情况
        目前来看要检查 5 个关键目录

        1: /
        2: /usr/local/
        3: /database/
        4: /backup/
        5: /binlog/

        """
        logger = self.logger.getChild('_get_disk_usage')

        for path_name, path in self.paths.items():
            try:
                usage = psutil.disk_usage(path)
                setattr(self, f"disk_{path_name}", usage)
                logger.debug(f"disk usage {path_name}  {usage}")
            except FileNotFoundError as err:

                # 如果给定的目录不存在会报 FileNotFoundError 异常
                logger.warning(f"{err}")

    def _get_global_disk_io_counter(self):
        """
        收集主机级别、所有磁盘的一个读写计数器
        """
        # 如果监控的粒度下沉到每一块磁盘级别，那就太细了，这个比较适合用监控系统来做

        logger = self.logger.getChild('_get_global_disk_io_counter')

        dio = psutil.disk_io_counters()
        read_count, write_count, read_bytes, write_bytes, *_ = dio

        self.global_disk_read_count = read_count
        self.global_disk_write_count = write_count
        self.global_disk_read_bytes = read_bytes
        self.global_disk_write_bytes = write_bytes

        logger.debug(str(dio))

    def _get_net_interfaces(self):
        """
        获取机器上除 lo 之外的每一张网卡
        """
        logger = self.logger.getChild('_get_net_interfaces')

        AF_INET = 2

        # 过滤出 IPV4 地址、对于非 IPV4 地址返回 None
        def get_ipv4_addr(addrs):
            """
            返回 ipv4 地址
            """
            for addr in addrs:
                if addr.family == AF_INET:
                    return addr.address
            return None

        # 网卡的物理信息
        # 如：{'ens33': snicstats(isup=True, duplex=<NicDuplex.NIC_DUPLEX_FULL: 2>, speed=1000, mtu=1500)}
        infs = psutil.net_if_stats()

        # 网卡的逻辑信息(ip地址列表)
        addresses = psutil.net_if_addrs()

        interfaces = []
        for inf in infs.keys():
            if inf == 'lo':
                pass
            else:
                addr = get_ipv4_addr(addresses[inf])
                i = speed = infs[inf]
                speed = i.speed
                isup = i.isup
                interfaces.append(NetInterface(
                    name=inf, speed=speed, isup=isup, address=addr))
        self.net_interfaces = interfaces

        logger.debug(self.net_interfaces)

    def _get_global_net_io_counter(self):
        """
        获取全局网卡 io 计数器
        """
        logger = self.logger.getChild("_get_global_net_io_counter")

        nio = psutil.net_io_counters()
        bytes_sent, bytes_recv, *_ = nio

        self.global_net_bytes_sent = bytes_sent
        self.global_net_bytes_recv = bytes_recv

        logger.debug(nio)

    def gather_monitor_item(self):
        """
        采集监控项
        """
        self._get_os_version()

        self._get_cpu_cores()
        self._get_cpu_times()
        self._get_cpu_frequence()

        self._get_mem_distribution()

        self._get_disk_usage()
        self._get_global_disk_io_counter()

        self._get_net_interfaces()
        self._get_global_net_io_counter()

        self.last_gather_time = datetime.now()

    def force_exits(self):
        """
        标记 _is_completed 为 True 为后面的强制退出做准备
        """
        self._is_completed = True

    def run(self):
        """
        """

        while True:

            # 统一处理在运行时产生的异常
            try:

                # 收集监控项
                self.gather_monitor_item()

                # 发送监控信息到 dbm-center
                self.send_host_monitor_item()

                # 测试父进程是不要强制退出子进程
                if self._is_completed == True:
                    return

            except Exception as err:
                self.logger.error(err)
                # 有异常也不退出，程序会周期性的重试

            finally:
                pass

            time.sleep(self.interval)
