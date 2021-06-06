"""
定义 dbm-agent 标准用户
"""
import pwd
import grp
from dbma.loggers.loggers import unix_logger
from dbma.unix.errors import UserNotExistsException,UserHasExistsException,GroupNotExistsException


logger = unix_logger.getChild("stdusers")


# 默认 dbm-agent 以 dbma 用户运行
linux_dbma_user = "dbma"
linux_dbma_group = "dbma"

# 所有的 MySQL 用户都在 mysql 组中
linux_mysql_group = "mysql"



class LinuxUserManager(object):
    """
    实现对 Linux 用户的管理
    """
    logger = logger.getChild("LinuxUserManager")

    @classmethod
    def is_user_exists(cls,linxu_user_name:str="dbma")->bool:
        """
        检查给定的 linux 用户是否存在.

        linxu_user_name
        ---------------
            str: linux 用户名

        Return:
        -------
            bool: 给定的用户存在就返回 True 不然返回 False.
        """
        logger = cls.logger.getChild("is_user_exists")

        try:
            pwd.getpwnam(linxu_user_name)
        except KeyError as err:
            logger.warning(f"linux user '{linxu_user_name}' not exists.")
            return False
        
        return True

    @classmethod
    def is_group_exists(cls,linux_group_name:str="dbma")->bool:
        """
        检查给定的用户组是否存在.

        linux_group_name
        ----------------
            str: linux 组名

        Return:
        ------
            bool: 给定的组名存在就返回 True ，不然就返回 False.
        """
        logger = cls.logger.getChild("is_group_exists")

        try:
            grp.getgrnam(linux_group_name)
        except KeyError as err:
            logger.warning(f"linux group '{linux_group_name}' not exists")
            return False

        return True

    @classmethod
    def get_uid(cls,linux_user_name:str="dbma"):
        """
        返回给定用户的 UID,当用户不存在时报 UserNotExistsException .

        linux_user_name
        ---------------
            str: linux 用户名

        Return
        ------
            int: uid

        Exceptions
        ----------
            UserNotExistsException
        """
        if cls.is_user_exists(linux_user_name) == False:
            raise UserNotExistsException(f"user '{linux_user_name}' Not exists.")

        # 能执行到这里说明用户存在，那就可以返回 UID 了
        _,_,uid,*_ = pwd.getpwnam(linux_user_name)
        return uid

    @classmethod
    def get_gid(cls,linux_group_name:str="dbma"):
        """
        返回给定用户组的组id(gid)，当用户组不存在的时候报 
        """
        if cls.is_group_exists(linux_group_name) == False:
            raise GroupNotExistsException(f"group '{linux_group_name}' not exists.")

        _,_,gid,*_ = grp.getgrnam(linux_group_name)
        return gid



LUM = LinuxUserManager

