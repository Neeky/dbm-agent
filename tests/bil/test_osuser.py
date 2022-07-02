# -*- coding: utf8 -*-
"""
实现操作系统用户的相关操作
"""

import unittest
from unittest.mock import MagicMock

class UserGroupExistsCheckerTestCase(unittest.TestCase):
    """
    对用户、组的存在性进行检查
    这个依赖于操作系统的用户和组的存在性
    """
    EXIST_USER = "root"
    NOT_EXIST_USER = "not_exist_user_"

    EXIST_GROUP = "wheel"
    NOT_EXIST_GROUP = "not_exist_group_"

    def test_when_user_not_exists_then_false(self):
        """
        """
        from dbma.bil import osuser
        self.assertFalse(osuser.is_user_exists(self.NOT_EXIST_USER))

    def test_when_name_not_str_then_false(self):
        """
        """
        from dbma.bil import osuser
        self.assertFalse(osuser.is_user_exists(None))
            
    def test_when_user_exists_then_true(self):
        """
        """
        from dbma.bil import osuser
        self.assertTrue(osuser.is_user_exists(self.EXIST_USER))

    def test_when_group_not_exists_then_false(self):
        """
        """
        from dbma.bil import osuser
        self.assertFalse(osuser.is_group_exists(self.NOT_EXIST_GROUP))

    def test_when_group_exists_then_true(self):
        """
        """
        from dbma.bil import osuser
        self.assertTrue(osuser.is_group_exists(self.EXIST_GROUP))

    def test_when_type_error_then_false(self):
        """
        """
        from dbma.bil import osuser
        self.assertFalse(osuser.is_group_exists(None))


class IdentifyTestCase(unittest.TestCase):
    """
    检查整个创建的流程是否正常
    """
    def test_give_identify_not_exists_when_create_then_create_it(self):
        """
        given: 用户|组不存在
        when: 调用 create 方法
        then: 这个时候要去执行整个创建流程
        """
        from dbma.bil.osuser import Identify
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        identify = Identify("mysql")
        identify.is_exists = MagicMock(return_value=False)
        identify.create_shell_str = MagicMock(return_value="groupadd mysql")
        identify.create()

        identify.is_exists.assert_called_once()
        identify.create_shell_str.assert_called_once()
        osuser.exe_shell_cmd.assert_called_once()
        osuser.exe_shell_cmd.assert_called_once_with("groupadd mysql")

    def test_give_identify_exists_when_create_then_do_nothing(self):
        """
        given: 用户|组存在
        when: 调用 create 方法
        then: 这个时候不去执行整个创建流程
        """
        from dbma.bil.osuser import Identify
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        identify = Identify("mysql")
        identify.is_exists = MagicMock(return_value=True)
        identify.create_shell_str = MagicMock(return_value="groupadd mysql")
        identify.create()

        # 检查要执行
        identify.is_exists.assert_called_once()
        # 不执行任何形式的操作
        identify.create_shell_str.assert_not_called()
        osuser.exe_shell_cmd.assert_not_called()


    def test_give_identify_not_exists_when_drop_then_do_nothing(self):
        """
        given: 用户|组不存在
        when: 调用 drop 方法
        then: 不执行任何一个操作
        """
        from dbma.bil.osuser import Identify
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        identify = Identify("mysql")
        identify.is_exists = MagicMock(return_value=False)
        identify.drop_shell_str = MagicMock(return_value="groupdel mysql")
        identify.drop()

        # 检查要执行
        identify.is_exists.assert_called_once()
        # 不执行任何形式上的操作
        identify.drop_shell_str.assert_not_called()
        osuser.exe_shell_cmd.assert_not_called()

    def test_give_identify_exists_when_drop_then_drop_it(self):
        """
        given: 用户|组存在
        when: 调用 drop 方法
        then: 这个时候要去执行整个删除流程
        """
        from dbma.bil.osuser import Identify
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        identify = Identify("mysql")
        identify.is_exists = MagicMock(return_value=True)
        identify.drop_shell_str = MagicMock(return_value="groupdel mysql")
        identify.drop()

        identify.is_exists.assert_called_once()
        identify.drop_shell_str.assert_called_once()
        osuser.exe_shell_cmd.assert_called_once()
        osuser.exe_shell_cmd.assert_called_once_with("groupdel mysql")


class RootGroupTestCase(unittest.TestCase):
    """
    针对 root 组的行为进行检查
    """

    def test_given_group_is_root_when_checke_is_exists_then_return_true(self):
        """
        give: 给定要检查的组名是 root
        when: 要检查组是否存在
        then: 我们认为这个组一定存在于操作系统中、所以这个一定会返回 true
        """
        from dbma.bil.osuser import RootGroup
        from dbma.bil import osuser

        root_group = RootGroup()
        self.assertTrue(root_group.is_exists())

    def test_given_group_is_root_when_create_then_do_nothing(self):
        """
        given: 给定要创建的组名是 root
        when: 调用 create 方法
        then: 不执行任何操作
        """
        from dbma.bil.osuser import RootGroup
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        root_group = RootGroup()
        root_group.is_exists = MagicMock(return_value=True)
        root_group.create_shell_str = MagicMock(return_value="groupadd root")
        root_group.create()

        root_group.is_exists.assert_called_once()
        root_group.create_shell_str.assert_not_called()
        osuser.exe_shell_cmd.assert_not_called()

    def test_given_group_is_root_when_drop_then_do_nothing(self):
        """
        given: 给定要删除的组名是 root
        when: 调用 drop 方法
        then: 不执行任何操作(RootGroup 重写了 drop 方法，这个方法是空的不会做任何事)
        """
        from dbma.bil.osuser import RootGroup
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        root_group = RootGroup()
        root_group.is_exists = MagicMock(return_value=True)
        root_group.drop_shell_str = MagicMock(return_value="groupdel root")
        root_group.drop()

        root_group.is_exists.assert_not_called()
        root_group.drop_shell_str.assert_not_called()
        osuser.exe_shell_cmd.assert_not_called()

    def test_given_group_is_root_when_convert_to_string_then_return_root(self):
        """
        given: 给定要转换的组名是 root
        when: 调用 __str__ 方法
        then: 返回的字符串应该是 root
        """
        from dbma.bil.osuser import RootGroup
        root_group = RootGroup()
        self.assertEqual(str(root_group), "root")


class RootUserTestCase(unittest.TestCase):
    """
    """
    def test_given_user_is_root_when_drop_then_do_nothing(self):
        """
        given: 给定的用户是 root
        when: 调用 drop 操作
        then: 什么操作也不做
        """
        from dbma.bil.osuser import RootUser
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        root_user = RootUser()
        root_user.is_exists = MagicMock(return_value=True)
        root_user.drop_shell_str = MagicMock(return_value="userdel root")
        root_user.drop()

        root_user.is_exists.assert_not_called()
        root_user.drop_shell_str.assert_not_called()
        osuser.exe_shell_cmd.assert_not_called()

    def test_given_user_is_root_when_check_is_user_exists_then_return_true(self):
        """
        given: 给定的用户是 root
        when: 检查用户是否存在
        then: 返回 true ，我们认为 linux 中一定存在 root 用户
        """
        from dbma.bil.osuser import RootUser
        self.assertTrue(RootUser().is_exists())

    def test_given_user_is_root_when_create_then_do_nothing(self):
        """
        given: 给定的用户是 root
        when: 调用 create 方法
        then: 不执行任何操作
        """
        from dbma.bil.osuser import RootUser
        from dbma.bil import osuser

        osuser.exe_shell_cmd = MagicMock()
        root_user = RootUser()
        root_user.is_exists = MagicMock(return_value=True)
        root_user.create_shell_str = MagicMock(return_value="useradd root")
        root_user.create()

        root_user.is_exists.assert_called_once()
        root_user.create_shell_str.assert_not_called()
        osuser.exe_shell_cmd.assert_not_called()

    def test_given_user_is_root_when_convert_to_string_then_return_root_sep_root(self):
        """
        given: 给定的用户是 root
        when: 调用 __str__ 方法
        then: 返回的字符串应该是 root:root
        """
        from dbma.bil.osuser import RootUser
        self.assertEqual(str(RootUser()), "root:root")