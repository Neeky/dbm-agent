# -*- coding: utf8 -*-

import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from collections import namedtuple

from dbma.bil.fs import get_file_size, is_file_greater_then


# region get_file_size
class GetFileSizeTestCase(unittest.TestCase):
    @patch("os.lstat")
    def test_get_file_size(self, mock):
        """ """
        StatResult = namedtuple("StatResult", "st_size")
        mock.return_value = StatResult(128 * 1024 * 1024)

        expected = 128 * 1024 * 1024
        result = get_file_size("/tmp/a.txt")
        self.assertEqual(expected, result)


# endregion get_file_size


# region is_file_greater_then


class IsFileGreaterThenTestCase(unittest.TestCase):
    """ """

    file_name = "/tmp/big-file.txt"

    @patch("dbma.bil.fs.get_file_size")
    def test_is_file_greater_then_given_file_greater(self, mock):
        """
        given: 给定的文件比 16MB 要大
        when: 调用 is_file_greater_then
        then: 返回 True
        """
        mock.return_value = 8 * 1024 * 1024

        result = is_file_greater_then(self.file_name, 16 * 1024 * 1024)
        self.assertEqual(result, False)


# endregion is_file_greater_then
