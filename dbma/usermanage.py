"""实现 linux 操作系统中的用户管理
"""
import grp
import pwd
import logging
import subprocess

from . import privileges as prv

logger = logging.getLogger('dbm-agent').getChild(__name__)


class LinuxUsers(object):
    """
    """
    logger = logger.getChild("UserManage")

    @staticmethod
    def gid(group_name=''):
        """返回组的 gid，如果组不存在就返回 None

        :param group_name: A string.
        :return gid or None
        """
        lgr = logger.getChild("gid")
        lgr.info("start.")

        if LinuxUsers.is_group_exists(group_name) == True:
            # 组存在
            _, _, gid, _ = grp.getgrnam(group_name)
            lgr.debug(f"gid = {gid}")
            lgr.info("complete.")
            return gid
        else:
            lgr.debug("group not exists.")
            lgr.info("complete.")
            return None

    @staticmethod
    def uid(user_name=''):
        """返回用户的 uid ,如果用户不存在就返回 None.
        :param user_name: A string.
        :return A int.
        """
        lgr = logger.getChild("udi")
        lgr.info("start.")

        if LinuxUsers.is_user_exists(user_name) == True:
            # 用户存在
            _, _, uid, *_ = pwd.getpwnam(user_name)
            lgr.debug(f"uid = {uid}.")
            lgr.info("complete.")
            return uid
        else:
            lgr.debug(f"use not exists.")
            lgr.info("complete.")
            return None

    @staticmethod
    def uid_gid(user_name=""):
        """返回用户的 uid,和 gid ，如果用户不存在就返回 None,None
        :param user_name: A string.
        :return A int tuple
        """
        lgr = logger.getChild("uid_gid")
        lgr.info("start.")

        if LinuxUsers.is_user_exists(user_name):
            _, _, uid, gid, *_ = pwd.getpwnam(user_name)
            lgr.debug(f"uid = {uid} gid = {gid}")
            lgr.info("complete.")
            return (uid, gid)
        else:
            lgr.warning(f"user '{user_name}' not exists.")
            lgr.info("complete.")
            return (None, None)

    @staticmethod
    def create_group(group_name=''):
        """创建组

        :param group_name: A string.
        :return A bool.
        """
        lgr = logger.getChild("create_group")
        lgr.info("start")
        if LinuxUsers.is_group_exists(group_name) == False:
            # 如果用户组不存在就创建它
            try:
                with prv.sudo(f"create group '{group_name}' "):
                    p = subprocess.run(f"groupadd {group_name}", shell=True)
                    return p is not None
            except Exception as err:
                lgr.error("unexcepted Exception.")
                lgr.exception(err)
        else:
            lgr.info(f"group '{group_name}' already exists.")

        lgr.info("complete")
        return False

    @staticmethod
    def create_user(user_name, group_name=''):
        """创建用户

        :param user_name: A string.
        :param group_name: A stirng.
        """
        lgr = logger.getChild("create_user")
        lgr.info("start.")

        if group_name == '':
            # 如果组名没有指定，那么就直接使用用户名
            group_name = user_name
            lgr.debug(f"group_name is '' we set it to {user_name}.")

        if not LinuxUsers.is_group_exists(group_name):
            # 如果组还不存在就先创建组
            lgr.info(f"group '{group_name}' not exists we create it.")
            LinuxUsers.create_group(group_name)

        with prv.sudo(f"create user '{user_name}' ."):
            lgr.info(f"prepare create user '{user_name}'.")
            subprocess.run(f"useradd -g{group_name} {user_name}", shell=True)
            lgr.info(f"done create user.")

        logger.info("complete.")

    @staticmethod
    def is_user_exists(user_name=''):
        """检查给定的用户是否存在于当前的操作系统中

        :param user_name: A string.
        :return A bool.
        """
        lgr = logger.getChild("is_user_exists")
        lgr.info("start")

        try:
            pwd.getpwnam(user_name)
            lgr.info("complete")
            return True
        except KeyError as err:
            lgr.warning(f"user '{user_name}' not exists.")
        except Exception as err:
            lgr.warning("unexcepted exception.")
            lgr.exception(err)

        logger.info("complete.")
        return False

    @staticmethod
    def is_group_exists(group_name=''):
        """检查给定的用户组是否存在

        :param group_name: A string.
        :return A bool.
        """
        lgr = logger.getChild("is_group_exists")
        lgr.info("start")

        try:
            grp.getgrnam(group_name)
            lgr.info("complete")
            return True

        except KeyError as err:
            lgr.warning(f"group '{group_name}' not exists")
        except Exception as err:
            lgr.warning(f"unexcepted exception")
            lgr.exception(err)

        lgr.info("complete")
        return False

    @staticmethod
    def drop_user(user_name=''):
        """删除用户

        :param user_name: A string.
        :return A bool.
        """
        lgr = logger.getChild("drop_user")
        lgr.info("start.")

        if LinuxUsers.is_user_exists(user_name) == False:
            lgr.warning(f"user '{user_name}' not exists.")
            lgr.info("complete.")
            return True

        # 如果执行到这里说明，用户存在
        try:
            lgr.debug("prepare delete user.")
            with prv.sudo(f"delete user '{user_name}'."):
                subprocess.run(f"userdel -r {user_name}", shell=True)
            lgr.debug("done delete user.")
            lgr.info("complete.")
            return True
        except Exception as err:
            lgr.error("unexcepted Exception.")
            lgr.exception(err)
        return False

    @staticmethod
    def delete_user(user_name=''):
        return LinuxUsers.drop_user(user_name)

    @staticmethod
    def drop_group(group_name=''):
        """删除组

        :param group_user: A string.
        :return A bool.
        """
        lgr = logger.getChild("delete_group")
        lgr.info("start.")

        if LinuxUsers.is_group_exists(group_name) == False:
            # 组不存在
            lgr.debug("group not exists.")
            lgr.info("complete.")
            return True

        # 检查给定的组中还有没有用户
        gid = LinuxUsers.gid(group_name)
        gids = []
        for user in pwd.getpwall():
            gids.append(user.pw_gid)

        if gid in gids:
            lgr.error("has user in this group can't drop group.")
            lgr.info("complete.")
            return

        # 执行到这里说明组中已经没有了用户
        try:
            with prv.sudo("delete group."):
                subprocess.run(f"groupdel {group_name}", shell=True)
        except Exception as err:
            lgr.error("unexcepted Exception.")
            lgr.exception(err)
            return False

        lgr.info("complete.")
        return True

    @staticmethod
    def delete_group(group_name):
        return LinuxUsers.drop_group(group_name)
