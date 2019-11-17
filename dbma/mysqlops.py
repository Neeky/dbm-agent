  
# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import re
import os
import time
import shutil
import logging
import pathlib
import subprocess
import configparser
from . import errors
from . import common
from . import checkings
from . import configrender
import mysql.connector as connector

logger = logging.getLogger('dbm-agent').getChild(__name__)

_cores = 1

class MySQLInstaller(object):
    """
    所有 MySQL 安装操作的基类
    """
    logger = logger.getChild('MySQLInstaller')

    def pre_checkings(self):
        """
        完成安装 MySQL 之前的必要检查
        :errors.UserAlreadyExistsError
        :errors.FileAlreadyExistsError
        :errors.DirecotryAlreadyExistsError
        :errors.NotSupportedMySQLVersionError
        """
        # 获取日志对象
        logger = self.logger.getChild('pre_checkings')

        pkg_full_path = os.path.join('/usr/local/dbm-agent/pkg/',self.pkg)

        logger.info(f"using {pkg_full_path} install mysql")

        # 检查安装包是不是存在并且之前也从来没有安装过
        logger.info(f"check package '{pkg_full_path}' is exists")
        if not checkings.is_file_exists(pkg_full_path)   and   not checkings.is_directory_exists(self.mysql_basedir):
            # 如果安装包在 pkg 目录下不存在，并且之前也没有安装过这个包(/ur/local/ 目录下也没有这个包解析后的目录)
            # 说明没有包可用，所以要报错
            raise errors.FileNotExistsError(pkg_full_path)

        # 检查端口是否被占用
        logger.info(f"check port {self.port} is in use or not")
        if checkings.is_port_in_use('127.0.0.1',self.port):
            raise errors.PortIsInUseError(f"*:{self.port}")

        # 检查用户是否存在
        if checkings.is_user_exists(self.mysql_user):
            raise errors.UserAlreadyExistsError(f'user {self.mysql_user} already exists')

        # 检查配置文件是否存在
        logger.info(f"check config file  {self.mysql_cnf} ")
        if checkings.is_file_exists(self.mysql_cnf):
            raise errors.FileAlreadyExistsError(f"config file '{self.mysql_cnf}' already exists")

        # 检查 datadir 是否存在
        logger.info(f"check datadir {self.mysql_datadir}")
        if checkings.is_directory_exists(self.mysql_datadir):
            raise errors.DirecotryAlreadyExistsError(f"directory  {self.mysql_datadir} alread exists")

        # 检查版本号是否被支持
        logger.info(f"check mysql version {self.pkg}")
        if not checkings.is_an_supported_mysql_version(self.pkg):
            raise errors.NotSupportedMySQLVersionError(self.pkg)

        if not checkings.is_file_exists(self.init_file):
            raise errors.FileNotExistsError(self.init_file)

        # 检查配置文件模板是否存在，如果配置模板不存在那当前的版本也不被支持
        m = re.search(r'(8.0.\d\d)',self.version)
        if m :
            v = m.group(1)
            cnf_template_file_path = os.path.join(self.dbma_basedir,'etc/templates/',f"mysql-{v}.cnf.jinja")
            if not checkings.is_file_exists(cnf_template_file_path):
                logger.error(f"mysql cnf file template not exists")
                raise errors.FileNotExistsError(f"{cnf_template_file_path} not exists.")
            # 设置配置文件模板的名称
            self.tmpl_file = f"mysql-{v}.cnf.jinja"
        else:
            logger.error(f"not supported mysql version {self.version}")
            raise errors.NotSupportedMySQLVersionError(self.version)

    def __init__(self,port:int=3306,
                 pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",
                 dbma_basedir='/usr/local/dbm-agent/',
                 max_mem:int=1024,
                 cores=_cores):
        """
        MSQL 安装器的构造函数
        """
        logger = self.logger.getChild('__init__')

        self.port = port
        self.dbma_basedir = dbma_basedir
        self.pkg = pkg
        self.max_mem = max_mem
        self.cores = cores
        self.version = pkg.replace('.tar.gz','').replace('.tar.xz','')
        # 初始化文件是写死的
        self.init_file = '/usr/local/dbm-agent/etc/init-users.sql'
        self.mysql_basedir = os.path.join('/usr/local/',self.version)
        self.mysql_datadir = os.path.join('/database/mysql/data/',str(self.port))
        self.mysql_cnf = f"/etc/my-{self.port}.cnf"
        self.mysql_user = f"mysql{self.port}"

        #def get_version_number(version:str="mysql-8.0.17-linux-glibc2.12-x86_64"):
        #    """
        #    返回 MySQL 的版本号
        #    """
        #    m = re.search(r'-(8.0.\d\d)-',version)
        #    if m:
        #        return m.group(1)
        #    else:
        #        return None
        # 取得数值版本号 8.0.18 vesion 的格式不
        # version_number = get_version_number(version)

        #self.mysql_cnf_render = configrender.MysqlRender(pkg=self.pkg,port=self.port,max_mem=self.max_mem,cores=self.cores)

        logger.info(f"install mysql instance with {self.pkg} port {self.port} max_mem {self.max_mem} MB cores = {cores}")

    def create_datadir(self):
        """
        创建数据目录
        :errors.DirecotryAlreadyExistsError
        """
        logger = self.logger.getChild('create_datadir')
        # 双重检测
        logger.info(f"create datadir /database/mysql/data/{self.port}")
        if checkings.is_directory_exists(f"/database/mysql/data/{self.port}"):
            raise errors.DirecotryAlreadyExistsError(f"directory  '/database/mysql/data/{self.port}' alread exists")

        datadir = pathlib.Path(f'/database/mysql/data/{self.port}')
        datadir.mkdir(parents=True)
        
        #os.mkdir(f'/database/mysql/data/{self.port}')

    def unarchive_pkg(self):
        """
        解压安装包
        """
        logger = self.logger.getChild('unarchive_pkg')

        logger.info("unarchive mysql pkg to /usr/local/")
        if checkings.is_directory_exists(os.path.join('/usr/local/',self.version)):
            logger.warning(f"{os.path.join('/usr/local/',self.version)} exists mysql may has been installed. skip untar {self.pkg} to /usr/local/")
            return
        # 这里是双重检查，pre_checkings 已经有对安装包版本的检查
        if not checkings.is_an_supported_mysql_version(pkg=self.pkg):
            raise errors.NotSupportedMySQLVersionError(f'not a supported mysql version "{self.pkg}" ' )
        # 获取安装包
        pkg_full_path = os.path.join(self.dbma_basedir,'pkg',self.pkg)

        if not checkings.is_file_exists(pkg_full_path):
            raise errors.FileNotExistsError(f'{pkg_full_path}')
        # 解压并更新目录权限
        with common.sudo("unarchive mysql install pkg"):
            shutil.unpack_archive(pkg_full_path,'/usr/local/')
            common.recursive_change_owner(os.path.join('/usr/local/',self.version),user="root",group="mysql")

    def init_database(self):
        """
        完成数据库 init
        """
        logger = self.logger.getChild('init_database')
        # mysql-8.0.18 版本及以上版本在 --initialize 时已经不再加载非必要插件
        # 如果配置文件中包含非必要插件和参数会使得 --initialize 过程出错并退出
        # 解决办法是 --initialize 阶段使用的配置文件和运行时的配置分离
        # 渲染配置文件到 /tmp/my.cnf
        render = configrender.MysqlRender(pkg=self.pkg,port=self.port,max_mem=self.max_mem,cores=self.cores,tmpl_file='mysql-8.0-init-only.jinja')
        render.render_init_only()

        logger.info("init database with --initialize-insecure")
        with common.sudo("init database"):
            args = [f'/usr/local/{self.version}/bin/mysqld',f'--defaults-file=/tmp/my.cnf',
                            '--initialize-insecure',f'--user=mysql{self.port}',f'--init-file={self.init_file}']
            logger.warning(args)
            subprocess.run(args,capture_output=True)
            os.remove('/tmp/my.cnf')


    def config_systemd(self):
        """
        配置 systemd
        """
        logger = self.logger.getChild('config_systemd')

        logger.info(f"config service(systemd) and daemon-reload")
        systemd = configrender.MySQLSystemdRender(pkg=self.pkg,port=self.port)
        systemd.render()
        with common.sudo(f"systemctl daemon reload"):
            subprocess.run(['systemctl daemon-reload'],shell=True)

    def start_mysql(self):
        """
        启动 MySQL
        """
        logger = self.logger.getChild('start_mysql')

        logger.info(f"start mysqld-{self.port} by systemctl start mysqld-{self.port}")
        with common.sudo(f"start mysql server {self.port}"):
            subprocess.run(f"systemctl start mysqld-{self.port}",shell=True)

    def config_path(self):
        """
        配置 PATH 环境变量
        """
        logger = self.logger.getChild('config_path')

        logger.info(f"config path env variable /usr/local/{self.version}/bin/")
        common.config_path(path=f"/usr/local/{self.version}/bin/",user_name=f"mysql{self.port}")

    def enable_service(self):
        """
        配置 数据库开机启动
        """
        logger = self.logger.getChild('enable_service')

        logger.info(f"config mysql auto start on boot")
        common.enable_service(f"mysqld-{self.port}")
    
    def config_so(self):
        """
        配置 so
        """
        logger = self.logger.getChild('config_so')

        logger.info(f"export so file")
        common.config_mysql_so(self.version)

    def config_include(self):
        """
        配置 头文件
        """
        logger = self.logger.getChild('config_include')

        logger.info(f"export header file")
        common.config_mysql_include(self.version)

    def pre_install(self):
        """
        实现：
        1、安装前的检测
        2、用户创建
        3、数据目录创建
        4、安装包解压
        """
        logger = self.logger.getChild('pre_install')

        # 安装前的检测，通过之后会给实例增加 tmpl_file 属性
        self.pre_checkings()
        
        # 如果前置的检查都通过了那么开始创建用户
        common.create_user(f"mysql{self.port}")

        # 创建数据目录
        self.create_datadir()

        # 解压安装包
        self.unarchive_pkg()

        # 创建配置文件渲染器
        self.mysql_cnf_render = configrender.MysqlRender(pkg=self.pkg,port=self.port,max_mem=self.max_mem,cores=self.cores,tmpl_file=self.tmpl_file)

    def post_install(self):
        """
        实现
        1、配置 mysqld-{port} 服务
        2、配置 mysqld-{port} 开机启动
        2、导出 环境变量
        3、启动 mysqld-{port} 服务
        4、导出 共享库
        5、导出 头文件
        """
        logger = self.logger.getChild('post_install')
        # 配置 systemd
        self.config_systemd()

        # 配置自动启动
        self.enable_service()

        # 配置环境变量
        self.config_path()

        # 启动
        self.start_mysql()

        # 导出共享库
        self.config_so()

        # 导出头文件
        self.config_include()

    def install(self):
        """
        实现：
        1、执行安装前置操作
        2、渲染配置文件到 /etc/my-{port}.cnf
        3、init database
        4、执行安装后置操作
        """
        raise NotImplementedError()


class MySQLSingleInstaller(MySQLInstaller):
    """
    实现单机的自动安装与配置
    """
    logger = logger.getChild('MySQLSingleInstaller')

    def install(self):
        """
        实现：
        1、执行安装前置操作
        2、渲染配置文件到 /etc/my-{port}.cnf
        3、init database
        4、执行安装后置操作
        """
        logger = self.logger.getChild('install')

        try:
            self.pre_install()
        except Exception as err:
            # 如果检测中通过错误就停止
            logger.error(str(err))
            return
        self.mysql_cnf_render = configrender.MysqlRender(pkg=self.pkg,
                                    port=self.port,
                                    max_mem=self.max_mem,
                                    cores=self.cores,
                                    tmpl_file=self.tmpl_file)
        self.mysql_cnf_render.render()

        self.init_database()

        self.post_install()

        logger.info("install single mysql instance complete")


class MySQLMGRInstaller(MySQLInstaller):
    """
    MGR 集群的安装
    """
    logger = logger.getChild('MySQLMGRInstaller')

    def __init__(self,port:int=3306,pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",
                 dbma_basedir='/usr/local/dbm-agent/',
                 max_mem:int=1024,cores=_cores,
                 local_address:str="127.0.0.1:33061",
                 group_seeds="127.0.0.1:33601,127.0.0.1:33062,127.0.0.1:33063"):
        logger = self.logger.getChild('__init__')

        super().__init__(port=port,pkg=pkg,dbma_basedir=dbma_basedir,max_mem=max_mem,cores=cores)

        self.local_address = local_address
        self.group_seeds = group_seeds
        logger.info("entry mysql group replication install logic")

    def pre_checkings(self):
        """
        在基本检测项之上添加 MGR 专用的检测项
        """
        logger = self.logger.getChild('pre_checkings')

        super().pre_checkings()

        # MGR 专用的检查项
        # 1、参数检查
        # local_address 要满足 xxxx:yyyy 这样的模式
        logger.info(f"check group_replication_local_address = {self.local_address} option is right or not")
        if not re.search(r"[\s\S]*:\d{1,5}",self.local_address):
            raise errors.MgrLocalAddressError(f"group_replication_local_address = {self.local_address}")
        # 2、检查 ip 是不是一个本机的 IP 
        ip,port = self.local_address.split(":")
        if not checkings.is_local_ip(ip):
            raise errors.NotALocalIPError(f"{ip} not a local ip")
        # 3、检查端口是否在被使用
        if checkings.is_port_in_use(ip,int(port)):
            raise errors.PortIsInUseError(f"{ip}:{port}")
        # 4、检查 group_seeds 是否一个正确的格式
        logger.info(f"check group_replication_group_seeds = {self.group_seeds} option is right or not")
        if ',' not in self.group_seeds:
            raise errors.MgrGroupSeedsError(f"group_replication_group_seeds = {self.group_seeds}")

        for local_address in self.group_seeds.split(','):
            if not re.search(r"[\s\S]*:\d{1,5}",local_address):
                raise errors.MgrLocalAddressError(f"group_replication_local_address = {self.local_address}")
        
        logger.info(f"change hostname to mgr{ip.replace('.','_')}")
        common.config_hostname('mgr'+ip.replace('.','_'))
        
        logger.info("config dns")
        for local_address in self.group_seeds.split(','):
            ip,_ = local_address.split(':')
            common.resolve_dns(ip,'mgr')
        
    def post_install(self):
        """
        添加 MGR 特有的安装后的操作
        """
        logger = self.logger.getChild('post_install')

        super().post_install()
        common.wait_until_tcp_ready('127.0.0.1',self.port)
        logger.info("sleep 7 secondes wait for mysql protoco avaiable")
        time.sleep(7)
        # 如果是 IP 列表中的第一个 IP 说明这个是 PRIMARY、那要执行 PRIMARY 相关的逻辑
        is_primary = False
        if self.group_seeds.startswith(self.local_address):
            logger.info("this is a primary node prepare bootstrap a group")
            is_primary = True
        else:
            logger.info("this is seconder node preprare start group replication")
        cnx = None
        try:
            # 前面有对 TCP 做检查，所以执行到这里的时候 MySQL 定可以连接的上
            pwd = common.get_init_pwd()
            cnx = connector.connect(host='127.0.0.1',port=self.port,user='dbma',password=pwd)
            cursor = cnx.cursor()
            # 不管 primary 还是 seconder 都要配置凭证
            change_sql = f"change master to master_user='repluser',master_password='{pwd}' for channel 'group_replication_recovery';"
            logger.info(change_sql)
            cursor.execute(change_sql)
            if is_primary:
                # 添加 priamry 相关的逻辑
                mgr_sql = "set @@global.group_replication_bootstrap_group=ON;start group_replication;set @@global.group_replication_bootstrap_group=OFF;"
                cursor.execute(mgr_sql)
                logger.info(mgr_sql)
                logger.info("mysql group replication primary node config complete")
            else:
                # 如果不是 primary 结点而是 seconder 结点、那么要先 clone 
                mgr_sql = "start group_replication;"
                cursor.execute(mgr_sql)
                logger.info(mgr_sql)
                logger.info("mysql group replication seconder node config complete")
        except Exception as err:
            logger.error(f"exception occur during config mgr inner error {str(err)}")
        finally:
            if hasattr(cnx,'close'):
                cnx.close()

    @classmethod
    def from_members(cls,
                    port:int=3306,
                    pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",
                    max_mem:int=1024,
                    cores:int=_cores,
                    members:str="127.0.0.1,127.0.0.1,127.0.0.1",
                    dbma_basedir="/usr/local/dbm-agent/"):
        """
        """
        logger.info(f"build mgr with members {members}")
        logger.info(f"check members option is right or not")
        # 检验类型
        if type(members) != str:
            # 如果不是 str 类型那么直接报错
            raise TypeError("members must be a str type")
    
        # 检验是否包含“,”号
        if ',' not in members:
            raise ValueError('member must a comma seprate string')
    
        # 检验是否饱含 3 个以上 IP
        node_counts = len(members.split(','))
        if node_counts < 3:
            raise RuntimeError(f"node counts must greater or equal than 3 ,current is {node_counts}")

        # 把 member 的 IP 列表转换成集体
        ips = set()
        for ip in members.split(','):
            ips.add(ip)
        
        local_ips = common.get_all_local_ip()
        # 这个时候 mgr_ip 还是一个集体，不能直接使用
        # 求出当前主机应该使用的 local_address 和 group_seeds
        mgr_ip = ips & local_ips
        mgr_port = port * 10 + 1
        logger.info(f"mysql group replication use {mgr_port} for communicate")
        logger.info(f"mgr ip {mgr_ip}")
        if len(mgr_ip) == 0:
            raise ValueError("members do not contain local ip")
        elif len(mgr_ip) == 1:
            local_address = f"{mgr_ip.pop()}:{mgr_port}"
        else:
            raise ValueError(f"members recive a error value.{members}")
        logger.info(f"mysql group replication  local_address use {local_address}")

        group_seeds = ','.join([f"{ip}:{mgr_port}" for ip in members.split(',')])
        logger.info(f"mysql group replication  group_seeds use  {group_seeds}")
        # 返回一个安装器
        return cls(port=port,pkg=pkg,
                   dbma_basedir=dbma_basedir,max_mem=max_mem,
                   cores=cores,local_address=local_address,group_seeds=group_seeds)

            
    def install(self):
        """
        实现：
        1、执行安装前置操作
        2、渲染配置文件到 /etc/my-{port}.cnf
        3、init database
        4、执行安装后置操作
        """
        logger = self.logger.getChild('install')

        # 1
        try:
            self.pre_install()
        except Exception as err:
            # 如果检测中通过错误就停止
            logger.error(str(err))
            return
        # 2 & 3
        self.mysql_cnf_render.enable_mgr(self.local_address,self.group_seeds)
        self.mysql_cnf_render.render()
        self.init_database()
        # 4
        self.post_install()

        logger.info("install mgr node complete")


class MySQLUninstaller(object):
    """
    uninstall mysql
    1: delete user
    2: remove config files
    3: delete datadir
    """
    logger = logger.getChild('MySQLUninstaller')

    def __init__(self,port:int=3306):
        """
        """
        self.port =port

    def is_mysql_in_runing_state(self):
        # 如果端口有监听那就是 runing
        if checkings.is_port_in_use(ip='127.0.0.1',port=self.port):
            return True
        if checkings.is_file_exists(f'/tmp/mysql-{self.port}.pid'):
            return True

        return False

    def uninstall(self):
        logger = self.logger.getChild('uninstall')

        if self.is_mysql_in_runing_state():
            logger.error(f"mysql-{self.port} is runing can't uninstall 'systemctl stop mysqld-{self.port}' ")
            return 
        
        try:
            user_name = f'mysql{self.port}'
            config_file = f'/etc/my-{self.port}.cnf'
            systemctl_file = f'/usr/lib/systemd/system/mysqld-{self.port}.service'
            datadir = f'/database/mysql/data/{self.port}'

            logger.info(f"delete user mysql{self.port}")
            if checkings.is_user_exists(user_name):
                common.delete_user(f'mysql{self.port}')
            else:
                logger.warning(f"user {user_name} not exists")

            logger.info(f"remove mysql config file {config_file}")
            if checkings.is_file_exists(config_file):
                os.remove(config_file)
            else:
                logger.warning(f"config file {config_file} not exists")

            logger.info(f"remove systemctl config file {systemctl_file}")
            if checkings.is_file_exists(systemctl_file):
                os.remove(systemctl_file)
            else:
                logger.warning(f"systemctl config {systemctl_file} file not exists")
            
            logger.info(f'remove datadir {datadir}')
            if checkings.is_directory_exists(datadir):
                shutil.rmtree(f'/database/mysql/data/{self.port}')
            else:
                logger.warning(f"datadir {datadir} not exists")

        except errors.Error as err:
            logger.error(f"during uninstall mysql a error occur inner error : {str(err)}")


class MySQLShellInstaller(object):
    """
    实现 mysql-shell 的安装
    """
    logger = logger.getChild('MySQLShellInstaller')

    def __init__(self,pkg="mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz",dbma_basedir="/usr/local/dbm-agent/"):
        """
        """
        self.pkg = pkg
        self.dbma_basedir = dbma_basedir
        self.mysql_shell_base_dir = os.path.join('/usr/local/', self.pkg.replace('.tar.gz', '').replace('.tar.xz', ''))
        self.user = 'mysqlsh'
        self.pkg_full_path = os.path.join(self.dbma_basedir,'pkg',self.pkg)

    def pre_checkings(self):
        """
        完成安装前的检查工作
        1、安装包的版本号要满足要求(mysql-shell-8.0.xx)
        2、安装包要存在，或已经解压过
        """
        logger = self.logger.getChild('per_checkings')

        # 从 pkg 中抽取 mysql-shell 中的版本号
        logger.info("checking mysql-shell version")
        m = re.search(r'mysql-shell-8\.\d.\d\d-',self.pkg)
        if not m:
            
            # 给定的版本不满足正则的格式，不被支持
            logger.error(f"an not supported mysql-shell version {self.pkg}")
            raise errors.NotSupportedMySQLVersionError(self.pkg)

        # 检查文件是否已经存在
        logger.info(f"cheking file {self.pkg_full_path} exists or not")
        if not checkings.is_file_exists(self.pkg_full_path) and not checkings.is_directory_exists(self.mysql_shell_base_dir):

            # 安装安装包不存在，并且 /usr/local/ 下也不存在解压后的安装包的情况下，就报错
            raise errors.FileNotExistsError(self.pkg_full_path)

    def create_mysqlsh_user(self):
        """
        如果 mysqlsh 用户不存在就创建
        """
        logger = self.logger.getChild('create_mysqlsh_user')
        if not checkings.is_user_exists(self.user):
            logger.warning("prepare create mysqlsh user")
            common.create_user(self.user)
            return
        logger.info("mysqlsh user exists skip create it")

    def untar_pkg(self):
        """
        解压 mysql-shell.xxx..tar.gz 安装包到 /usr/local/
        """
        logger = self.logger.getChild('untar_pkg')

        # 检查安装包是否已经解压完成，如果没有就解压，如果已经解压就跳过
        mysql_shell_base_dir = os.path.join('/usr/local',self.pkg.replace('.tar.gz','').replace('.tar.xz',''))
        if checkings.is_directory_exists(mysql_shell_base_dir):
            logger.warning(f"directory {mysql_shell_base_dir} exists")
            return
        logger.info(f"prepare untar {self.pkg} to /usr/local/")
        shutil.unpack_archive(self.pkg_full_path, '/usr/local/')

    def change_owner(self):
        """
        调整目录的用户为 mysqlsh
        """
        logger = self.logger.getChild('change_owner')
        logger.info(f"change owner to {self.user}")
        common.recursive_change_owner(self.mysql_shell_base_dir, self.user)

    def export_path(self):
        """
        导出 path 环境变量到 /etc/profile 
        """
        logger = self.logger.getChild('export_path')

        #
        path = f"export PATH={self.mysql_shell_base_dir}/bin/:$PATH\n"
        with common.sudo('export path'):
            is_exported = False
            with open('/etc/profile', 'r') as f:
                for line in f:
                    if path in line:
                        is_exported = True
                        logger.info(f"{path} has been exported.")
                        break
                else:

                    # 在 for 循环没有执行 break 的情况下会执行 else 块
                    is_exported = False

            if is_exported == False:

                # 如果没有导出 path 变量就导出它
                logger.info("prepare export path variable ")
                with open('/etc/profile', 'a') as f:
                    f.write('\n')
                    f.write(path)

    def install(self):
        """
        安装 mysql-shell
        """
        logger = self.logger.getChild('install')

        try:
            self.pre_checkings()
        except errors.Error as err:
            logger.error(str(err))
            return

        # 第一步：创建用户
        self.create_mysqlsh_user()

        # 第二步：解压
        self.untar_pkg()

        # 第三步：修改文件属性
        self.change_owner()

        # 第四小：导出 path 环境变量
        self.export_path()

        logger.info(f"{self.pkg} install compelete")





        


        
    


