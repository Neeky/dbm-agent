
import os
import logging
import unittest

from dbma.loggers.loggers import root_logger

class RootLoggerTestCase(unittest.TestCase):
    """
    """
    @unittest.skip
    def test_001_default_logger_level(self):
        """
        默认情况下 root-logger 的日志级别是 INFO
        """
        self.assertEqual(root_logger.level,logging.INFO)

    def test_002_debug_logger_level(self):
        """
        当环境变量 DEMA_DEBUG 被设置时 root-logger 的日志级别是 DEBUG
        """
        if 'DBMA_DEBUG' in os.environ:
            self.assertEqual(root_logger.level,logging.DEBUG)
        else:
            self.assertEqual(root_logger.level,logging.INFO)

    
    