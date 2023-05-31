# -*- coding: utf8 -*-

"""
测试 osuser.py 模块
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from collections import namedtuple

from dbma.bil.osuser import (
    is_root,
    is_user_exists,
    is_group_exists,
    get_uid_gid,
    Identify,
    BaseGroup,
    BaseUser,
    DBMAUser,
    MySQLUser,
    RedisUser,
    RootGroup,
    RootUser,
)


# region is_root


class IsRootTestCase(unittest.TestCase):
    """
    测试 is_root 函数
    """

    @patch("os.geteuid")
    def test_is_root_given_uid_equals_0(self, mock):
        """
        given: uid = 0
        when: 调用 is_root
        then: 返回 True
        """
        mock.return_value = 0
        expected = True
        result = is_root()
        self.assertEqual(result, expected)

    @patch("os.geteuid")
    def test_is_root_given_uid_not_equal_0(self, mock):
        """
        given: uid != 0
        when: 调用 is_root
        then: 返回 False
        """
        mock.return_value = 1000
        expected = False
        result = is_root()
        self.assertEqual(result, expected)


# endregion is_root


# region is_user_exists


class IsUserExistsTestCase(unittest.TestCase):
    """
    测试 is_user_exists
    """

    user = "mysql"

    @patch("pwd.getpwnam")
    def test_is_user_exists_given_user_exists(self, mock):
        expected = True
        result = is_user_exists(self.user)
        mock.assert_called_with(self.user)
        self.assertEqual(result, expected)

    @patch("pwd.getpwnam")
    def test_is_user_exists_given_user_not_exists(self, mock):
        mock.side_effect = KeyError()
        expected = False
        result = is_user_exists(self.user)
        self.assertEqual(result, expected)

        mock.side_effect = TypeError()
        result = is_user_exists(self.user)
        self.assertEqual(result, expected)


# endregion is_user_exists


# region is_group_exists
class IsGroupExistsTestCase(unittest.TestCase):
    """
    测试 is_group_exists
    """

    @patch("grp.getgrnam")
    def test_is_group_exists_given_not_exists(self, mock):
        """
        given: 给定的用户组不存在
        when: 调用 is_group_exists
        then: 返回 False
        """
        expected = False
        mock.side_effect = KeyError()
        result = is_group_exists("mysql")
        self.assertEqual(result, expected)

        mock.side_effect = TypeError()
        result = is_group_exists("mysql")
        self.assertEqual(result, expected)

    @patch("grp.getgrnam")
    def test_is_group_exists_given_exists(self, mock):
        """
        given: 给定的用户组存在
        when: 调用 is_group_exists
        then: 返回 True
        """
        expected = True
        mock.return_value = None
        result = is_group_exists("mysql")
        self.assertEqual(result, expected)


# endregion is_group_exists


# region get_uid_gid
class GetUidGidTestCase(unittest.TestCase):
    """
    测试 get_uid_gid
    """

    @patch("pwd.getpwnam")
    def test_get_uid_gid_when_exists(self, mock):
        """
        given: 给定的用户名存在
        when: 调用 get_uid_gid
        then: 返回用户名的(uid, gid)
        """
        UserInfo = namedtuple("UserInfo", "pw_uid, pw_gid")
        user_info = UserInfo(100, 100)
        mock.return_value = user_info

        uid, gid = get_uid_gid("mysql")
        mock.assert_called_with("mysql")
        self.assertEqual(uid, user_info.pw_uid)
        self.assertEqual(gid, user_info.pw_gid)

    @patch("pwd.getpwnam")
    def test_get_uid_gid_when_not_exists(self, mock):
        """
        given: 给定的用户名存在
        when: 调用 get_uid_gid
        then: 返回用户名的(uid, gid)
        """
        mock.side_effect = Exception()

        uid, gid = get_uid_gid("mysql")
        mock.assert_called_with("mysql")
        self.assertEqual(uid, 0)
        self.assertEqual(gid, 0)


# endregion get_uid_gid


# region Identify
class IdentifyTestCase(unittest.TestCase):
    """
    测试 Identify 类
    """

    def test_create_shell_str(self):
        identif = Identify("mysql")
        with self.assertRaises(NotImplementedError):
            identif.create_shell_str()

    def test_drop_shell_str(self):
        identif = Identify("mysql")
        with self.assertRaises(NotImplementedError):
            identif.drop_shell_str()

    def test_is_exists(self):
        identif = Identify("mysql")
        with self.assertRaises(NotImplementedError):
            identif.is_exists()

    @patch("dbma.bil.osuser.exe_shell_cmd")
    def test_create_given_user_exists(self, mock):
        identif = Identify("mysql")
        identif.is_exists = Mock()
        identif.is_exists.return_value = True
        identif.create()
        mock.assert_not_called()

    @patch("dbma.bil.osuser.exe_shell_cmd")
    def test_create_given_user_not_exists(self, mock):
        identif = Identify("mysql")
        identif.is_exists = Mock()
        identif.create_shell_str = Mock()

        identif.is_exists.return_value = False
        identif.create_shell_str.return_value = "useradd mysql"
        identif.create()
        mock.assert_called_once()
        mock.assert_called_with("useradd mysql")

    @patch("dbma.bil.osuser.exe_shell_cmd")
    def test_drop_given_user_exists(self, mock):
        identif = Identify("mysql")
        identif.is_exists = Mock()
        identif.drop_shell_str = Mock()

        identif.is_exists.return_value = True
        identif.drop_shell_str.return_value = "userdel mysql"
        identif.drop()
        mock.assert_called_once()
        mock.assert_called_with("userdel mysql")

    @patch("dbma.bil.osuser.exe_shell_cmd")
    def test_drop_given_user_not_exists(self, mock):
        identif = Identify("mysql")
        identif.is_exists = Mock()
        identif.drop_shell_str = Mock()

        identif.is_exists.return_value = False
        identif.drop_shell_str.return_value = "userdel mysql"
        identif.drop()
        mock.assert_not_called()


# endregion Identify


# region BaseGroup


class BaseGroupTestCase(unittest.TestCase):
    def test_create_shell_str(self):
        identify = BaseGroup("mysql")
        self.assertEqual(identify.create_shell_str(), "groupadd mysql")

    def test_drop_shell_str(self):
        identify = BaseGroup("mysql")
        self.assertEqual(identify.drop_shell_str(), "groupdel mysql")

    @patch("dbma.bil.osuser.is_group_exists")
    def test_is_exists_given_group_exists(self, mock):
        mock.return_value = True
        identify = BaseGroup("mysql")
        self.assertEqual(identify.is_exists(), True)

    @patch("dbma.bil.osuser.is_group_exists")
    def test_is_exists_given_group_not_exists(self, mock):
        mock.return_value = False
        identify = BaseGroup("mysql")
        self.assertEqual(identify.is_exists(), False)

    def test__str(self):
        """ """
        identify = BaseGroup("mysql")
        self.assertEqual(str(identify), "mysql")

    def test__repr(self):
        """ """
        identify = BaseGroup("mysql")
        self.assertEqual(repr(identify), "BaseGroup{name=mysql}")


# endregion BaseGroup


# region BaseUser


class BaseUserTestCase(unittest.TestCase):
    """
    测试 BaseUser
    """

    user_name: str = "mysql3306"

    def test_init(self):
        """
        given: 给定对象的 name 属性
        when: 访问对象的 name
        then: 能得到之前传进去的值
        """
        identify = BaseUser(self.user_name)
        self.assertEqual(identify.name, self.user_name)

    def test_create_shell_str(self):
        """
        given: 给定一个 BaseUser ,它的 group.name 的值为 “mysql”
        when: create_shell_str
        then: 返回的字符串应该是 “useradd mysql3306 -g mysql”
        """
        identify = BaseUser(self.user_name)
        identify.group = Mock()
        identify.group.name = "mysql"

        result = identify.create_shell_str()
        self.assertEqual(result, "useradd mysql3306 -g mysql")

        identify.home = "/home/mysql3306"
        result = identify.create_shell_str()
        self.assertEqual(result, "useradd mysql3306 -g mysql -d /home/mysql3306")

    def test_drop_shell_str(self):
        """
        given: 给定一个 BaseUser
        when: 调用 create_shell_str
        then: 返回的字符串应该是 "userdel mysql"
        """
        expected = "userdel mysql"
        identify = BaseUser("mysql")
        res = identify.drop_shell_str()
        self.assertEqual(res, expected)

    @patch("dbma.bil.osuser.is_user_exists")
    def test_is_exists_given_user_exists(self, mock):
        """
        given: 给定的用户存在于操作系统之上
        when:  调用 is_exists 方法
        then:  返回 True
        """
        mock.return_value = True
        identify = BaseUser(self.user_name)
        expected = True
        res = identify.is_exists()
        self.assertEqual(res, expected)

    @patch("dbma.bil.osuser.is_user_exists")
    def test_is_exists_given_user_not_exists(self, mock):
        """
        given: 给定的用户不存在于操作系统之上
        when:  调用 is_exists() 方法
        then:  返回 True
        """
        mock.return_value = False
        identify = BaseUser(self.user_name)
        expected = False
        res = identify.is_exists()
        self.assertEqual(res, expected)

    def test_create_given_group_exists(self):
        """
        given: 给定的用户存在于操作系统之上
        when:  调用 create() 方法
        then:  创建给定的用户
        """
        identify = BaseUser(self.user_name)
        identify.group = Mock()
        identify.group.is_exists.return_value = True
        with patch.object(Identify, "create") as ic_mock:
            identify.create()
            ic_mock.assert_called_once()

    def test_create_given_group_not_exists(self):
        """
        given: 给定的用户存在于操作系统之上
        when:  调用 create() 方法
        then:  创建给定的用户
        """
        identify = BaseUser(self.user_name)
        identify.group = Mock()
        identify.group.is_exists.return_value = False
        with patch.object(Identify, "create") as ic_mock:
            identify.create()
            ic_mock.assert_called_once()
        # 当 group 不存在的时候会调用 group 的 create 方法
        identify.group.create.assert_called_once()

    @patch("dbma.bil.osuser.exe_shell_cmd")
    def test_chown(self, mock):
        t_p = "/database/mysql/data/3306"
        identify = BaseUser(self.user_name)
        identify.group = "mysql"
        identify.chown(t_p)
        mock.assert_called_once()
        mock.assert_called_with("chown -R mysql3306:mysql /database/mysql/data/3306")

        identify.chown(t_p, recursive=False)
        mock.assert_called_with("chown mysql3306:mysql /database/mysql/data/3306")


# endregion BaseUser


# region DBMUser


class DBMAUserTestCase(unittest.TestCase):
    user_name: str = "mysql"

    def test__init(self):
        identify = DBMAUser(self.user_name)
        self.assertEqual(identify.name, self.user_name)


# endregion DBMUser


# region MySQLUser


class MySQLUserTestCase(unittest.TestCase):
    mysql_port: int = 3306

    def test__init(self):
        identify = MySQLUser(self.mysql_port)
        self.assertEqual(identify.name, "mysql{}".format(self.mysql_port))

    def test_create(self):
        """
        given: 给定的用户存在
        when:  调用 create() 方法
        then:
        """
        identity = MySQLUser(self.mysql_port)
        identity.group.is_exists = Mock(return_value=True)
        with patch.object(BaseUser, "create") as mock:
            identity.create()
        mock.assert_called_once()

        identity.group.is_exists = Mock(return_value=False)
        with patch.object(BaseUser, "create") as mock:
            identity.create()
        mock.assert_called_once()

    def test__str(self):
        expected = "mysql3306:mysql"
        identity = MySQLUser(self.mysql_port)
        self.assertEqual(str(identity), expected)


# endregion MySQLUser


# region RediskUser


class RedisUserTestCase(unittest.TestCase):
    """
    测试 RedisUser
    """

    redis_port: int = 6375

    def test__init(self):
        identify = RedisUser(self.redis_port)
        self.assertEqual(identify.name, "redis{}".format(self.redis_port))

    def test_create(self):
        identify = RedisUser(self.redis_port)
        identify.group = Mock()
        identify.group.is_exists = Mock(return_value=True)
        identify.create()

        identify.group.is_exists = Mock(return_value=False)
        identify.group.create = Mock()
        identify.create()

        identify.group.create.assert_called()

    def test__str(self):
        identify = RedisUser(self.redis_port)
        expected = "redis{}:redis".format(self.redis_port)
        self.assertEqual(str(identify), expected)


# endregion RedisUser


# region RootGroup


class RootGroupTestCase(unittest.TestCase):
    """ """

    def test_drop(self):
        identify = RootGroup()
        identify.drop()


# endregion RootGroup


# region RootUser


class RootUserTestCase(unittest.TestCase):
    """ """

    def test_drop(self):
        identify = RootUser()
        identify.drop()


# endregion RootUser
