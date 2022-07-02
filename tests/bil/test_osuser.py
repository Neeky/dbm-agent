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