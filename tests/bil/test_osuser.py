# -*- coding: utf8 -*-

"""
测试 osuser.py 模块
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from collections import namedtuple

from dbma.bil.osuser import is_root, is_user_exists, is_group_exists, get_uid_gid

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
