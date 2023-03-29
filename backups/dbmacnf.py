import os
import configparser
from . import checkings


class DbmCnf(object):
    """
    读取配置文件并包装成实例属性以方便使用
    """

    def __init__(self):
        """
        """
        # 这种实例虽然简单，但是编码时缺少智能提示，所以不要了
        # try:
        #    parser = configparser.ConfigParser(allow_no_value=True,inline_comment_prefixes='#')
        #    parser.read("/usr/local/dbm-agent/etc/dbma.cnf")
        #    self.__dict__ = dict(parser['dbma'])
        # except Exception :
        #    self.__dict__ = {}
        if not checkings.is_file_exists('/usr/local/dbm-agent/etc/dbma.cnf'):
            # 如果文件不存在就使用默认值
            self.host_uuid = "dde1f082-67fc-436f-a149-90a1fa4612c2"
            self.dbmc_site = "http://172.16.192.1:8080"
            self.base_dir = "/usr/local/dbm-agent/"
            self.config_file = "etc/dbma.cnf"
            self.log_file = "logs/dbma.log"
            self.log_level = "info"
            self.user_name = "dbma"
            self.pid = "/tmp/dbm-agent.pid"
            self.init_pwd = "dbma@0352"
            self.net_if = "ens33"
            self.mysql_install_dir = "/usr/local/"
            
        else:
            parser = configparser.ConfigParser(
                allow_no_value=True, inline_comment_prefixes='#')
            parser.read("/usr/local/dbm-agent/etc/dbma.cnf")

            self.host_uuid = parser['dbma'].get(
                'host_uuid', 'dde1f082-67fc-436f-a149-90a1fa4612c2')
            self.dbmc_site = parser['dbma'].get(
                'dbmc_site', 'http://172.16.192.1:8080')
            self.base_dir = parser['dbma'].get(
                'base_dir', '/usr/local/dbm-agent/')
            self.config_file = parser['dbma'].get(
                'config_file', 'etc/dbma.cnf')
            self.log_file = parser['dbma'].get('log_file', 'logs/dbma.log')
            self.log_level = parser['dbma'].get('log_level', 'info')
            self.user_name = parser['dbma']['user_name']
            self.pid = parser['dbma']['pid']
            self.init_pwd = parser['dbma']['init_pwd']
            self.net_if = parser['dbma']['net_if']
            self.mysql_install_dir = parser['dbma'].get(
                'mysql_install_dir', '/usr/local/')

        # API 固定以减小配置文件中的选项数量
        self.api_host = "dbmc/hosts/"
        self.api_cpu_times = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/cpu-times/".format(self.host_uuid))
        self.api_cpu_frequences = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/cpu-frequences/".format(self.host_uuid))
        self.api_net_io_counters = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/net-io-counters/".format(self.host_uuid))
        self.api_net_interfaces = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/net-interfaces/".format(self.host_uuid))
        self.api_memory_distributions = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/memory-distributions/".format(self.host_uuid))
        self.api_disk_usages = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/disk-usages/".format(self.host_uuid))
        self.api_disk_io_counters = os.path.join(
            self.dbmc_site, "dbmc/hosts/{0}/disk-io-counters/".format(self.host_uuid))


cnf = DbmCnf()
