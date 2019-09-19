  
# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import shutil
import logging
import pathlib
import subprocess
import configparser
from . import errors
from . import common
from . import checkings
from . import configrender
from . import gather
logger = logging.getLogger('dbm-agent').getChild(__name__)

# 读取配置文件
#parser = configparser.ConfigParser()
#parser.read("/usr/local/dbm-agent/etc/dbma.cnf")
#dbma_basedir = parser['dbma']['base_dir']   # /usr/local/dbm-agent/
#template_dir = os.path.join(dbma_basedir,'etc/templates/') # /usr/local/dbm-agent/etc/templates/
#pkg_dir = os.path.join(dbma_basedir,'pkg') # /usr/local/dbm-agent/pkg/
#default_pkg = "mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz" # mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz

_cores = gather.cpu_cores().counts

class MySQLInstaller(object):
    """
    完成单实例架构下 MySQL 实例的自动化安装
    """
    def pre_checkings(self):
        """
        完成安装 MySQL 之前的必要检查
        :errors.UserAlreadyExistsError
        :errors.FileAlreadyExistsError
        :errors.DirecotryAlreadyExistsErrror
        """
        port = self.port
        pkg = self.pkg
        pkg_full_path = os.path.join('/usr/local/dbm-agent/pkg/',pkg)
        basedir_full_path = os.path.join('/usr/local/',self.version)

        # 检查安装包是不是存在并且之前也从来没有安装过
        logger.info(f"check package '{pkg_full_path}' is exists")
        if not checkings.is_file_exists(pkg_full_path)   and   not checkings.is_directory_exists(basedir_full_path):
            raise errors.FileNotExistsError(pkg_full_path)

        logger.info(f"check port {port} is in use or not")
        # 检查用户是否存在
        if checkings.is_user_exists(f"mysql{port}"):
            raise errors.UserAlreadyExistsError(f'user mysql{port} already exists')

        # 检查配置文件是否存在
        logger.info(f"check config file  /etc/my-{port}.cnf ")
        if checkings.is_file_exists(f"/etc/my-{port}.cnf"):
            raise errors.FileAlreadyExistsError(f"config file '/etc/my-{port}.cnf' already exists")

        # 检查 datadir 是否存在
        logger.info(f"check datadir /database/mysql/data/{port}")
        if checkings.is_directory_exists(f"/database/mysql/data/{port}"):
            raise errors.DirecotryAlreadyExistsErrror(f"directory  /database/mysql/data/{port} alread exists")

        # 检查版本号是否被支持
        logger.info(f"check mysql version {pkg}")
        if not checkings.is_an_supported_mysql_version(pkg=pkg):
            raise errors.NotSupportedMySQLVersionError(pkg)

        if not checkings.is_file_exists(self.init_file):
            raise errors.FileNotExistsError(self.init_file)

    def __init__(self,port:int=3306,pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",
                 dbma_basedir='/usr/local/dbm-agent/',
                 max_mem:int=1024,cores=_cores):
        self.port = port
        self.dbma_basedir = dbma_basedir
        self.pkg = pkg
        self.max_mem = max_mem
        self.cores = cores
        self.version = pkg.replace('.tar.gz','').replace('.tar.xz','')
        self.init_file = '/usr/local/dbm-agent/etc/templates/init-users.sql'
        logger.info(f"install mysql instance with this mysql version {self.pkg} port {self.port} max_mem {self.max_mem} MB cores = {cores}")


    def create_datadir(self):
        """
        创建数据目录
        :errors.DirecotryAlreadyExistsErrror
        """
        # 双重检测
        logger.info(f"create datadir /database/mysql/data/{self.port}")
        if checkings.is_directory_exists(f"/database/mysql/data/{self.port}"):
            raise errors.DirecotryAlreadyExistsErrror(f"directory  '/database/mysql/data/{self.port}' alread exists")

        datadir = pathlib.Path(f'/database/mysql/data/{self.port}')
        datadir.mkdir(parents=True)
        
        #os.mkdir(f'/database/mysql/data/{self.port}')

    def unarchive_pkg(self):
        """
        """
        logger.info("unarchive mysql pkg to /usr/local/")
        if checkings.is_directory_exists(os.path.join('/usr/local/',self.version)):
            logger.warning(f"{os.path.join('/usr/local/',self.version)} exists mysql may has been installed. skip untar {self.pkg} to /usr/local/")
            return
        
        if not checkings.is_an_supported_mysql_version(pkg=self.pkg):
            raise errors.NotSupportedMySQLVersionError(f'not a supported mysql version "{self.pkg}" ' )

        pkg_full_path = os.path.join(self.dbma_basedir,'pkg',self.pkg)

        if not checkings.is_file_exists(pkg_full_path):
            raise errors.FileNotExistsError(f'{pkg_full_path}')

        with common.sudo("unarchive mysql install pkg"):
            shutil.unpack_archive(pkg_full_path,'/usr/local/')
            common.recursive_change_owner(os.path.join('/usr/local/',self.version),user="root",group="mysql")

    def init_database(self):
        """
        完成数据库 init
        """
        logger.info("init database with --initialize-insecure")
        with common.sudo("init database"):
            args = [f'/usr/local/{self.version}/bin/mysqld',f'--defaults-file=/etc/my-{self.port}.cnf',
                            '--initialize-insecure',f'--user=mysql{self.port}',f'--init-file={self.init_file}']
            logger.warning(args)
            subprocess.run(args,capture_output=True)

    def config_systemd(self):
        """
        """
        logger.info(f"config service(systemd) and daemon-reload")
        systemd = configrender.MySQLSystemdRender(pkg=self.pkg,port=self.port)
        systemd.render()
        with common.sudo(f"systemctl daemon reload"):
            subprocess.run(['systemctl daemon-reload'],shell=True)

    def start_mysql(self):
        """
        """
        logger.info(f"start mysqld-{self.port} by systemctl start mysqld-{self.port}")
        with common.sudo(f"start mysql server {self.port}"):
            subprocess.run(f"systemctl start mysqld-{self.port}",shell=True)

    def config_path(self):
        """
        配置 PATH 环境变量
        """
        logger.info(f"config path env variable /usr/local/{self.version}/bin/")
        common.config_path(path=f"/usr/local/{self.version}/bin/",user_name=f"mysql{self.port}")

    def enable_service(self):
        """
        配置 数据库开机启动
        """
        logger.info(f"config mysql auto start on boot")
        common.enable_service(f"mysqld-{self.port}")
    
    def config_so(self):
        """
        配置 so
        """
        logger.info(f"export so file")
        common.config_mysql_so(self.version)

    def config_include(self):
        """
        配置 头文件
        """
        logger.info(f"export header file")
        common.config_mysql_include(self.version)

    def install(self):
        try:
            # 如果必要条件检查不成功就直接退出
            self.pre_checkings()
        except errors.Error as err:
            logger.error(f"riase a exception during install mysql inner error is {str(err)}")
            return None
        
        # 如果前置的检查都通过了那么开始创建用户
        common.create_user(f"mysql{self.port}")

        # 创建数据目录
        self.create_datadir()

        # 解压安装包
        self.unarchive_pkg()

        # 渲染配置文件
        render = configrender.MysqlRender(pkg=self.pkg,port=self.port,max_mem=self.max_mem,cores=self.cores)
        render.render()
        
        # 初始化数据目录
        self.init_database()

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

            
class MySQLSingleInstaller(MySQLInstaller):
    pass


class MySQLMGRInstaller(MySQLInstaller):
    pass


class MySQLUninstaller(object):
    """
    uninstall mysql
    1: delete user
    2: remove config files
    3: delete datadir
    """

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





