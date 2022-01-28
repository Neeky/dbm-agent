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

    