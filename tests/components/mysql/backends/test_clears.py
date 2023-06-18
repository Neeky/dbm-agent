# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from dbma.components.mysql.backends.clears import ClearTask, scan_data_dir_gen_task


class ScanDirsGenTaskTestCase(unittest.TestCase):
    """ """

    @patch("glob.glob")
    def test_scan_data_dir_gen_task(self, mock):
        """ """
        mock.return_value = [
            "/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128",
            "/database/mysql/data/3307-backup-2023-06-17T14-45-21-949788",
        ]

        tasks = scan_data_dir_gen_task()

        calls = [call("/database/mysql/data/*"), call("/database/mysql/binlog/*")]
        self.assertEqual(mock.call_args_list, calls)
