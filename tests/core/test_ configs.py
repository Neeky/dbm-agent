# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from pathlib import Path

from dbma.core.configs import Cnfr


class CnfrTestCase(unittest.TestCase):
    def test_save_given_config_file_path_not_exists(self):
        """
        given: 给定的配置对象没有设置 config_file_path 属性
        when: 调用 save 方法
        then: 报异常
        """
        cnf = Cnfr()
        with self.assertRaises(ValueError):
            cnf.save()
