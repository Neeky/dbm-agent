# -*- coding: utf8 -*-
"""
实现操作系统用户的相关操作
"""

import unittest

from dbma.bil import osuser

class OsUserTestCase(unittest.TestCase):
    """
    """
    EXIST_USER = "root"
    NOT_EXIST_USER = "not_exist_user_"

    EXIST_GROUP = "wheel"
    NOT_EXIST_GROUP = "not_exist_group_"

    def test_when_user_not_exists_then_false(self):
        """
        """
        self.assertFalse(osuser.is_user_exists(self.NOT_EXIST_USER))

    def test_when_name_not_str_then_false(self):
        """
        """
        self.assertFalse(osuser.is_user_exists(None))
            
    def test_when_user_exists_then_true(self):
        """
        """
        self.assertTrue(osuser.is_user_exists(self.EXIST_USER))

    def test_when_group_not_exists_then_false(self):
        """
        """
        self.assertFalse(osuser.is_group_exists(self.NOT_EXIST_GROUP))

    def test_when_group_exists_then_true(self):
        """
        """
        self.assertTrue(osuser.is_group_exists(self.EXIST_GROUP))

    def test_when_type_error_then_false(self):
        """
        """
        self.assertFalse(osuser.is_group_exists(None))


class BaseGroupTestCase(unittest.TestCase):
    """
    """
    NOT_EXIST_GROUP = "not_exist_group_"

    def test_when_give_mysql_then_return_groupadd_mysql(self):
        """
        """
        group = osuser.BaseGroup("mysql")
        self.assertEqual("groupadd mysql",group.create_shell_str())


    def test_when_group_not_exists_then_false(self):
        """
        """
        group = osuser.BaseGroup(self.NOT_EXIST_GROUP)
        self.assertFalse(group.is_exists())


class BaseUserTestCase(unittest.TestCase):
    """
    """
    NOT_EXISTS_USER = "mysql33333"

    def test_when_give_mysql3306_then_return_useradd_mysql(self):
        mysql_user = osuser.BaseUser(name="mysql3306",group="mysql")
        self.assertEqual("useradd mysql3306 -g mysql", mysql_user.create_shell_str())

    def test_when_user_not_exists_then_false(self):
        """
        """
        user = osuser.BaseUser(name=self.NOT_EXISTS_USER,group="mysql")
        self.assertFalse(user.is_exists())


class MySQLGroupTestCase(unittest.TestCase):
    def test_defautl_return_groupadd_mysql(self):
        group = osuser.MySQLGroup()
        self.assertEqual("groupadd mysql",group.create_shell_str())

class MySQLUserTestCase(unittest.TestCase):
    """
    """
    def test_default_return_useradd_mysql3306__g_mysql(self):
        user = osuser.MySQLUser()
        self.assertEqual("useradd mysql3306 -g mysql",user.create_shell_str())