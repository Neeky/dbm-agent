"""实现所有于 http-center 之间的通信接口
"""

import os
import re
import logging
import requests
from datetime import datetime

import psutil
import distro
from .dbmacnf import cnf
from .version import agent_version


logger = logging.getLogger('dbm-agent').getChild(__name__)


class HttpClientMixin(object):
    """实现 http(s) 会话保持等相关功能
    """
    _session = None
    _lastest_request_time = None
    _expire_times = 79
    _times = 0
    logger = logger.getChild("HttpClient")

    def get_session(self):
        """创建一个连接到 dbmc 的 session 对象并返回，如果连接不上就返回 None
        """
        logger = self.logger.getChild("get_session")

        # 注销掉之前的 session
        if self._session is not None and hasattr(self._session, 'close'):
            logger.info("going to close older session object")
            self._session.close()
            self._session = None

        # 创建出新的 session
        csrf_url = os.path.join(cnf.dbmc_site, 'dbmc/csrf')
        try:
            logger.info(f"connect to '{csrf_url}' ")
            session = requests.Session()
            session.get(csrf_url, timeout=0.01)
            self._session = session
            self._lastest_request_time = datetime.now()
            logger.info("create new session success")
        except Exception as err:
            logger.warning(f"exception create new session fail '{str(err)}' ")
            self._session = None

        return self.session

    @property
    def session(self):
        """如果 dbmc 可用就返回一个 Session 对象，如果不可用就返回 None 值

        """
        logger = self.logger.getChild("session")

        # 每一次请求 session 都会使得 self._times + 1
        # 这样就使得每一个 session 被使用 _expire_times 次就会自动释放
        self._times = self._times + 1
        if self._times % self._expire_times == 0:
            #
            self._times = 0
            session = self.get_session()
            return session

        # _session 不会空直接返回
        if self._session is not None:
            logger.info("session is usable")
            return self._session

        # _session 为空，那么 60 秒内不要重复的请求
        # 如果执行到这里说明 session 是 None
        if self._lastest_request_time is None:

            # _lastest_request_time 是 None 但是之前重来没有请求过，这里就请求一次
            session = self.get_session()
            return session
        else:

            # _lastest_request_time 不是 None 说明之前请求过一次，看一下有没有超时
            now = datetime.now()
            expire_second = (now - self._lastest_request_time).second
            if expire_second <= 60:
                return None
            else:
                session = self.get_session()
                return session

    def post(self, url=None, data=None, timeout=1):
        """所有的 post 请求都由这里实现
        """
        logger = self.logger.getChild("post")
        if url is None:
            logger.error("exception url is None cant not post data to dbmc")
            return

        if data is None:
            logger.error("exception data is None,nothing to post")
            return

        # 可以成功执行到这里说明基本正确
        if 'csrftoken' not in self._session.cookies:
            logger.warning("exception miss csrftoken in session.cookies")
            return

        # 添加 csrftoken 标记
        data.update(
            {'csrfmiddlewaretoken': self._session.cookies['csrftoken']})

        try:

            # 发送请求
            response = self._session.post(url, data=data, timeout=timeout)
            return response
        except Exception as err:
            logger.error(f"exception when post data to '{url}' '{str(err)}' ")
            return None


class HostMonitorMixin(object):
    """实现主机层面监控数据的上报
    """
    logger = logger.getChild("HostMonitorMixin")
    # 根据 host_uuid 查询 host 的信息
    # http://127.0.0.1:8080/dbmc/hosts/api/hosts/detail/205a4069-2578-4fc0-b6af-e4bf0047dce0
    host_uuid_detail_view_url = os.path.join(
        cnf.dbmc_site, f"dbmc/hosts/api/hosts/detail/{cnf.host_uuid}")

    # http://127.0.0.1:8080/dbmc/hosts/api/hosts/create
    host_create_view_url = os.path.join(
        cnf.dbmc_site, f"dbmc/hosts/api/hosts/create")

    host_update_view_url = os.path.join(
        cnf.dbmc_site, f"dbmc/hosts/api/hosts/update/")
    _host_id = None

    @property
    def host_uuid(self):
        """
        """
        return cnf.host_uuid

    @property
    def host_id(self):
        """
        """
        logger = self.logger.getChild("host_id")

        if self._host_id is None:
            logger.info("host_id is None,we well query it from dbmc")
            host_id = self.get_host_id()
            return host_id

        return self._host_id

    def _prepare_host_monitor_data(self):
        """
        """
        # 构造数据
        data = {}
        data['host_uuid'] = self.host_uuid
        data['agent_version'] = agent_version
        data['cpu_cores'] = psutil.cpu_count()
        data['mem_total_size'] = psutil.virtual_memory().total
        data['os_version'] = ' '.join(distro.linux_distribution()).strip()

        def get_manager_ip():
            addresss = psutil.net_if_addrs()
            if cnf.net_if in addresss:
                # 给定网卡存在
                addres = addresss[cnf.net_if]
                for addr in addres:
                    # 返回 ipv4 地址
                    if addr.family == 2:
                        return addr.address
            else:
                return None
        data['manager_net_ip'] = get_manager_ip()

        return data

    def create_host(self):
        """上报当前主机的基本信息到 dbm-center
        """
        logger = self.logger.getChild("create_host")
        logger.info("start")

        # session 为空就直接返回
        if self.session is None:
            logger.warning("session is None")
            return

        try:

            data = self._prepare_host_monitor_data()

            logger.info(f"post {data} to {self.host_create_view_url}")

            # 发送请求
            response = self.post(url=self.host_create_view_url, data=data)

            # 检查结果
            logger.info("parser response to json")
            data = response.json()
            if 'pk' in data:
                logger.info(" pk in response.json")
                pk = data['pk']
                logger.info(f"create host success host.pk = {pk}")
            elif 'error-message' in data:
                logger.info('error-message in response.json')
                message = data['error-message']
                logger.warning(f"exception error-message='{message}' ")
            else:
                logger.error(f"exception response.json = {data}")

        except Exception as err:
            logger.warning(f"create host fail '{str(err)}' ")

    def update_host(self):
        """
        """
        logger = self.logger.getChild("update_host")
        logger.info("start")

        # 必要条件检查
        if self.session is None:
            logger.warning("session is None")
            return

        if self.host_id is None:
            logger.warning("host_id is None")
            return

        # 准备数据
        data = self._prepare_host_monitor_data()

        try:

            # update view 是根据 pk 来定位行的，所以要进行进一步处理才能用
            host_update_view_url = os.path.join(
                self.host_update_view_url, str(self.host_id))

            logger.info(f"post data {data} to {self.host_update_view_url}")
            response = self.post(url=host_update_view_url, data=data)
            logger.info("parser response to json")

            data = response.json()
            if 'pk' in data:
                logger.info("'pk' in response.json")
                logger.info("update host complete")
            elif 'error-message' in data:
                message = data['error-message']
                logger.warning(f"exception error-message='{message}' ")
            else:
                logger.error(f"exception response.json = {data}")

        except Exception as err:

            # 求知异常
            logger.warning(f"create host fail '{str(err)}' ")

    def get_host_id(self):
        """返回当前主机的 id 值
        """
        logger = self.logger.getChild("get_host_id")
        logger.info("start")

        #
        if self.session is None:
            logger.warning("session is None")
            return

        # 能执行到这里说明  session 存在
        try:

            # 准备请求 dbmc
            logger.info(f"requests '{self.host_uuid_detail_view_url}' ")
            response = self.session.get(
                self.host_uuid_detail_view_url, timeout=0.07)

            # 解析数据
            data = response.json()
            if 'pk' in data:

                # 正常情况
                self._host_id = data['pk']
            elif 'error-message' in data:

                # 已知的异常情况
                error = data['error-message']
                logger.warning(f"exception '{error}' ")
                self._host_id = None
            else:

                # 其它未知的异常
                logger.error(f"error '{response.text}' ")
                self._host_id = None

        except Exception as err:

            #
            logger.warning(f"exception '{str(err)}' ")
            self._host_id = None

        return self._host_id


class MonitorProxy(HttpClientMixin, HostMonitorMixin):
    pass
