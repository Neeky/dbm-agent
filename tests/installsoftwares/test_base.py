# -*- coding: utf8 -*-
"""
对于软件安装环节各个功能的测试
"""

import unittest
from unittest.mock import MagicMock


class BinaryInstallTestCase(unittest.TestCase):
    """
    """
    def test_given_pkg_and_user_when_call_install_then_do_install_procedure(self):
        from dbma.installsoftwares.base import BinaryInstall
        bi = BinaryInstall(pkg="TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz")
        bi.is_pkg_exists = MagicMock(return_value=True)
        bi.create_user = MagicMock(return_value=None)
        bi.extract_pkg = MagicMock(return_value=None)
        bi.make_link = MagicMock(return_value=None)
        bi.chown = MagicMock(return_value=None)
        bi.exports = MagicMock(return_value=None)

        bi.install()

        bi.is_pkg_exists.assert_called_once()
        bi.create_user.assert_called_once()
        bi.extract_pkg.assert_called_once()
        bi.make_link.assert_called_once()
        bi.chown.assert_called_once()
        bi.exports.assert_called_once()

    def test_given_env_not_exists_when_call_export_env_then_write_it_to_etc_profile(self):
        """
        """
        from dbma.bil import fs
        fs.is_line_in_etc_profile = MagicMock(return_value=False)
        fs.append_new_line_to_etc_profile = MagicMock(return_value=None)

        from dbma.installsoftwares.java import JavaInstall
        bi = JavaInstall()
        bi.export_env("JAVA_HOME", "/usr/local/java")

        fs.is_line_in_etc_profile.assert_called_once()
        fs.append_new_line_to_etc_profile.assert_called_once()

    
    def test_is_pkg_exists_given_pkg_exists_then_return_true(self):
        """
        """
        from dbma.bil import fs
        fs.is_file_exists = MagicMock(return_value=True)

        from dbma.installsoftwares.base import BinaryInstall
        bi = BinaryInstall(pkg="TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz")
        self.assertTrue(bi.is_pkg_exists())
        fs.is_file_exists.assert_called_once_with("/usr/local/dbm-agent/pkg/")

    def test_extract_pkg_given_pkg_exists_then_extract_it(self):
        """
        """
        from dbma.bil import fs
        fs.is_file_exists = MagicMock(return_value=True)
        fs.extract_tar_file = MagicMock(return_value=None)

        from dbma.installsoftwares.base import BinaryInstall
        bi = BinaryInstall(pkg="TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz")
        bi.extract_pkg()
        fs.extract_tar_file.assert_called_once_with("/usr/local/dbm-agent/pkg/TencentKona-17.0.3.b1-jdk_linux-x86_64.tar.gz", "/usr/local/")