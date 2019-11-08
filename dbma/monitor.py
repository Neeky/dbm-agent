import time
import distro
import psutil
import logging
import threading
from datetime import datetime
from collections import namedtuple
from mysql import connector
from . import dbmacnf

"""
各项性能指标的采集
"""

logger = logging.getLogger('dbm-agent').getChild(__name__)

# 为什么要在 psutil 已经存在的数据结构之前再加上一层数据结构
# 1、要保证不管 psutil 的数据结构怎么变化 dbm-agent 输出的数据结构不变
# 2、一定程序上兼容 mac

CpuTimes = namedtuple(
    'CpuTimes', ['user', 'system', 'idle', 'nice', 'iowait', 'irq', 'softirq'])
CpuCores = namedtuple('CpuCores', ['counts'])
CpuFrequency = namedtuple('CpuFrequency', ['current'])

MemDistri = namedtuple('MemDistri', ['total', 'available', 'used', 'free'])

DiskUsage = namedtuple('DiskUsage', ['mountpoint', 'total', 'used', 'free'])
GlobalDiskIOCounter = namedtuple('GlobalDiskIOCounter', [
                                 'read_count', 'write_count', 'read_bytes', 'write_bytes'])

# ipv4
AF_INET = 2
NetInterface = namedtuple('NetInterface', ['name', 'speed', 'isup', 'address'])
GlobalNetIOCounter = namedtuple(
    'GlobalNetIOCounter', ['bytes_sent', 'bytes_recv'])

# mysql
DMLStat = namedtuple(
    'DMLStat', ['comselect', 'comupdate', 'cominsert', 'comdelete', 'slowquery'])


def os_version():
    return '-'.join(distro.linux_distribution())


def cpu_cores() -> CpuCores:
    """
    采集当前操作系统上 cpu 的逻辑核心数量
    """
    cores = psutil.cpu_count()
    return CpuCores(counts=cores)


def cpu_times() -> CpuTimes:
    """
    采集 CPU 时间片分布
    """
    c = psutil.cpu_times()
    total = sum(c)
    if len(c) == 10:
        # linux platform
        # 解包
        user, nice, system, idle, iowait, irq, softirq, *_ = c
        return CpuTimes(user=user/total,
                        nice=nice/total,
                        system=system/total,
                        idle=idle/total,
                        iowait=iowait/total,
                        irq=irq/total,
                        softirq=softirq/total)
    else:
        # mac platform
        user, nice, system, idle, *_ = c
        return CpuTimes(user=user/total,
                        nice=nice/total,
                        system=system/total,
                        idle=idle/total,
                        iowait=0/total,
                        irq=0/total,
                        softirq=0/total)


def cpu_frequence() -> CpuFrequency:
    """
    cpu 当前的运行频率
    """
    f = psutil.cpu_freq()
    return CpuFrequency(current=f.current)


def mem_distri() -> MemDistri:
    """
    内存使用分布情况
    """
    m = psutil.virtual_memory()
    total, available, _, used, free, *_ = m
    return MemDistri(total=total,
                     available=available,
                     used=used,
                     free=free)


def disk_usage():
    """
    返回
        /
        /backup
        /database
    这三个挂载点对应的磁盘使用情况
    """
    du = []
    for mp in ['/', '/database', '/backup']:
        total, used, free, _ = psutil.disk_usage(mp)
        du.append(DiskUsage(mountpoint=mp, total=total, used=used, free=free))
    return du


def global_disk_io_counter():
    """
    全局 磁盘 IO 计数器
    """
    dio = psutil.disk_io_counters()
    read_count, write_count, read_bytes, write_bytes, *_ = dio

    return GlobalDiskIOCounter(read_count=read_count,
                               write_count=write_count,
                               read_bytes=read_bytes,
                               write_bytes=write_bytes)


def net_interfaces():
    """
    返回网卡信息的列表：
    [NetInterface(name='eth0', speed=10000, isup=True,
                  address='172.17.0.2'),... ]
    """
    infs = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()

    def get_ipv4_addr(addrs):
        """
        返回 ipv4 地址
        """
        for addr in addrs:
            if addr.family == AF_INET:
                return addr.address
        return None
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
    return interfaces


def global_net_io_counter():
    """
    全局 网络 IO 计数器
    """
    n = psutil.net_io_counters()
    bytes_sent, bytes_recv, *_ = n
    return GlobalNetIOCounter(bytes_sent=bytes_sent, bytes_recv=bytes_recv)

# mysql 相关的监控
# 不想把 dbm 做成一套监控系统，推荐使用 zabbix 来做监控
# dbm 实现少数几个监控项还是有必要的


def dml_stat(host: str = "127.0.0.1",
             port: int = 3306,
             user: str = "dbma",
             password: str = "dbma@0352") -> DMLStat:
    """
    一个轻量级的监控实现，只采集
    select
    update
    insert
    delete
    slow_query
    这几个计数器
    """
    cnx = None
    try:
        cnx = connecotr.connect(host=host, port=port,
                                user=user, password=password)
        cursor = cnx.cursor()
        cursor.execute("show global status ;")
        all_status = cursor.fetchall()

        status_dict = dict(all_status)
        comselect = status_dict['Com_select']
        cominsert = status_dict['Com_insert']
        comdelete = status_dict['Com_delete']
        comupdate = status_dict['Com_update']
        slowquery = status_dict['Slow_queries']

        dmlstat = DMLStat(comselect=comselect, comupdate=comupdate, cominsert=cominsert,
                          comdelete=comdelete, slowquery=slowquery)
        return dmlstat

    except Exception as err:
        logger.error(str(err))
        return None
    finally:
        if hasattr(cnx, 'close'):
            cnx.close()


class ItemSenderMixin(object):
    """
    实现将采集到的信息发送 dbmc
    """

    def send_host_monitor_item(self):
        """
        """
        logger = self.logger.getChild('send_host_monitor_item')
        logger.info('send host monitor item...')

    def send_mysql_monitor_item(self):
        """
        """
        logger = self.logger.getChild('send_mysql_monitor_item')


class HostMonitor(threading.Thread, ItemSenderMixin):
    """
    实现主机级别的监控
    """
    logger = logging.getLogger('dbm-agent').getChild(__name__)

    def __init__(self, name: str = "host-monitor", daemon=True, interval=60):
        """

        """
        logger = self.logger.getChild('__init__')

        # 配置线程的名字和属性
        threading.Thread.__init__(self, name=name, daemon=daemon)

        # dbma 配置文件对象
        self.dbmacnf = dbmacnf.cnf

        # 每 interval 秒运行一次
        self.interval = interval

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

        paths = {
            'user_local': '/usr/local/',
            'database': '/database/',
            'backup': '/backup/',
            'binlog': '/binlog/',
            'root': '/',
        }

        for path_name, path in paths.items():
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
