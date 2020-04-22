import os
import logging
import unittest
from unittest.mock import MagicMock

from dbma.softinstall import MySQLBinaryInstall, BaseSoftInstall

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s")


class TestMySQLBinaryInstallTestCase(unittest.TestCase):
    """
    """
    mysql_installer = MySQLBinaryInstall(
        pkg="mysql-8.0.19-linux-glibc2.12-x86_64.tar.xz")

    def test_01_sopath(self):
        """ 8.0.19
        """
        lib_dir, version = self.mysql_installer.sopath
        self.assertEqual(
            lib_dir, "/usr/local/mysql-8.0.19-linux-glibc2.12-x86_64/lib")
        self.assertEqual(version, "mysql-8.0.19-linux-glibc2.12-x86_64")

    def test_02_path(self):
        bin_dir = self.mysql_installer.mysql_bin_dir
        self.assertEqual(
            bin_dir, "/usr/local/mysql-8.0.19-linux-glibc2.12-x86_64/bin")

    def test_03_is_has_been_installed(self):
        self.assertFalse(self.mysql_installer.is_has_been_installed)

    def test_04_is_an_supported_mysql_version(self):
        self.assertTrue(self.mysql_installer.is_an_supported_mysql_version)

    def test_05_install(self):
        """mock
        """
        self.mysql_installer.install_mysql = MagicMock()
        self.mysql_installer.install()
        self.mysql_installer.install_mysql.assert_called_once_with()
