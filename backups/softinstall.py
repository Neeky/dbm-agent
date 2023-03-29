"""单独出一个模块用于软件安装
"""

import re
import os
import logging
import shutil
from . import privileges as prv
from . import errors
from .usermanage import LinuxUsers as lus
from .ldconfig import ldconfig
from .dbmaconfig import ConfigMixin


logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseSoftInstall(ConfigMixin):
    """所有软件安装的基类
    """
    logger = logger.getChild("BaseSoftInstall")
    group_name = "dbma"
    user_name = "dbma"

    pkgs_dir = "/usr/local/dbm-agent/pkg/"
    usr_local_dir = "/usr/local/"
    ld_so_dir = "/etc/ld.so.conf.d"

    def __init__(self, pkg, *args, **kwargs):
        """
        """
        self.pkg = pkg
        self.profile = "/etc/profile"
        self.version = pkg.replace('.tar.gz', '').replace('.tar.xz', '')
        self.pkg_full_path = os.path.join(self.usr_local_dir, self.pkgs_dir)

    @property
    def path(self):
        raise NotImplementedError("请在子类当中实现，返回 PATH 路径的功能")

    @property
    def sopath(self):
        """返回库文件的路径
        """
        raise NotImplementedError("请在子类当中实现，返回库文件路径的功能")

    def export_path(self):
        """导出 PATH 环境变量到 /etc/profile
        """
        logger = self.logger.getChild("export_path")
        logger.info("start")

        # 取出要导出的路径
        # 拼接出 export PATH 语句
        path = self.path
        export_path_str = f"export PATH={path}:$PATH\n"

        is_end_with_new_line = False
        with prv.sudo("export PATH env"):

            # 检查 /etc/profile 是不是以 \n 结尾
            with open(self.profile) as profile_obj:
                content = profile_obj.read()
            is_end_with_new_line = content.endswith('\n')
            is_has_been_exported = export_path_str in content

            if is_has_been_exported:
                # 如果已经导出过了，就不再导出
                logger.info(
                    f"'{path}' has been exported, we well skip this trip.")

                logger.info("complete")
                return

            # 如果文件以最后有换行符，那么就直接往反而追回，如果没有就先写一个换行。
            with open(self.profile, 'a') as profile_obj:
                if is_end_with_new_line == True:
                    # 有换行
                    logger.debug(f"file {self.profile} ends with new-line")
                else:
                    # 没有换行就先写一个换行进去
                    logger.debug(f"file {self.profile} not ends with new-line")
                    profile_obj.write("\n")
                profile_obj.write(export_path_str)

        logger.info("complete")

    def export_sofile(self):
        """导出库文件到 /etc/ld.so.conf.d
        """
        logger = self.logger.getChild("export_sofile")
        logger.info("start.")

        so_lib_full_path, version = self.sopath
        with prv.sudo("export os file"):
            so_export_file = os.path.join(self.ld_so_dir, f"{version}.conf")
            with open(so_export_file, 'w') as soconfig_obj:
                soconfig_obj.write(so_lib_full_path)

        # 导出
        ldconfig()
        logger.info("complete.")

    def pre_checks(self):
        """安装前要执行的检查
        """
        # 默认什么都不检查
        pass

    def create_user(self):
        """创建用户和组
        """
        logger = self.logger.getChild("create_user")
        logger.info("start")

        if lus.is_group_exists(self.group_name) == False:
            logger.debug(f"create group '{self.group_name}'")
            lus.create_group(self.group_name)

        if lus.is_user_exists(self.user_name) == False:
            logger.debug(f"create group '{self.user_name}'")
            lus.create_user(self.user_name, self.group_name)

        logger.info("complete")

    def is_pkg_exists(self):
        """检查包是不否存在
        """
        logger = self.logger.getChild("is_pkg_exists")
        logger.info("start.")

        # 检查文件是否存在
        is_exists = os.path.isfile(os.path.join(self.pkgs_dir, self.pkg))
        if is_exists == False:
            logger.warning(f"pkg '{self.pkg}' not exists.")

        logger.info("complete.")
        return is_exists

    def is_has_been_installed(self):
        """
        """
        return os.path.isdir(self.usr_local_dir, self.version)

    def decompression(self):
        """解压安装包到 /usr/local/
        """
        logger = self.logger.getChild("decompression")
        logger.info("start")

        with prv.sudo("decompression mysql pkg to /usr/local/"):
            shutil.unpack_archive(self.pkg_full_path, self.usr_local_dir)

        logger.info("complete")

    def install(self):
        pass


class MySQLBinaryInstall(BaseSoftInstall):
    """实现用二进制包安装 MySQL 相关的工作
    """
    logger = logger.getChild("MySQLBinaryInstall")
    group_name = "mysql"
    user_name = "mysql"
    mysql_57_re = r"mysql-.*5\.7\.\d*-linux-glibc2.12-x86_64"
    mysql_80_re = r"mysql-.*8\.0\.\d*-linux-glibc2.12-x86_64"

    def __init__(self, pkg="mysql-8.0.19-linux-glibc2.12-x86_64.tar.xz", *args, **kwargs):
        """
        """
        logger = self.logger.getChild("__init__")
        logger.info("start")

        # 初始化由 pkg 参数就能设定的变量

        # 版本号:mysql-8.0.19-linux-glibc2.12-x86_64
        version, *_ = pkg.split('.tar')

        # 安装包的全路径 /usr/local/dbm-agent/pkg/mysql-8.0.19-linux-glibc2.12-x86_64.tar.xz
        pkg_full_path = os.path.join(self.pkgs_dir, pkg)

        # 其它路径
        mysql_base_dir = os.path.join(self.usr_local_dir, version)
        mysql_bin_dir = os.path.join(mysql_base_dir, 'bin')
        mysql_lib_dir = os.path.join(mysql_base_dir, 'lib')

        # 设定 MySQL 相关的属性
        self.pkg_full_path = pkg_full_path
        self.mysql_base_dir = mysql_base_dir
        self.mysql_lib_dir = mysql_lib_dir
        self.mysql_bin_dir = mysql_bin_dir
        self.mysql_version = version

        # 设定公共的属性
        BaseSoftInstall.__init__(self, pkg, *args, **kwargs)
        logger.info("complete")

    @property
    def path(self):
        return self.mysql_bin_dir

    @property
    def sopath(self):
        return (self.mysql_lib_dir, self.mysql_version)

    @property
    def is_has_been_installed(self):
        """之前是否就已经安装过了
        """
        return os.path.isdir(self.mysql_base_dir)

    @property
    def is_an_supported_mysql_version(self):
        """
        """
        return re.search(self.mysql_57_re, self.mysql_version) or re.search(self.mysql_80_re, self.mysql_version)

    def pre_checks(self):
        """
        """
        # 要满足父类的要求
        BaseSoftInstall.pre_checks(self)

    def install_mysql(self):
        """实现 MySQL 的自动化安装
        """
        logger = self.logger.getChild("install_mysql")
        logger.info("start")

        if self.is_an_supported_mysql_version:
            # 如果是一个不支持的 MySQL 版本就直接报错
            raise errors.NotSupportedMySQLVersionError(self.mysql_version)

        if self.is_has_been_installed:
            # 如果已经安装过了那么就直接退出。
            logger.info("has been installed")
            return
        # 如果执行到这里说明，当前版本的 MySQL 还没有安装过。

        # 第一步 检查 mysql 用户是否存在，不存在就创建
        self.create_user()

        # 第二步 检查包是否存在
        logger.info("step 1 check pkg exists or not.")
        if self.is_pkg_exists == False:
            logger.error(f"pkg file not exists '{self.pkg}'.")
            raise errors.FileNotExistsError(self.pkg_full_path)

        # 第三步 解压
        logger.info("step 2 decompression.")
        self.decompression()

        # 第四步 导出 PATH 环境变量
        logger.info("setp 3 export path.")
        self.export_path()

        # 第五步 导出 os 文件
        logger.info('step 4 export so file.')
        self.export_sofile()

        # 第六步 chown
        logger.info(f"step 5 chwon {self.mysql_base_dir}")
        prv.chown(self.mysql_version, self.user_name,
                  self.group_name, recusive=True)

    def install(self):
        """实现软件包的安装
        """
        logger = self.logger.getChild("install")
        logger.info("start.")

        try:
            self.install_mysql()
            logger.info("mysql install successful.")
        except errors.Error as err:
            logger.error("mysql install fail.")
            logger.exception(err)
        except Exception as err:
            logger.error("unexcepted Exception.")
            logger.exception(err)

        logger.info("complete.")


class PrometheusBinaryInstall(BaseSoftInstall):
    """prometheus 二进制包安装
    """
    logger = logger.getChild("PrometheusBinaryInstall")
    prometheus_re = r"prometheus-2.\d+.\d+.linux-amd64.tar.gz"
    user_name = "prometheus"
    group_name = "prometheus"

    def __init__(self, pkg="prometheus-2.17.2.linux-amd64.tar.gz", *args, **kwargs):
        """
        """
        logger = self.logger.getChild("__init__")
        logger.info("start.")

        self.pkg = pkg
        self.version = pkg.replace('.tar.gz', '').replace('.tar.xz', '')
        self.pkg_full_path = os.path.join(self.pkgs_dir, self.version)

        logger.info("complete.")

    @property
    def path(self):
        """
        """
        return os.path.join(self.usr_local_dir, self.version)

    def export_sofile(self):
        """没有 so 要导出
        """
        pass

    @property
    def is_pkg_exists(self):
        """检查软件包是否存在
        """
        return os.path.isfile(self.pkg_full_path)

    @property
    def is_has_been_installed(self):
        return os.path.isdir(self.usr_local_dir, self.version)

    def install_prometheus(self):
        """
        """
        logger = self.logger.getChild("install_prometheus")
        logger.info("start.")

        if self.is_has_been_installed is True:
            # 如果已经安装过了就直接退出
            logger.info(f"'{self.version}' has been installd.")
            logger.info("complete.")
            return

        # 执行到这里说明之前还没有安装过
        if self.is_pkg_exists is False:
            logger.error(f"pkg '{self.pkg_full_path}' not exists.")
            raise errors.FileNotExistsError(self.pkg_full_path)

        # 执行常规的安装程序

        # 第一步：创建用户
        self.create_user()

        # 第二步：解压
        self.decompression()

        # 第三步：
