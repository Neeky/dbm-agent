
import psutil
from collections import namedtuple

"""
各项性能指标的采集
"""

CpuTimes = namedtuple('CpuTimes',['user','system','idle','nice','iowait','irq','softirq'])
CpuCores = namedtuple('CpuCores',['counts'])
CpuFrequency = namedtuple('CpuFrequency',['current'])

#MemoryDistribution = namedtuple('MemoryDistribution',[''])

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
    if len(c) == 10:
        # linux platform
        # 解包
        user,nice,system,idle,iowait,irq,softirq = c
        return CpuTimes(user=user,
                        nice=nice,
                        system=system,
                        idle=idle,
                        iowait=iowait,
                        irq=irq,
                        softirq=softirq)
    else:
        # mac platform
        user,nice,system,idle = c
        return CpuTimes(user=user,
                        nice=nice,
                        system=system,
                        idle=idle,
                        iowait=0,
                        irq=0,
                        softirq=0)









