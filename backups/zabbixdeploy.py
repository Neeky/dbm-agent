"""
实现 zabbix-agent 的安装与配置

1、zabbix-agent 的安装包使用的是官方提供的静态安装包(解压就能用的那那种)
   https://www.zabbix.com/download_agents#tab:40LTS

2、
"""
# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import re
import os
import sys
import time
import socket
import random
import shutil
import pathlib
import logging
import threading
import subprocess
from mysql import connector
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from . import checkings
from .dbmacnf import cnf
from . import errors
from . import common

logger = logging.getLogger('dbm-agent').getChild(__name__)


class ZabbixAgentInstallerMixin(object):
    """
    抽象出所有 MYSQL 安装&卸载过程中所有的操作、安装介质为官方表态二进制包

    https://www.zabbix.com/download_agents#tab:40LTS
    """
    logger = logger.getChild("ZabbixInstallerMixin")

    #
    pkg_pattern = re.compile(
        r"^zabbix_agents-(\d\.\d\.\d{1,2})-linux3.0-amd64-static.tar.(gz|xz)")

    def _basic_checks(self):
        """
        完成执行 zabbix-agent 安装之前的检查工作

        @UserAlreadyExistsError
        @NotSupportedZabbixAgentVersionError
        @DirecotryAlreadyExistsError
        @FileNotExistsError
        """
        logger = self.logger.getChild("_basic_checks")

        logger.debug(f"checking user '{self.zabbix_user}' exists or not")
        if checkings.is_user_exists(self.zabbix_user):

            # 由于是安装逻辑所以要求 zabbix 用户事先不存在、如果用户存在就报错
            logger.error(f"user '{self.zabbix_user}' already exists")
            raise errors.UserAlreadyExistsError(self.zabbix_user)

        logger.debug(f"chekcing '{self.pkg}' is spported or not ")
        if not self.pkg_pattern.search(self.pkg):

            # 遇到了不被支持的 zabbix-agent 包
            logger.error(
                f"zabbix agent install package '{self.pkg}' is not been supported ")
            logger.error(
                "please use offical static package https://www.zabbix.com/download_agents#tab:40LTS")
            raise errors.NotSupportedZabbixAgentVersionError(self.pkg)

        # 如果检查版本满足条件那么一定可以拿到版本号 如 4.0.15
        #self.zabbix_version = self.pkg_pattern.search(self.pkg).group(1)

        logger.debug(
            f"checking directory '{self.zabbix_basedir}' exists or not")
        if checkings.is_directory_exists(self.zabbix_basedir):

            # 安装目录已经存在
            logger.warning(f"'{self.zabbix_basedir}' exists")
            raise errors.DirecotryAlreadyExistsError(self.zabbix_basedir)

        # 检查安装包是否存在
        logger.debug(f"checking pkg '{self.pkg}' exists or not")
        full_pkg_path = os.path.join(cnf.base_dir, f'pkg/{self.pkg}')
        if not checkings.is_file_exists(full_pkg_path):

            # 安装包不存在
            logger.error(f"pkg not exists '{full_pkg_path}'")
            raise errors.FileNotExistsError(full_pkg_path)

        logger.info("all checkings complete")

    def _create_user(self):
        """
        创建 zabbix 用户
        """
        logger = self.logger.getChild("_create_user")
        logger.debug("start checking zabbix user exists or not")

        if checkings.is_user_exists(self.zabbix_user):

            # 存在就报错
            raise errors.UserAlreadyExistsError(self.zabbix_user)

        # 如果可以执行到这里说明 zabbix 用户不存在，并可以创建
        with common.sudo("create zabbix user"):
            common.create_user(self.zabbix_user)

        logger.info(f"use '{self.zabbix_user}' create complete")

    def _extract_pkg(self):
        """
        解压静态安装包
        """
        logger = self.logger.getChild("_extract_pkg")
        logger.debug(f"start extract install package '{self.pkg}' ")

        with common.sudo("extract zabbix-agent install pkg"):
            full_pkg_path = os.path.join(self.dbma.base_dir, f'pkg/{self.pkg}')
            #self.base_dir = f'/usr/local/zabbix-{self.zabbix_version}'

            # 解压安装包到指定的目录，如/usr/local/zabbix-4.0.15
            shutil.unpack_archive(
                full_pkg_path, self.zabbix_basedir)

            # 设置属主，属组
            common.recursive_change_owner(
                self.zabbix_basedir, self.zabbix_user, self.zabbix_user)

    def _render_zabbix_config(self):
        """
        渲染 zabbix-agent 的配置文件模板
        """
        logger = self.logger.getChild("_render_zabbix_config")

        # 加载配置文件模板
        template_dir = os.path.join(self.dbma.base_dir, 'etc/templates/')
        self.tmpl = Environment(loader=FileSystemLoader(
            searchpath=template_dir)).get_template("zabbix_agentd.conf.jinja")

        # 配置全局字典
        self.tmpl.globals = {
            'server_ip': self.server_ip,
            'agent_ip': self.agent_ip,
            'host_name': self.host_name}

        # 配置文件渲染后的出口文件
        self.zabbix_agent_config_file = os.path.join(
            f"{self.zabbix_basedir}", 'conf/zabbix_agentd.conf')

        #
        with common.sudo(f"render config file {self.zabbix_agent_config_file}"):
            with open(f"{self.zabbix_agent_config_file}", 'w') as cnf:
                cnf.write(self.tmpl.render())

        logger.info(
            f"render mysql config file {self.zabbix_agent_config_file}")

    def _create_link(self):
        """
        创建相关的连接文件
        1、连接 /usr/local/zabbix_agents-4.0.15-linux3.0-amd64-static 到 /usr/local/zabbix
        2、连接 /usr/local/zabbix_agents-4.0.15-linux3.0-amd64-static/conf 到 /usr/local/zabbix_agents-4.0.15-linux3.0-amd64-static/etc/
        """

        with common.sudo("create link file"):
            # 如果对应的连接文件存在就删除
            if os.path.islink('/usr/local/zabbix'):
                os.remove('/usr/local/zabbix')

            # 如果对应的连接文件存在就删除
            if os.path.islink("/usr/local/zabbix/etc"):
                os.remove("/usr/local/zabbix/etc")

            # 创建连接文件
            os.symlink(self.zabbix_basedir, "/usr/local/zabbix")
            os.symlink("/usr/local/zabbix/conf", "/usr/local/zabbix/etc")

            # 创建配置目录
            os.mkdir("/usr/local/zabbix/etc/zabbix_agentd.conf.d")

            #
            shutil.rmtree("/usr/local/zabbix/etc/zabbix_agentd")

            # 调整权限
            common.recursive_change_owner(
                self.zabbix_basedir, self.zabbix_user, self.zabbix_user)

    def _export_path(self):
        """
        导出环境变量
        """
        logger = self.logger.getChild("_export_path")
        logger.debug("entry config path variable logic")

        # 进入 root 模式
        with common.sudo("export path"):

            # 和一步检查一下 zabbix-agent 相关
            zabbix_bin = "export PAYH=/usr/local/zabbix/bin/:$PATH\n"
            zabbix_sbin = "export PAYH=/usr/local/zabbix/sbin/:$PATH\n"
            _has_been_exported = False

            with open("/etc/profile") as f_profile:
                for line in f_profile:
                    if line == zabbix_sbin:

                        # 如果已经完成了配置会进入到这里、标记 _has_been_exported 为 True
                        _has_been_exported = True

            # 如果 _has_been_exported == False 说明 path 还没有被导出
            if _has_been_exported == False:
                with open("/etc/profile", 'a') as f_profile:
                    f_profile.write('\n')
                    f_profile.write(zabbix_sbin)
                    f_profile.write(zabbix_bin)

        logger.info("export path complete")

    def _config_user_parameter(self):
        """
        配置用户自定义监控项，向 /usr/local/zabbix/etc/zabbix_agentd.conf.d/dbma.conf 文件写入

        UserParameter=dbma[*],/usr/local/python/bin/dbma-cli-mysql-monitor-item --port=$2 --gateway-port=$3 $1
        """
        logger = self.logger.getChild("_config_user_parameter")
        logger.debug("enter config UserParameter logic")

        config_file = "/usr/local/zabbix/etc/zabbix_agentd.conf.d/dbma.conf"
        with open(config_file, 'w') as f_config:
            f_config.truncate()
            cmd = shutil.which("dbma-cli-mysql-monitor-item")
            user_parameter = f"UserParameter=dbma[*],{cmd} --port=$2 --gateway-port=$3 $1\n"
            f_config.write(user_parameter)

        logger.info("config UserParameter complete")

    def _config_systemd(self):
        """
        配置 systemd
        """
        zabbix_systemd = "/usr/lib/systemd/system/zabbix-agentd.service"
        with common.sudo("config zabbix systemd"):

            # 如果文件存在就删除
            if checkings.is_file_exists(zabbix_systemd):
                os.remove(zabbix_systemd)

            # 配置新的 systemd 文件
            # shutil.copyfile(self.dbma.)
            src = os.path.join(self.dbma.base_dir,
                               'etc/templates/zabbix-agentd.service')
            shutil.copyfile(src, zabbix_systemd)

    def _enable_zabbix_agent(self):
        """
        配置 zabbix-agentd 开机启动
        """
        logger = self.logger.getChild("_enable_zabbix_agent")
        with common.sudo(f"enable systemd zabbix-agentd"):
            subprocess.run(['systemctl daemon-reload'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(
                [f'systemctl enable zabbix-agentd'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("config zabbix-agent auto start on boot complete")

    def _start_zabbix_agent(self):
        """
        """
        logger = self.logger.getChild("_start_zabbix_agent")
        with common.sudo(f"enable systemd zabbix-agentd"):
            subprocess.run(['systemctl start zabbix-agentd'], shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("zabbix-agent start complete")

    def install(self):
        """
        """
        logger = self.logger.getChild("install")
        logger.info(f"prepare install zabbix agent using {self.pkg}")

        # 检查安装的前置条件
        try:
            self._basic_checks()

        except errors.DirecotryAlreadyExistsError as err:

            # /usr/local/zabbix_agents-4.0.16-linux3.0-amd64-static 已经存在
            now = datetime.now().isoformat()
            with common.sudo("backup the old zabbix-agent"):
                shutil.move(self.zabbix_basedir,
                            self.zabbix_basedir + '-backup-' + now)
        except Exception as err:
            logger.error(f"{err}")
            logger.error("install zabbix agent fail")
            return

        # 能执行到这里说明、满足所有条件开始安装

        self._create_user()
        self._extract_pkg()
        self._render_zabbix_config()
        self._create_link()
        self._export_path()
        self._config_user_parameter()
        self._config_systemd()
        self._enable_zabbix_agent()
        self._start_zabbix_agent()


class ZabbixAgentUninstallerMixin(object):
    """
    """

    logger = logger.getChild('ZabbixAgentUninstallerMixin')

    def _basic_checks(self):
        """
        """
        logger = self.logger.getChild("_basic_checks")

        # 检查 zabbix-agentd 是否在运行
        logger.info("checking zabbix-agentd is runing or not")
        if checkings.is_file_exists("/tmp/zabbix_agentd.pid") or checkings.is_port_in_use(ip="127.0.0.1", port=10050):
            raise errors.PortIsInUseError("zabbix-agent is runing")

        # 检查 zabbix 用户是否存在
        #logger.info(f"checking '{self.zabbix_user}' is exists or not")
        # if not checkings.is_user_exists(self.zabbix_user):
        #    logger.error(f"'{self.zabbix_user}' user not exists")
        #    raise errors.UserNotExistsError(self.zabbix_user)

        # 检查 /usr/local/zabbix 是否存在
        #logger.info(f"checking link file '/usr/local/zabbix' exists or not")
        # if not os.path.islink("/usr/local/zabbix"):
        #    logger.error(f"link file '/usr/local/zabbix' not exists")
        #    raise errors.FileNotExistsError("/usr/local/zabbix")

        # 检查 /usr/lib/systemd/system/zabbix-agentd.service
        # logger.info(
        #    "checking '/usr/lib/systemd/system/zabbix-agentd.service' exists or not")
        # if not os.path.isfile("/usr/lib/systemd/system/zabbix-agentd.service"):
        #    logger.error(
        #        f"'/usr/lib/systemd/system/zabbix-agentd.service' not exists")
        #    raise errors.FileNotExistsError(
        #        "/usr/lib/systemd/system/zabbix-agentd.service")

        logger.info("all chechkings are ok")

    def _delete_user(self):
        """
        删除 zabbix 用户
        """
        logger = self.logger.getChild("_delete_user")

        logger.debug("prepare delete user zabbix")
        if checkings.is_user_exists(self.zabbix_user):
            common.delete_user(self.zabbix_user)

        logger.info("delete user complete")

    def _disable_systemd(self):
        """
        关闭 zabbix-agentd 的开机启动、并删除 systemd 配置文件
        """
        logger = self.logger.getChild("_disable_systemd")

        logger.debug("prepare disable zabbix-agentd")
        with common.sudo("disable zabbix-agentd"):
            if os.path.exists("/usr/lib/systemd/system/zabbix-agentd.service"):
                # subprocess.run(['systemctl stop zabbix-agentd'], shell=True,
                #               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run(
                    [f'systemctl disable zabbix-agentd'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info("disable zabbix-agentd complete")

                os.remove("/usr/lib/systemd/system/zabbix-agentd.service")

                logger.info("remove zabbix-agentd.service complete")

    def _remove_link(self):
        logger = self.logger.getChild("_remove_link")

        logger.debug("prepare remove link file '/usr/local/zabbix' ")
        with common.sudo("remove link file"):
            if os.path.exists("/usr/local/zabbix"):
                os.remove("/usr/local/zabbix")

        logger.info("remove link file complete")

    def uninstall(self):
        """
        实现卸载 zabbix-agent 相关的逻辑
        """
        logger = self.logger.getChild("uninstall")
        logger.info("enter uninstall zabbix logic")

        try:
            self._basic_checks()
        except Exception as err:
            logger.error(f"got exception during checkings {err}")
            return

        # 能执行到这里说明所有的检查都已经通过了

        self._delete_user()
        self._disable_systemd()
        self._remove_link()

        logger.info("uninstall zabbix-agent complete")


class ZabbixAgentInstaller(threading.Thread, ZabbixAgentInstallerMixin):
    """
    """
    logger = logger.getChild("ZabbixAgentInstaller")

    def __init__(self, server_ip="172.16.192.100", agent_ip="172.16.192.200", host_name=None, pkg="zabbix_agents-4.0.15-linux3.0-amd64-static.tar.gz"):
        """
        """
        # 获取 logger 对象
        logger = self.logger.getChild("__init__")

        # 初始化线程
        threading.Thread.__init__(
            self, name='iza', daemon=True)
        logger.debug(
            f"enter install zabbix-agent logic server_ip = {server_ip} agent_ip={agent_ip}")

        # 基础变量
        self.pkg = pkg
        self.zabbix_user = 'zabbix'
        self.agent_ip = agent_ip
        self.server_ip = server_ip
        self.zabbix_basedir_prefix = "/usr/local/"
        self.host_name = host_name
        self.dbma = cnf

        # 计算变量
        # 配置文件中的主机名
        if self.host_name is None:

            # 如果没有指定 host_name 就把 host_name 设置成 agent_ip
            self.host_name = self.agent_ip

        # 在检查版本被支持后会设定这个值为对应的版本号、如 4.0.15
        _m = self.pkg_pattern.search(self.pkg)
        if _m:

            # 如果可以执行到这里说明匹配成功，准备解析出版本号
            self.zabbix_version = _m.group(1)

        # 完整的包版本号
        self.zabbix_agent_full_version = self.pkg.replace(
            '.tar.gz', '').replace('.tar.xz', '')

        # 完整的安装路径 如 /usr/local/zabbix_agents-4.0.15-linux3.0-amd64-static
        self.zabbix_basedir = os.path.join(
            self.zabbix_basedir_prefix, self.zabbix_agent_full_version)

    def run(self):
        """
        """
        self.install()


class ZabbixAgentUninstaller(threading.Thread, ZabbixAgentUninstallerMixin):
    logger = logger.getChild("ZabbixAgentUninstaller")

    def __init__(self):
        """
        """
        self.zabbix_user = "zabbix"

        #
        threading.Thread.__init__(self, name='uza', daemon=True)

    def run(self):
        self.uninstall()
