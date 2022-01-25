# -*- coding: utf8 -*-
"""
实现操作系统用户的相关操作
"""

import unittest

from dbma.bil import osuser

class OsUserTestCase(unittest.TestCase):
    """
    """
    def test_when_user_not_exists_then_false(self):
        """
        """
        self.assertFalse(osuser.is_user_exists("not_exist_user_"))
