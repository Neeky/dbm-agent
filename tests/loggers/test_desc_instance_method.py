"""
检查实例方法装饰器的正确性

# (c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""

import logging
import unittest
from dbma.loggers.loggers import desc_instance_method,loggers_logger,root_logger

class TempCls(object):
    """
    """

    logger = loggers_logger.getChild("test").getChild("TempCls")

    @desc_instance_method(logging.DEBUG)
    def fun(self):
        """
        """
        self.logger.warning(f"this is test logger.")


class InstanceLoggerDescTestCase(unittest.TestCase):
    """
    """
    @classmethod
    def setUpClass(cls):
        

        cls.handlers = [handler for handler in root_logger.handlers]
        root_logger.handlers.clear()

        root_logger.addHandler(logging.FileHandler("/tmp/1sfes.log"))
        print('#' * 32)
        print(cls.handlers)
        print('#' * 32)

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        for handler in root_logger.handlers:
            handler.close()
        root_logger.handlers.clear()

        for handler in cls.handlers:
            root_logger.addHandler(handler)

        print('#' * 32)
        print(root_logger.handlers)
        root_logger.error("hello world.")
        print('#' * 32) 
        
        return super().tearDownClass()


    def test_instance_logger(self):
        """
        检查 实例方法装饰器是否能正常工作
        """
        tc = TempCls()
        tc.fun()
        




    

    




