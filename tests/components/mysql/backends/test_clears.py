# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import datetime
from dbma.components.mysql.backends.clears import ClearTask, scan_data_dir_gen_task


# region scan_data_dir_gen_task
class ScanDirsGenTaskTestCase(unittest.TestCase):
    """ """

    @patch("glob.glob")
    def test_scan_data_dir_gen_task(self, mock):
        """
        given: 预期的调用环境下
        when: 调用 scan_data_dir_gen_task
        then: /database/mysql/data/*, /database/mysql/binlog/* 这两个地方都要被扫一次
        """
        mock.return_value = [
            "/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128",
            "/database/mysql/data/3307-backup-2023-06-17T14-45-21-949788",
        ]

        tasks = scan_data_dir_gen_task()

        calls = [call("/database/mysql/data/*"), call("/database/mysql/binlog/*")]
        self.assertEqual(mock.call_args_list, calls)


# endregion scan_data_dir_gen_task


# region ClearTask
class ClearTaskTestCase(unittest.TestCase):
    def test__init(self):
        task = ClearTask("/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128")

    def test_is_expired_given_dir_expired(self):
        """
        given: 给定的备份目录已经过期
        when: 调用 task.is_expired()
        then: 返回 True
        """
        task = ClearTask("/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128")
        self.assertEqual(task.is_expired(), True)

    def test_is_expired_given_dir_not_expired(self):
        """
        given: 给定的备份目录没有过期
        when: 调用 task.is_expired()
        then: 返回 False
        """
        task = ClearTask("/database/mysql/data/3308-backup-2023-01-01T01-01-01-472128")
        now = datetime(2023, 1, 2, 0, 0, 0)
        self.assertEqual(task.is_expired(now), False)


# endregion ClearTask
