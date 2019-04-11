"""
对 dbma.utils.directorys 进行测试
"""
import os
import unittest
from dbma.utils import directors

class DirectorysTestCase(unittest.TestCase):

    def test_001_create_directory_if_not_exists(self):
        """
        测试创建目录的功能
        """
        directors.create_directory_if_not_exists('/tmp/dir_temp_1234',owner='root')
        self.assertTrue(os.path.isdir('/tmp/dir_temp_1234'))
        os.removedirs('/tmp/dir_temp_1234')
        self.assertFalse(os.path.isdir('/tmp/dir_temp_1234'))
        