"""支持两种主流备份工具的自动化安装
"""

import re
import os
import psutil
import shutil
import logging

from . import errors

logger = logging.getLogger('dbm-agent').getChild(__name__)


class BaseInstall(object):
    """
    """
    logger = logger.getChild("BaseInstall")

    def __init__(self, pkg=None):
        self.pkg = pkg

    def pre_checks(self):
        """执行安装前的一些检查工作
        """
        logger = self.logger.getChild("pre_checks")

        if self.pkg is None:
            logger.warn(f"pkg is None,can not execute installing program")
            raise ValueError("self.pkg is None")

        # 能执行到这里说明 self.pkg 已经不是 None了、下面查看指定的包是否存在
        pkg_abs_path = os.path.join("/usr/local/dbm-agent/pkg", self.pkg)
        if not os.path.isfile(pkg_abs_path):
            logger.warn(f"{pkg_abs_path} not exists.")
            raise errors.FileNotExistsError(pkg_abs_path)

        logger.info(f"{pkg_abs_path} looking good")

    @property
    def pkg_abs_path(self):
        """返回备份工具的全路径
        """
        if self.pkg is None:
            return None

        abs_path = os.path.join("/usr/local/dbm-agent/pkg", self.pkg)
        if os.path.isfile(abs_path):
            return abs_path

        return None

    @property
    def pkg_base_dir(self):
        """返回 pkg 解压后的根目录
        """
        raise NotImplementedError("please implement it in subclass")

    def extract_pkg(self):
        """解压备份工具到 /usr/local/
        """
        logger = self.logger.getChild("extract_pkg")

        if os.path.isdir(self.pkg_base_dir):
            logger.info(f"{self.pkg_base_dir} exists")
            return

        # 目录不存在就解压
        shutil.unpack_archive(self.pkg_abs_path, "/usr/local/")

    def export_path(self):
        """导出 PATH 环境变量
        """
        logger = self.logger.getChild("export_path")
        has_exported = False
        export_cmd = f"export PATH={self.pkg_base_dir}/bin/:$PATH\n"
        with open("/etc/profile") as f:
            for line in f:
                if export_cmd in line:
                    has_exported = True
                    break

        if has_exported == True:
            logger.info("PATH has been exported")
            return

        # 导出环境变量
        with open("/etc/profile", 'a') as f:
            f.write(f"export PATH={self.pkg_base_dir}/bin/:$PATH\n")

    def install(self):
        """
        """
        logger = self.logger.getChild("install")

        try:
            self.pre_checks()
        except Exception as err:
            logger.info(f"install {self.pkg} fail becuase {err}")
            return

        # 执行到这里说明就可以安装了
        self.extract_pkg()
        self.export_path()

        logger.info("install complete")


class MySQLBackupInstall(BaseInstall):
    """
    """

    logger = logger.getChild("MySQLBackupInstall")

    def __init__(self, pkg="mysql-commercial-backup-8.0.19-linux-glibc2.12-x86_64.tar.xz"):
        logger = self.logger.getChild("__init__")

        BaseInstall.__init__(self, pkg)
        logger.info(f"using {self.pkg}")

        self.pkg_pattern = r"mysql-commercial-backup-8.0.\d{1,2}-linux-glibc2.12-x86_64.tar.xz"

    def pre_checks(self):
        """
        """
        logger = self.logger.getChild("pre_checks")
        try:
            if not re.match(self.pkg_pattern, self.pkg):

                # 如果匹配不了给定的模式串，说明这个不是一个官方的包，直接报错
                logger.warn(
                    f"{self.pkg} not a official package,we only support official package")
                raise errors.NotSupportedPackageError()

            # 调用父类的检操作
            BaseInstall.pre_checks(self)

        except Exception as err:
            raise err

    @property
    def pkg_base_dir(self):
        """
        """
        dirname = self.pkg.replace('.tar.gz', '').replace('.tar.xz', '')
        return os.path.join("/usr/local/", dirname)


class XtraBackupInstall(BaseInstall):
    """
    """
    logger = logger.getChild("MySQLBackupInstall")

    def __init__(self, pkg="percona-xtrabackup-8.0.9-Linux-x86_64.libgcrypt153.tar.gz"):
        """
        """
        logger = self.logger.getChild("__init__")
        BaseInstall.__init__(self, pkg)

        self.pkg_pattern = r"percona-xtrabackup-8.0.\d{1,2}-Linux-x86_64.libgcrypt\d{1,4}.tar.gz"
        logger.info(f"using {self.pkg}")

    def pre_checks(self):
        """
        """
        logger = self.logger.getChild("pre_checks")
        try:
            if not re.match(self.pkg_pattern, self.pkg):

                # 不匹配
                logger.warn(
                    f"{self.pkg} not a official package,we only support official package")
                raise errors.NotSupportedPackageError()

            # 调用父类的检操作
            BaseInstall.pre_checks(self)

        except Exception as err:
            raise err

    @property
    def pkg_base_dir(self):
        """
        """
        ptn = r"percona-xtrabackup-8.0.\d{1,3}-Linux-x86_64"
        if re.match(ptn, self.pkg):
            dirname = re.match(ptn, self.pkg).group()
            return os.path.join("/usr/local/", f"{dirname}")

    def extract_pkg(self):
        BaseInstall.extract_pkg(self)

        # 如果连接文件存在，那么就删除它并且重新建设
        if os.path.islink("/usr/local/percona-xtrabackup"):
            os.remove("/usr/local/percona-xtrabackup")

        os.symlink(self.pkg_base_dir, "/usr/local/percona-xtrabackup")
