# -*- encoding: utf8 -*-
"""
实现 linux 系统上的软件包自动化安装与卸载。
"""

from dbma.bil import fs
from dbma.bil import sudos
from dbma.loggers.loggers import get_logger
from dbma.bil.osuser import RootUser
from dbma.installsoftwares.exceptions import PkgNotExistsException


logger = get_logger(__file__)


class BaseInstall(object):
    """
    所有装包类的基类
    """
    logger = logger.getChild("BaseInstall")    # 日志对象
    pkg_repo_dir = "/usr/local/dbm-agent/pkg/" # 安装包要保存的目录
    install_dir = "/usr/local/"                # 安装目录
    pkg = None                                 # 安装包的名字
    user = RootUser()                          # 程序的运行用户
    target_link = None                         # 安装后要创建的目标链接名

    @classmethod
    def export_env(cls, name, value):
        """
        配置环境变量
        Parameters:
        ----------
        bin_path: str
            PATH 环境变量值要新加的前缀

        Returns:
            None
        """
        cls_logger = cls.logger.getChild("export_env")
        # 如果是 PATH 就是追加，其它的情况都是一个 name 一个值
        if name == "PATH":
            line = f"export {name}={value}:${name}"
        else:
            line = f"export {name}={value}"

        # 检查有没有配置，如果没有就添加
        if fs.is_line_in_etc_profile(line) == False:
            cls_logger.info(f"export env {line}")
            fs.append_new_line_to_etc_profile(line)
    
    @classmethod
    def pkgs(cls):
        """
        返回 /usr/local/dbm-agent/pkg/ 目录下的安装包名
        """
        cls_logger = cls.logger.getChild("pkgs")
        cls_logger.info("start")

        if not fs.is_file_exists(cls.pkg_repo_dir):
            return []
        return [_ for _ in fs.listdir(cls.pkg_repo_dir)]

    @classmethod
    def is_installed(cls):
        """
        判断软件是否已经安装(不管版本号是多少，只要安装了就返回 True)
        """
        if cls.target_link is None:
            return False
        return fs.is_file_exists(cls.target_link)

    @classmethod
    def current_installed_version(cls):
        """
        """
        return fs.readlink(cls.target_link) if cls.is_installed() else ''

    def is_pkg_exists(self):
        """
        检查安装包是否存在

        Returns:
        -------
            bool
        """
        logger = self.logger.getChild("is_pkg_exists")
        logger.info(f"start pkg = '{self.pkg}' ")

        return self.pkg in self.__class__.pkgs()

    def extract_pkg(self):
        """
        解压安装包
        """
        # 把安装包(/usr/local/dbm-agent/pkg/xxx.yyy)   解压到 安装目录(/usr/local/)
        fs.extract_tar_file(fs.join(self.pkg_repo_dir, self.pkg), self.install_dir)

    def exports(self):
        """
        导出软件安装后需要的环境变量
        """
        raise NotImplementedError("this function not implemented 'BaseInstall.exports'")

    def create_user(self):
        """
        创建用户(user.create 当用户存在的时候就不会创建)
        """
        logger = self.logger.getChild("create_user")
        logger.info(f"going to create user {str(self.user)} .")

        # 创建用户
        self.user.create()

        logger.info(f"done .")

    def chown(self):
        """
        修改文件的所有者与组
        """
        raise NotImplementedError("this function not implemented 'BaseInstall.chown'")

    def make_link(self):
        """
        创建链接
        """
        raise NotImplementedError("this function not implemented 'BaseInstall.make_link'")

    def install(self):
        """
        实现软件包的自动安装
        """
        raise NotImplementedError("this function not implemented 'BaseInstall.install'")

    def config(self):
        """
        """
        raise NotImplementedError("this function not implemented 'BaseInstall.install'")
    
    def start(self):
        """
        """
        raise NotImplementedError("this function not implemented 'BaseInstall.install'")



class TarballInstall(BaseInstall):
    """
    源码安装方式的基类
    """
    pass


class BinaryInstall(BaseInstall):
    """
    实现二进行包的安装
    """
    target_link = None

    logger = logger.getChild("BinaryInstall")

    def __init__(self, pkg=None ):
        """
        Parameters:
        -----------
        pkg: str
            安装包的名称
        
        """
        self.pkg = pkg

    def get_src_dir_name(self):
        """
        一旦把 pkg 解压到 /usr/local/ 目录后就会得到一个新的目录，如果真要解压完成之后再去查这个目录名，这样做会比较麻烦。
        我们可以通过 tarfile 的 api 直接得到目录名

        Returns:
        --------
            str
                '' 没有安装包的时候
                '安装包名' 有安装包的时候
        """
        logger = self.logger.getChild("get_src_dir_name")
        logger.info("start .")

        if fs.is_file_exists(fs.join(self.pkg_repo_dir, self.pkg)):
            return fs.get_tar_file_name(fs.join(self.pkg_repo_dir, self.pkg))
        logger.info(f"pkg not exists {self.pkg}")
        return ''

    def chown(self):
        """
        把解压后的目录，和链接文件都配置上
        """
        self.user.chown(fs.join(self.install_dir, self.get_src_dir_name()))
        self.user.chown(self.target_link)

    def make_link(self):
        fs.link(fs.join(self.install_dir, self.get_src_dir_name()), self.target_link)

    def install(self):
        """
        二进制包的安装流程

        Exceptions:
        ----------
            PkgNotExistsException
        """
        with sudos.sudo():
            is_exists = self.is_pkg_exists()
            if not is_exists:
                raise PkgNotExistsException(f"pkg {self.pkg} not exists in /usr/local/dbm-agent/pkg/ ")
            self.create_user()
            self.extract_pkg()
            self.make_link()
            self.chown()
            self.exports()
        # 为了后面直接点下去, 比如 install 了之后还有可能要 config, start 这类的
        return self
