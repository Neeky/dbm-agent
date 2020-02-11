"""
实现对主机层面与数据库层面的监控
"""

# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import re
import os
import time
import distro
import psutil
import socket
import logging
import requests
import threading
import subprocess

from mysql import connector
from datetime import datetime
from collections import namedtuple
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler


from . import dbmacnf
from . import version
from . import common

"""
各项性能指标的采集
"""

NetInterface = namedtuple('NetInterface', ['name', 'speed', 'isup', 'address'])

logger = logging.getLogger('dbm-agent').getChild(__name__)


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


class MySQLConnectionKeeperMixin(object):
    """
    用长连接的方式连接进 MySQL、并维护好这个连接
    """

    def get_cnx(self):
        """
        如果连接可用就返回 self.cnx
        如果连接不可用就返回 None
        """
        logger = self.logger.getChild("get_cnx")

        # 如果 self.cnx is None 说明连接还没有建立那么要建一个
        if self.cnx is None:
            try:
                logger.debug(
                    f"prepare create monitor session to mysqld-{self.port} user='{self.monitor_user}' password='{self.monitor_password}' ")
                self.cnx = connector.connect(
                    host=self.host, port=self.port, user=self.monitor_user, password=self.monitor_password)
            except Exception as err:
                logger.warning(
                    f"create monitor session fail inner error '{err}' ")
                self.cnx = None

        # 执行到这里 self.cnx 要么是 None 要么是一个已经连接好的会话
        if self.cnx is None:
            return None

        # 执行到这里有可能是连接之前是正常的，但是 MySQL 宕机了，使得 self.cnx 不为 None ，但是 self.cnx 不一定可用
        try:

            # 如果一切正常就返回 self.cnf
            self.cnx.ping()
            return self.cnx

        except Exception as err:

            # 一旦遇到异常就把连接回收、并返回 None
            try:
                if hasattr(self.cnx, 'close'):
                    self.cnx.close()
            except Exception:
                pass
            finally:
                self.cnx = None

            logger.warning(
                "monitor session loss,may been killed or mysqld is down")
            self.cnx = None
            return None

        # 永远都不应该执行到这里
        logger.warning("unknown excecption ,dead code been executed !!!")
        return None

    def __del__(self):
        """
        连接回收
        """
        if hasattr(self.cnx, 'close'):
            self.cnx.close()

        if hasattr(self, 'kill'):
            self.kill()


class MySQLVariablesMonitorMixin(object):
    """
    完成对 global variables 的查询功能
    """
    variables_last_update_time = None

    logger = logger.getChild("MySQLVariablesMonitorMixin")

    def _query_variables(self):
        """
        查询数据库中的 variable 
        """
        logger = self.logger.getChild("_query_variables")
        logger.debug("prepare start query variables")

        # 拿到连接
        cnx = self.get_cnx()
        if cnx is None:

            # 如果连接对象拿不到，就直接把 variables 设置为空字典
            # 并返回
            logger.warning("cnx is None")
            self.variables = {}
            self.variables_last_update_time = datetime.now()
            logger.info("set self.variables to None")
            return

        # 执行到这里说明 cnx 对象不是 None
        try:

            # 就算不是 None 也还是有可能会引发异常
            cursor = cnx.cursor()
            cursor.execute("show global variables;")
            data = cursor.fetchall()
            self.variables = {k.lower(): v for k, v in data}
            self.variables_last_update_time = datetime.now()
            logger.info("query variables complete")
        except Exception as err:
            self.variables = {}
            self.variables_last_update_time = datetime.now()
            # 有可能引发异常、比如说权限不足
            logger.warning(f"got exception {err}")

    def __contains__(self, name):
        """
        为了支持 in 操作
        """
        # 如果不是空，那么 variables 里面有就返回 True ，没有就返回 False
        return name.lower() in self.variables

    def __getitem__(self, name):
        """
        定义索引操作
        """

        if self.variables_last_update_time == None:

            # variables_last_update_time 还是 None 说明还没有到数据库中查询过 variables
            # 那么先要查询一下
            self._query_variables()

        # 计算出上一次查询 variables 到现在已经过去了多少秒
        now = datetime.now()
        seconds_passed = (now - self.variables_last_update_time).second
        if seconds_passed >= self.expire_seconds:

            # 说明 variables 已经过期了又要重新收集一下
            self._query_variables()

        # 执行到这里要么 variables 是最新的状态值，要么就是空值
        # 这两个值都是可用的

        # 如果有这个项就返回、没有这返回 None
        _lower_name = name.lower()
        if _lower_name in self:
            return self.variables[_lower_name]

        return None


class MySQLStatusMonitorMixin(object):
    """
    成对 global status 的查询功能
    """
    status_last_update_time = None
    logger = logger.getChild("MySQLStatusMonitorMixin")

    def _query_status(self):
        """
        查询 global status 的值
        """
        logger = self.logger.getChild("_query_status")
        logger.debug("prepare start query status")
        # 获取连接对象
        cnx = self.get_cnx()
        if cnx is None:

            # 如果连接对象拿不到
            logger.warning("cnx is None")
            self.status = {}
            self.status_last_update_time = datetime.now()
            logger.warning("set self.staus to None")
            return

        # 执行到这里说明连接对象拿到了
        try:
            cursor = cnx.cursor()
            cursor.execute("show global status;")
            data = cursor.fetchall()

            # 所有的 status 变量小写
            # key 相关的内容不要发出去
            self.status = {k.lower(): v for k, v in data if k not in(
                'Caching_sha2_password_rsa_public_key', 'Rsa_public_key')}
            self.status_last_update_time = datetime.now()

            logger.info("query status complete")
        except Exception as err:
            #
            self.status = {}
            self.status_last_update_time = datetime.now()
            logger.warning(f"got exception {err}")

    def __contains__(self, name):
        """
        支持 in 操作
        """

        # 自动小写化
        return name.lower() in self.status

    def __getitem__(self, name):
        """
        支持索引操作
        """
        _lower_name = name.lower()

        if self.status_last_update_time is None:

            # 这个值还是 None 说明还没有查询过 status
            self._query_status()

        now = datetime.now()
        seconds_passed = (now - self.status_last_update_time).second
        if seconds_passed >= self.expire_seconds:

            # status 已经过期了
            self._query_status()

        # 执行到这里说明 self.status 要么是 None 要么真实可用

        if _lower_name in self:
            return self.status[_lower_name]

        return None


class MySQLSlaveMonitorMixin(object):
    """
    实现对 slave 的监控 (show slave status)
    """

    slave_last_update_time = None
    logger = logger.getChild("MySQLSlaveMonitorMixin")

    def _query_slave(self):
        """
        执行 show slave status 
        """
        logger = self.logger.getChild("_query_slave")
        logger.debug("prepare start query slave")
        # 获取连接
        cnx = self.get_cnx()
        if cnx is None:

            # 没有取到连接
            self.slaves = {}
            self.slaves_last_update_time = datetime.now()
            return

        # 执行到这里说明有取得连接，但是还是有可能会报错的，比如 MySQL 突然就宕机了，所以还是要 try except
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("show slave status;")

            data = cursor.fetchone()
            if data is None:
                # 有可能没有复制关系，这个时候 data 就是 None
                self.slaves = {}
                self.slaves_last_update_time = datetime.now()
                return

            # 可以会有多个复制通路(channel) 目前只支持一个的情况
            #data,*_ = data
            self.slaves = {k.lower(): v for k, v in data.items()}
            self.slaves_last_update_time = datetime.now()
            logger.info("query slave complete")
        except Exception as err:
            self.slaves = {}
            self.slaves_last_update_time = datetime.now()
            logger.warning(f"got exception {err}")

    def __contains__(self, name):
        return name.lower() in self.slaves

    def __getitem__(self, name):
        """
        """
        _lower_name = name.lower()

        if self.slave_last_update_time is None:
            # 如果还没有更新过就更新
            self._query_slave()

        now = datetime.now()
        seconds_passed = (now - self.variables_last_update_time).second
        if seconds_passed >= self.expire_seconds:
            # 如果过期了也更新
            self._query_slave()

        # 到这里 self.slaves 要么是 None 要么是已经真正可用

        if _lower_name in self:
            return self.slaves[_lower_name]

        return None


class MySQLMasterMonitorMixin(object):
    """
    实现对 master 的监控 show master status
    """
    logger = logger.getChild("MySQLMasterMonitorMixin")
    master_last_update_time = None

    def _query_master(self):
        """
        查询 master 的状态信息 show master status
        """
        logger = self.logger.getChild("_query_master")
        logger.debug("prepare start query master")
        # 获取连接对象
        cnx = self.get_cnx()
        if cnx is None:
            logger.warning("cnx is None")
            self.masters = {}
            self.master_last_update_time = datetime.now()
            logger.warning("set self.masters to None")
            return

        # 执行到这里说明连接对象是有的
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("show master status;")
            data = cursor.fetchone()
            self.masters = {k.lower(): v for k, v in data.items()}
            self.master_last_update_time = datetime.now()
            logger.info("query master complete")
        except Exception as err:
            self.masters = {}
            self.master_last_update_time = datetime.now()
            logger.warning(f"got exception {err}")

    def __contains__(self, name):
        """

        """
        return name.lower() in self.masters

    def __getitem__(self, name):
        """
        """
        # 如果还没有查询过 master 的信息那么就查一下
        if self.master_last_update_time is None:
            self._query_master()

        # 如果过期了，那也要重新查询一下
        now = datetime.now()
        seconds_passed = (now - self.variables_last_update_time).second
        if seconds_passed >= self.expire_seconds:
            self._query_master()

        # 现在 self.masters 要么是可用的，要么是 None
        _lower_name = name.lower()
        if _lower_name in self:
            return self.masters[_lower_name]

        return None


class MySQLMGRMonitorMixin(object):
    """
    实现对 MGR 的监控
    """

    logger = logger.getChild("MySQLMGRMonitorMixin")
    mgrs_last_update_time = None

    def _query_mgr(self):
        """
        select * from performance_schema.replication_group_member_stats where member_id = @@server_uuid;
        select * from performance_schema.replication_group_members where member_id = @@server_uuid; 
        """

        logger = self.logger.getChild("_query_mgr")
        logger.debug("prepare start query MGR")
        cnx = self.get_cnx()
        if cnx is None:
            #
            logger.warning("cnx is None")
            self.mgrs = {}
            self.mgrs_last_update_time = datetime.now()
            logger.warning("set self.mgrs to None")
            return

        #
        try:
            cursor = cnx.cursor(dictionary=True)
            # 故意用的 select * 这样整个监控程序的字典都自适应了
            cursor.execute(
                "select * from performance_schema.replication_group_member_stats where member_id = @@server_uuid;")
            data = cursor.fetchone()
            if data is not None:
                self.mgrs = {k.lower(): v for k, v in data.items()}
                self.mgrs_last_update_time = datetime.now()
            else:
                # 如果根据 server_uuid 找不到对应的行，说明 MGR 并没有开启
                self.mgrs = {}
                self.mgrs_last_update_time = datetime.now()
                logger.warning("set self.mgr to None")
                return

            # 如果执行到这里都没有 return 说明 mgr 是开启的
            # select * 同上
            cursor.execute(
                "select * from performance_schema.replication_group_members where member_id = @@server_uuid; ")
            data = cursor.fetchone()
            if data is not None:
                self.mgrs.update({k.lower(): v for k, v in data.items()})
                self.mgrs_last_update_time = datetime.now()
            else:
                # 绝对不应该执行到这里
                logger.warning("dead code got execution !!!!")

            logger.info("query mgr completed")

        except Exception as err:
            self.mgrs = {}
            self.mgrs_last_update_time = datetime.now()
            logger.warning(f"go execption during query mgr info {err}")
            return

    def __contains__(self, name):
        """
        """
        return name.lower() in self.mgrs

    def __getitem__(self, name):
        """
        """
        # 如果还没有查询过 mgr 的信息那么就查一下
        if self.mgrs_last_update_time is None:
            self._query_mgr()

        # 如果过期了，那也要重新查询一下
        now = datetime.now()
        seconds_passed = (now - self.variables_last_update_time).second
        if seconds_passed >= self.expire_seconds:
            self._query_mgr()

        _lower_name = name.lower()
        if _lower_name in self:
            return self.mgrs[_lower_name]

        return None


# 主机层面的监控数据采集
class ExpireTimeMixin(object):
    """定义一个数据采集的超时机制
    """
    expire_seconds = 17
    logger = logger.getChild("ExpireTime")

    def expired(self, basetime=None):
        """返回是否已经超时
        """
        logger = self.logger.getChild("expired")
        if basetime is None:
            logger.info("data expired")
            logger.info("complete")
            return True
        else:
            logger.info("data expired")
            now = datetime.now()
            seconds_passed = (now - basetime).second
            if seconds_passed > self.expire_seconds:
                logger.info("complete")
                return True

        logger.info("data not expired")
        logger.info("complete")
        return False


class NetInterfacesGather(ExpireTimeMixin):
    """采集网卡的特征信息
    """
    expire_seconds = 86400
    logger = logger.getChild("NetInterfacesGather")

    def __init__(self):
        self._nifs = None
        self._last_update_time = None

    def first_ipv4(self, snicaddrs=None):
        """提取出网卡上的第一个 ipv4 地址
        """
        logger = self.logger.getChild("first_ipv4")
        logger.info("start")

        if snicaddrs is None:
            logger.warning("exception snicaddrs is None")
            return None

        for addr in snicaddrs:
            if addr.family == 2:
                logger.info("complete")
                return addr.address

    def get_nifs(self):
        """返回所有的网卡特征信息
        """
        logger = self.logger.getChild("get_nifs")
        logger.info("start")

        # 临时的空数据
        data = {}

        # 填充地址信息
        address = psutil.net_if_addrs()
        for eth_name in address:
            data[eth_name] = {'address': self.first_ipv4(
                address[eth_name]), 'name': eth_name}

        # 填充是否在线，带宽信息
        net_ifs = psutil.net_if_stats()
        for eth_name in net_ifs:
            data[eth_name].update(
                {'isup': net_ifs[eth_name].isup, 'speed': net_ifs[eth_name].speed})

        logger.info(f"net interfaces = {data}")
        logger.info("complete")
        self._nifs = data
        return data

    def __contains__(self, name):
        """
        """
        if self._nifs is None:
            self._nifs = self.get_nifs()
        return name in self._nifs

    def __getitem__(self, name):
        if name in self:
            return self._nifs[name]

        return None

    def __iter__(self):
        if self._nifs is None:
            self._nifs = self.get_nifs()

        for nif in self._nifs:
            yield self._nifs[nif]


class HostMonitorGather(ExpireTimeMixin):
    """
    """
    _host_last_update_time = None
    _host_data = None
    logger = logger.getChild("HostMonitorGather")

    def _query_host(self):
        """查询主机监控数据
        """
        logger = self.logger.getChild("_query_host")
        logger.info("start")
        try:
            data = {}
            data['host_uuid'] = dbmacnf.cnf.host_uuid
            data['agent_version'] = version.agent_version
            data['cpu_cores'] = psutil.cpu_count()
            data['mem_total_size'] = psutil.virtual_memory().total
            data['os_version'] = ' '.join(distro.linux_distribution()).strip()
            self._host_data = data
            self._host_last_update_time = datetime.now()
            logger.info("complete")
            return data
        except Exception as err:
            logger.info(f"exception {str(err)}")
            return None

    def __contains__(self, name):
        """
        """
        return name in self._host_data

    def __getitem__(self, name):

        if self.expired(self._host_last_update_time) == True:
            self._query_host()

        name = name.lower()
        if name in self._host_data:
            return self._host_data[name]
        else:
            return None

    def __iter__(self):
        """
        """
        if self._host_data is None:
            self._host_data = self._query_host()
        yield self._host_data


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


class MySQLMonitor(threading.Thread, ItemSenderMixin, MySQLConnectionKeeperMixin, MySQLVariablesMonitorMixin, MySQLStatusMonitorMixin, MySQLSlaveMonitorMixin, MySQLMasterMonitorMixin, MySQLMGRMonitorMixin):
    """
    数据库层面的监控

    In [1]: from dbma import monitor                                                                                          

    In [2]: m = monitor.MySQLMonitor(host='127.0.0.1',monitor_user='root',monitor_password='',port=3306)                      

    In [3]: m.start()      # 启动子线程                                                                                                   

    In [4]: m.stop()       # stop 或 kill 会让线程跳出子循环                                                                                                     

    In [5]: m.join()       #                                                                                                     

    In [6]: m = None       # 这样才会触发 __del__ 去关闭连接
    """
    logger = logger.getChild("MySQLMonitor")

    def __init__(self, host="127.0.0.1", port=3306, monitor_user="monitor", monitor_password="dbma@0352", expire_seconds=7):
        """
        """
        threading.Thread.__init__(self, name=f"monitor-{port}", daemon=True)
        # threading.Thread(self,name=f"monitor-{port}",daemon=True)
        logger.info("__init__")
        self.host = host
        self.port = port
        self.monitor_user = monitor_user
        self.monitor_password = monitor_password
        # 监控项的过期时间设置了(7秒 expire_seconds 默认等于 7)
        self.expire_seconds = expire_seconds
        self.cnx = None
        self._kill_flag = False

    def _periodic_monitor(self):
        """
        周期性的对给定实例进行监制项收集 
        """
        logger = self.logger.getChild("_periodic_monitor")
        while True:
            logger.debug("periodic monitor prepare execute")
            MySQLStatusMonitorMixin._query_status(self)
            MySQLVariablesMonitorMixin._query_variables(self)
            MySQLSlaveMonitorMixin._query_slave(self)
            MySQLMasterMonitorMixin._query_master(self)
            MySQLMGRMonitorMixin._query_mgr(self)
            logger.debug("periodic monitor execute complete")

            # 比过期时间少一秒，尽可以的减少对数据的查询总次数
            time.sleep(self.expire_seconds - 1)

            if self._kill_flag == True:

                # 这个 return 会导致整个线程结束
                return

    def run(self):
        self._periodic_monitor()

    def __contains__(self, name):
        _lower_name = name.lower()

        if _lower_name in self.status:
            return True

        if _lower_name in self.slaves:
            return True

        if _lower_name in self.mgrs:
            return True

        if _lower_name in self.masters:
            return True

        if _lower_name in self.variables:
            return True

        return False

    def __getitem__(self, name):
        """
        """
        _lower_name = name.lower()

        if _lower_name in self.status:
            return self.status[_lower_name]

        if _lower_name in self.mgrs:
            return self.mgrs[_lower_name]

        if _lower_name in self.slaves:
            return self.slaves[_lower_name]

        if _lower_name in self.variables:
            return self.variables[_lower_name]

        if _lower_name in self.masters:
            return self.masters[_lower_name]

        return None

    def __iter__(self):
        """
        支持迭代 key 值
        """
        yield from self.status
        yield from self.slaves
        yield from self.mgrs
        yield from self.variables
        yield from self.masters

    def items(self):
        """
        模拟字典的 items 函数
        """
        for k in self:
            yield k, self[k]

    def kill(self):
        """
        打开自动退出子线程的开关
        """
        self._kill_flag = True

    stop = kill


class Mmps(object):
    """
    MySQL-Monitor-Port-Scan
    """

    logger = logger.getChild("Mmps")

    def __init__(self, monitor_user="monitor", monitor_password="dbma@0352"):
        self.monitor_user = monitor_user
        self.monitor_password = monitor_password

    def _query_all_possible_port(self):
        """
        查询出所有可能的 MySQL 的监听端口
        """
        logger = self.logger.getChild("_query_all_possible_port")
        with common.sudo("mysql-monitor-port-scan"):
            # 命令返回的是 bytes
            try:

                output_bytes = subprocess.check_output(
                    "netstat -ltnp | grep mysqld", shell=True)
            except subprocess.CalledProcessError:

                # 如果没有 mysql 数据库在运行，这里会报异常
                return []

            # 把 bytes 编码成 str
            output_str = output_bytes.decode('utf8')

            # 把包含 \n 的 str 转换成数组
            lines = [_ for _ in output_str.split('\n') if _ != '']

            # 从行中抽取出 ip:port 的部分
            ip_ports = []
            for line in lines:
                _, _, _, ip_port, *_ = line.split()
                ip_ports.append(ip_port)

            # 抽取出 port
            ports = []
            for ip_port in ip_ports:
                * _, port = ip_port.split(':')
                ports.append(int(port))
            return ports

    def _is_sql_port(self, port=3306):
        """
        检查给定的端口是不是 sql 端口
        """
        logger = self.logger.getChild("_is_sql_port")

        # 阅读 mysql-connector-python 的源代码后发现 connector.connect 支持一个叫 connection_timeout 的参数
        # 通过这个参数就不在信赖低层 socket 的 timeout 机制了
        # 先用 socket 进行粗排
        #client_socket = None
        # try:
        #    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #    client_socket.connect(('127.0.0.1',port))
        #    client_socket.settimeout(0.1)
        #    #MySQL协议下是由Server端先发送握手信息到client的
        #    message = client_socket.recv(1024)
        #    message = message.decode('latin-1').lower()
        #    #if 'password' in message:
        #    #    return port
        # except Exception as e:
        #    return False
        # finally:
        #    if hasattr(client_socket,'close'):
        #        client_socket.close()

        cnx = None
        try:
            cnx = connector.connect(host="127.0.0.1", port=port,
                                    user=self.monitor_user, password=self.monitor_password, connection_timeout=1)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("select @@port")
            data = cursor.fetchone()

            # 如果 @@port 等于当前给定的 port 那么就返回 True
            return data['@@port'] == port
        except connector.errors.ProgrammingError:

            # monitor 用户连接 admim_port 时会有这个异常
            return False
        except connector.errors.DatabaseError:

            # montior 用户连接 x 协议时会报这个错
            return False
        except Exception as err:
            # 没有对超时做特别的处理，也就是连接超时的时候会进入到这里
            logger.warning(type(err))
            logger.warning(
                f"got error '{err}',when checking {port} is a sql port or not")
            return False
        finally:
            if hasattr(cnx, 'close'):
                cnx.close()

        # 死代码，永远都不应该执行到这里
        logger.warning("dead code got execute !!!")
        return False

    def get_all_sql_port(self):
        """
        """
        ports = []
        for port in self._query_all_possible_port():
            if self._is_sql_port(port):
                ports.append(port)

        return ports
