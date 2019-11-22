
import unittest
from unittest.mock import Mock, patch
from dbma.mysqldeploy import MyCnfRender


class MyCnfRenderTestCase(unittest.TestCase):
    """
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        cls.render = MyCnfRender(basedir="/usr/local/mysql-8.0.18-linux-glibc2.12-x86_64/",
                                 datadir="/database/mysql/data/3306/", binlogdir="/binlog/mysql/binlog/3306",
                                 max_mem=128, cores=1, port=3306, user="mysql3306")
        cls.render.auto_config()

    @classmethod
    def tearDownClass(cls):
        """
        """
        pass

    def test_01_auto_config(self):
        pass

    def test_02_innodb_buffer_pool_size(self):
        self.assertEqual(self.render.innodb_buffer_pool_size, "128M")

    def test_03_user(self):
        self.assertEqual(self.render.user, "mysql3306")
