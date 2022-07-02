"""
实现 linux 系统上的软件包自动化安装与卸载。
"""

from dbma.loggers.loggers import get_logger
from dbma.bil.osuser import is_user_exists, is_group_exists
logger = get_logger(__file__)

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
    logger = logger.getChild("BinaryInstall")

    def __init__(self,linux_user_name="dbma", linux_user_group="dbma", pkg=None ):
        """
        Parameters:
        -----------
        linux_user_name: str 
            守护进程的用户名

        linux_user_group: str
            守护进程用户的属组

        pkg: str
            安装包的名称
        
        """
        self._linux_user_name = linux_user_name
        self._linux_user_group = linux_user_group
        self._pkg = pkg

    def create_linux_user(self):
        """
        检查给定的用户是否存在、不存在就创建
        """
        if is_user_exists(self._linux_user_name) == False:
            # Todo
            pass

        





