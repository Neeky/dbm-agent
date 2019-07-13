import os
import unittest
from dbma import log

class LogTestCase(unittest.TestCase):
    def setUp(self):
        self.logger = log.log_config(filename="/tmp/dbma-test.log",root_logger_name="dbm-agent")

    def test_logger_is_singleton(self):
        self.assertIs(self.logger,log.get_root_logger('dbm-agent'))
    
    def tearDown(self):
        if os.path.isfile('/tmp/dbma-test.log'):
            os.remove('/tmp/dbma-test.log')
    