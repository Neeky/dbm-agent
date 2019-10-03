import distro
import psutil
import logging
from collections import namedtuple
from mysql import connector

"""
各项性能指标的采集
"""

logger = logging.getLogger('dbm-agent').getChild(__name__)

# 为什么要在 psutil 已经存在的数据结构之前再加上一层数据结构
# 1、要保证不管 psutil 的数据结构怎么变化 dbm-agent 输出的数据结构不变
# 2、一定程序上兼容 mac

CpuTimes = namedtuple('CpuTimes',['user','system','idle','nice','iowait','irq','softirq'])
CpuCores = namedtuple('CpuCores',['counts'])
CpuFrequency = namedtuple('CpuFrequency',['current'])

MemDistri= namedtuple('MemDistri',['total','available','used','free'])

DiskUsage = namedtuple('DiskUsage',['mountpoint','total','used','free'])
GlobalDiskIOCounter = namedtuple('GlobalDiskIOCounter',['read_count','write_count','read_bytes','write_bytes'])

# ipv4
AF_INET = 2
NetInterface = namedtuple('NetInterface',['name','speed','isup','address'])
GlobalNetIOCounter = namedtuple('GlobalNetIOCounter',['bytes_sent','bytes_recv'])

# mysql
DMLStat = namedtuple('DMLStat',['comselect','comupdate','cominsert','comdelete','slowquery'])

def os_version():
    return '-'.join( distro.linux_distribution() )

def cpu_cores()->CpuCores:
    """
    采集当前操作系统上 cpu 的逻辑核心数量
    """
    cores = psutil.cpu_count()
    return CpuCores(counts = cores)

def cpu_times()->CpuTimes:
    """
    采集 CPU 时间片分布
    """
    c = psutil.cpu_times()
    total = sum(c)
    if len(c) == 10:
        # linux platform
        # 解包
        user,nice,system,idle,iowait,irq,softirq,*_= c
        return CpuTimes(user=user/total,
                        nice=nice/total,
                        system=system/total,
                        idle=idle/total,
                        iowait=iowait/total,
                        irq=irq/total,
                        softirq=softirq/total)
    else:
        # mac platform
        user,nice,system,idle,*_ = c
        return CpuTimes(user=user/total,
                        nice=nice/total,
                        system=system/total,
                        idle=idle/total,
                        iowait=0/total,
                        irq=0/total,
                        softirq=0/total)

def cpu_frequence()->CpuFrequency:
    """
    cpu 当前的运行频率
    """
    f = psutil.cpu_freq()
    return CpuFrequency(current=f.current)


def mem_distri()->MemDistri:
    """
    内存使用分布情况
    """
    m = psutil.virtual_memory()
    total,available,_,used,free,*_ = m
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
    for mp in ['/','/database','/backup']:
        total,used,free,_ = psutil.disk_usage(mp)
        du.append(DiskUsage(mountpoint=mp,total=total,used=used,free=free))
    return du

def global_disk_io_counter():
    """
    全局 磁盘 IO 计数器
    """
    dio = psutil.disk_io_counters()
    read_count,write_count,read_bytes,write_bytes,*_ = dio

    return GlobalDiskIOCounter(read_count=read_count,
                            write_count=write_count,
                            read_bytes=read_bytes,
                            write_bytes=write_bytes)
    

def net_interfaces():
    """
    返回网卡信息的列表：
    [NetInterface(name='eth0', speed=10000, isup=True, address='172.17.0.2'),... ]
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
            i = speed=infs[inf]
            speed = i.speed
            isup = i.isup
            interfaces.append(NetInterface(name=inf,speed=speed,isup=isup,address=addr))
    return interfaces


def global_net_io_counter():
    """
    全局 网络 IO 计数器
    """
    n = psutil.net_io_counters()
    bytes_sent,bytes_recv,*_ = n
    return GlobalNetIOCounter(bytes_sent=bytes_sent,bytes_recv=bytes_recv)

# mysql 相关的监控
# 不想把 dbm 做成一套监控系统，推荐使用 zabbix 来做监控
# dbm 实现少数几个监控项还是有必要的

def dml_stat(host:str="127.0.0.1",
            port:int=3306,
            user:str="dbma",
            password:str="dbma@0352")->DMLStat:
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
        cnx = connecotr.connect(host=host,port=port,user=user,password=password)
        cursor = cnx.cursor()
        cursor.execute("show global status ;")
        all_status = cursor.fetchall()

        status_dict = dict(all_status)
        comselect = status_dict['Com_select']
        cominsert = status_dict['Com_insert']
        comdelete = status_dict['Com_delete']
        comupdate = status_dict['Com_update']
        slowquery = status_dict['Slow_queries']

        dmlstat = DMLStat(comselect=comselect,comupdate=comupdate,cominsert=cominsert,
                        comdelete=comdelete,slowquery=slowquery)
        return dmlstat

    except Exception as err:
        logger.error(str(err))
        return None
    finally:
        if hasattr(cnx,'close'):
            cnx.close()








