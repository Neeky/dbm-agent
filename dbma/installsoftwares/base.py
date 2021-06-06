"""
实现 linux 系统上的软件包自动化安装与卸载。
"""

from dbma.loggers.loggers import install_logger

logger = install_logger.getChild("base")

class BaseInstall(object):
    """
    所有装包类的基类
    """
    logger = logger.getChild("BaseInstall")

    def install(self):
        """
        实现软件包的自动安装
        """
        raise NotImplementedError(f"this function not implemented 'BaseInstall.install' ")


class BinaryInstall(BaseInstall):
    """
    实现二进行包的安装
    """

    def __init__(self,linux_user_name="dbma",linux_user_group="dbma"):
        """
        linux_user_name
        ---------------
            str: 守护进程的用户名

        linux_user_group
        ----------------
            str: 守护进程用户的属组

        
        """
        self._linux_user_name = linux_user_name
        self._linux_user_group = linux_user_group

    def create_linux_user(self):
        """
        """
        pass

        





