"""单独出一个模块用于软件安装
"""

import re
import os
import logging
import shutil
from . import privileges as prv
from . import errors


logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseSoftInstall(object):
    """所有软件安装的基类
    """
    logger = logger.getChild("BaseSoftInstall")

    pkgs_dir = "/usr/local/dbm-agent/pkg/"
    usr_local_dir = "/usr/local/"

    def __init__(self, pkg, *args, **kwargs):
        """
        """
        self.pkg = pkg
        self.profile = "/etc/profile"

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
        raise NotImplementedError("请在子类当中实现，导出 so 文件到 /etc/ld.so.conf.d 的逻辑")


class MySQLBinaryInstall(BaseSoftInstall):
    """实现用二进制包安装 MySQL 相关的工作
    """
    logger = logger.getChild("MySQLBinaryInstall")

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

        # 设定公共的属性
        BaseSoftInstall.__init__(self, pkg, *args, **kwargs)
        logger.info("complete")

    @property
    def path(self):
        return self.mysql_bin_dir

    @property
    def sopath(self):
        return self.mysql_lib_dir

    @property
    def is_has_been_installed(self):
        """之前是否就已经安装过了
        """
        return os.path.isdir(self.mysql_base_dir)

    def decompression(self):
        """解压安装包到 /usr/local/
        """
        logger = self.logger.getChild("decompression")
        logger.info("start")

        with prv.sudo("decompression mysql pkg to /usr/local/"):
            shutil.unpack_archive(self.pkg_full_path, self.usr_local_dir)

        logger.info("complete")

    
