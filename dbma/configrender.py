"""
读取模板并渲染
"""
# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/> 
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import copy
import logging
from jinja2 import Environment,FileSystemLoader
from . import errors
from . import checkings
from . import common

logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseRender(object):
    """
    所有配置文件渲染功能的基类
    """
    def __init__(self,tmpl_dir:str="/usr/local/dbm-agent/etc/templates/",
                      tmpl_file:str="mysql-8.0.17.cnf.jinja"):
        logger.info(f"load template from {tmpl_dir}")
        logger.info(f"template file name {tmpl_file}")
        if not checkings.is_directory_exists(tmpl_dir):
            logger.warning(f"directory {tmpl_dir} not exists")
            raise errors.DirectoryNotExistsError(f"{tmpl_dir}")

        if not checkings.is_file_exists(os.path.join(tmpl_dir,tmpl_file)):
            logger.warning(f"template file {tmpl_file} not exists")
            raise errors.FileNotExistsError(f"{os.path.join(tmpl_dir,tmpl_file)}")

        env = Environment(loader=FileSystemLoader(searchpath=tmpl_dir))
        tmpl = env.get_template(tmpl_file)

        self.tmpl = tmpl

    def render(self)->str:
        raise NotImplementedError()


class MysqlRender(BaseRender):
    """
    """
    defaults = {
        # basic
        'user': None,
        'port': None,
        'basedir': None,
        'datadir': None,
        'socket': None,
        'pid': None,
    }

    def __init__(self,pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",port:int=3306,max_mem:int=1024,
                 tmpl_dir:str="/usr/local/dbm-agent/etc/templates/",tmpl_file="mysql-8.0.17.cnf.jinja"):
        super().__init__(tmpl_dir=tmpl_dir,tmpl_file=tmpl_file)

        #
        logger.info(f"mysql pkg {pkg} max memory {max_mem}")
        self.defaults = copy.deepcopy(MysqlRender.defaults)
        self.pkg = pkg
        self.max_mem = max_mem

        # basic
        self.user = f"mysql{port}"
        self.port = port
        self.basedir = os.path.join('/usr/local/',pkg.replace('.tar.gz','').replace('.tar.xz',''))
        self.datadir = os.path.join(f'/database/mysql/data/{port}')
        self.socket = f"/tmp/mysql-{port}.sock"
        self.mysqlx_socket = f"tmp/mysqlx-{port}.sock"
        self.pid_file = f"/tmp/mysql-{port}.pid"

        self.defaults.update({
            'user': self.user,
            'port': self.port,
            'basedir': self.basedir,
            'datadir': self.datadir,
            'socket': self.socket,
            'mysqlx_socket': self.mysqlx_socket,
            'pid_file': self.pid_file,
        })


    def _config_cpu(self):
        """
        """
        logger.info("config cpu options")
        pass

    def _config_disk(self):
        """
        """
        logger.info("config disk options")
        pass

    def _config_mem(self):
        """
        """
        logger.info("config memory options")
        pass

    def config_all(self):
        """
        完成 cpu mem disk 相关的配置
        """
        self._config_cpu()
        self._config_mem()
        self._config_disk()

    def render(self):
        self.config_all()
        self.tmpl.globals = self.defaults
        logger.info("going to render config file")
        with common.sudo(f"render config file /etc/my-{self.port}.cnf"):
            with open(f"/etc/my-{self.port}.cnf",'w') as cnf:
                cnf.write(self.tmpl.render())


class ZabbixRender(BaseRender):
    """
    """
    pass


class MySQLSystemdRender(BaseRender):
    """
    """
    def __init__(self,tmpl_dir:str="/usr/local/dbm-agent/etc/templates/",
                      tmpl_file:str="mysqld.service.jinja",
                      pkg:str="mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz",port:int=3306):
        super().__init__(tmpl_dir,tmpl_file)
        self.version = pkg.replace('.tar.gz','').replace('.tar.xz','')
        self.basedir = os.path.join('/usr/local/',self.version)
        self.port = port

        self.defaults = {
            'basedir': self.basedir,
            'port': self.port,
            'user': f'mysql{self.port}',
        }

        self.tmpl.globals = self.defaults

    def render(self):
        """
        """
        with common.sudo(f"render mysql systemd config file port = {self.port}"):
            cnf = self.tmpl.render()
            with open(f'/usr/lib/systemd/system/mysqld-{self.port}.service','w') as cnf_dst:
                cnf_dst.write(cnf)












































