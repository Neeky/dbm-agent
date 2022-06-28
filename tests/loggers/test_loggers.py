"""
tests for loggers.loggers
"""

import os
import logging
import unittest

from dbma.loggers.loggers import get_logger_name

class GetLoggerNameTestCase(unittest.TestCase):
    """测试 get_logger_name 算法是否正确
    """
    def test_given_core_httpserver_then_return_core_httpserver(self):
        self.assertEqual(get_logger_name('/data/repos/dbm-agent/dbma/core/httpserver.py'), 'dbma.core.httpserver')
        self.assertEqual(get_logger_name("/usr/local/python/bin/dbm-agent"), "dbm-agent")