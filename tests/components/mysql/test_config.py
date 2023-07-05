# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from dbma.components.mysql.config import MySQLConfig


class MySQLConfigTestCase(unittest.TestCase):
    """
    MySQL 配置文件生成类的测试
    """

    basedir = "mysql-8.0.33-linux-glibc2.28-x86_64"
    port = 3333
    innodb_buffer_pool_size = "128M"

    def test_given_(self):
        """ """
        cnf = MySQLConfig(self.basedir, self.port, self.innodb_buffer_pool_size)
        self.assertEqual(cnf.version, "8.0.33")
        cnf._calcu_deps_basedir = Mock()
        cnf._calcu_deps_mem = Mock()
        cnf._calcu_deps_port = Mock()
        cnf._calcu_random_attrs = Mock()

        # cnf.calcu_second_attrs()

        # cnf._calcu_deps_basedir.assert_called_once()
        # cnf._calcu_deps_mem.assert_called_once()
        # cnf._calcu_deps_port.assert_called_once()
        # cnf._calcu_random_attrs.assert_called_once()
