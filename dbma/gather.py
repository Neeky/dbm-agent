
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








