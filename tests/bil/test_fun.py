# -*- coding: utf8 -*-

"""
测试 fun.py 模块
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from dbma.bil.fun import fname


class FnameTestCase(unittest.TestCase):
    @patch("inspect.stack")
    def test_fname(self, mock):
        mock.return_value = [None, [None, None, None, "funhello"]]
        expected = "funhello"
        result = fname()
        self.assertEqual(result, expected)
