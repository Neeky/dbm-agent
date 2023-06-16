# -*- coding: utf8 -*-

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path, PosixPath
from dbma.components.mysql.install import (
    create_init_sql_file,
    remove_init_sql_file,
    checks_for_install,
    enable_systemd_for_mysql,
    disable_systemd_for_mysql,
    check_mysql_systemd_exists,
    exe_shell_cmd,
    start_mysql,
    stop_mysql,
)
from dbma.components.mysql.asserts import (
    assert_mysql_install_pkg_exists,
    assert_mysql_datadir_not_exists,
    assert_mysql_systemd_file_exists,
    assert_mysql_systemd_file_not_exists,
)
from dbma.components.mysql.exceptions import MySQLSystemdFileNotExists


# region create_init_sql_file
class CreateInitSQLFileTestCase(unittest.TestCase):
    # 不管是哪个版本的 MySQL 用户初始化文件都是一个
    dest = "/tmp/mysql-init-user.sql"

    @patch("shutil.copy")
    def test_create_init_sql_file_given_8_0_x_version(self, mock):
        """
        given: 当给定的 MySQL 版本号是 MySQL-8.0.x 版本的话，就复制 init-8.0.x.sql 到 /tmp/
        when: 调用 create_init_sql_file
        then: shutil.copy 会复制对应的文件到 /tmp/
        """
        src = PosixPath("/data/repos/dbm-agent/dbma/static/cnfs/init-8.0.x.sql")
        # dest = "/tmp/mysql-init-user.sql"
        create_init_sql_file("8.0.23")
        mock.assert_called_once()
        mock.assert_called_once_with(src, self.dest)

    @patch("shutil.copy")
    def test_create_init_sql_file_given_5_7_x_version(self, mock):
        """
        given: 当给定的 MySQL 版本号是 MySQL-5.7.x 版本的话，就复制 init-5.7.x.sql 到 /tmp/
        when: 调用 create_init_sql_file
        then: shutil.copy 会复制对应的文件到 /tmp/
        """
        src = PosixPath("/data/repos/dbm-agent/dbma/static/cnfs/init-5.7.x.sql")
        create_init_sql_file("5.7.44")
        mock.assert_called_once()
        mock.assert_called_once_with(src, self.dest)

    @patch("shutil.copy")
    def test_create_init_sql_file_given_error_version(self, mock):
        """
        given: 当给定的 MySQL 版本号是不被支持的
        when: 调用 create_init_sql_file
        then: shutil.copy 就不会被调用并且报 ValueError
        """
        src = PosixPath("/data/repos/dbm-agent/dbma/static/cnfs/init-5.7.x.sql")
        with self.assertRaises(ValueError):
            create_init_sql_file("8848.10086.10000")

        mock.assert_not_called()

    def test_create_init_sql_file_given_none_value(self):
        with self.assertRaises(ValueError):
            create_init_sql_file()


# endregion create_init_sql_file


# region remove_init_sql_file
class RemoveInitSqlFileTestCase(unittest.TestCase):
    @patch("os.remove")
    def test_remove_init_sql_file_given_init_file_exists(self, mock_remove):
        """
        given: /tmp/mysql-init.sql 存在
        when: 调用 remove_init_sql_file
        then: 删除 /tmp/mysql-init.sql 文件
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            remove_init_sql_file()
            mock_remove.assert_called_once()
            mock_remove.assert_called_with(PosixPath("/tmp/mysql-init-user.sql"))

    @patch("os.remove")
    def test_remove_init_sql_file_given_init_file_not_exists(self, mock_remove):
        """
        given: /tmp/mysql-init.sql 不存在
        when: 调用 remove_init_sql_file
        then: 不会调用 os.remove 函数
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            remove_init_sql_file()
            mock_remove.assert_not_called()


# endregion remove_init_sql_file


# region checks_for_install


class ChecksForInstallTestCase(unittest.TestCase):
    @patch("dbma.components.mysql.install.assert_mysql_datadir_not_exists")
    @patch("dbma.components.mysql.install.assert_mysql_install_pkg_exists")
    def test_checks_for_install(self, mock_pkg, mock_dir):
        pkg = Path(
            "/usr/local/dbm-agent/pkgs/mysql-8.0.3333-linux-glibc2.28-x86_64.tar.gz"
        )
        checks_for_install(3306, pkg)
        mock_pkg.assert_called_once()
        mock_dir.assert_called_once()

        mock_pkg.assert_called_with(pkg)
        mock_dir.assert_called_with(3306)


# endregion checks_for_install


# region enable_systemd_for_mysql


class EnableSystemdForMysqlTestCase(unittest.TestCase):
    port: int = 3308
    enable_cmd = "systemctl enable mysqld-3308"

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_enable_systemd_for_mysql_given_systemd_exists(self, mock_a, mock_e):
        """
        given: 给定端口号对应的 Systemd 文件存在
        when: 调用 enable_systemd_for_mysql
        then: 去调用对应的 systemctl 命令
        """
        enable_systemd_for_mysql(self.port)
        mock_a.assert_called_with(self.port)
        mock_e.assert_called_with(self.enable_cmd)

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_enable_systemd_for_mysql_given_systemd_not_exists(self, mock_a, mock_e):
        """
        given: 给定端口号对应的 Systemd 文件不存在
        when: 调用 enable_systemd_for_mysql
        then: 报异常
        """
        mock_a.side_effect = MySQLSystemdFileNotExists()
        with self.assertRaises(MySQLSystemdFileNotExists):
            enable_systemd_for_mysql(self.port)
        mock_a.assert_called_with(self.port)
        mock_e.not_called()


# endregion enable_systemd_for_mysql


# region disable_systemd_for_mysql
class DisableSystemdForMysqlTestCase(unittest.TestCase):
    """
    disable_systemd_for_mysql 的测试用例
    """

    port: int = 3308
    enable_cmd: str = "systemctl disable mysqld-{}".format(port)

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_disable_systemd_for_mysql_given_systemd_exists(
        self, mock_exists, mock_cmd
    ):
        """
        given: 给定端口对应的 systemd 文件存在
        when: 调用 disable_systemd_for_mysql
        then: 执行对应的 systemctl disable xxx 命令
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = True
            disable_systemd_for_mysql(self.port)

        mock_exists.assert_called_with(self.port)
        mock_cmd.assert_called_with(self.enable_cmd)

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_disable_systemd_for_mysql_given_systemd_not_exists(
        self, mock_exists, mock_cmd
    ):
        """
        given: 给定端口对应的 systemd 文件不存在
        when: 调用 disable_systemd_for_mysql
        then: 报异常
        """
        mock_exists.side_effect = MySQLSystemdFileNotExists()
        with patch.object(Path, "exists") as mock:
            mock.return_value = False
            with self.assertRaises(MySQLSystemdFileNotExists):
                disable_systemd_for_mysql(self.port)

        mock_exists.assert_called_with(self.port)
        mock_cmd.assert_not_called()


# endregion disable_systemd_for_mysql

# region check_mysql_systemd_exists


class CheckMysqlSystemdExistsTestCase(unittest.TestCase):
    port = 3306

    def test_check_mysql_systemd_exists_given_exists(self):
        """
        given: mysql systemd 配置文件存在
        when: 调用 check_mysql_systemd_exists(3306)
        then: 正常执行
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = True
            check_mysql_systemd_exists(self.port)

    def test_check_mysql_systemd_exists_given_not_exists(self):
        """
        given: mysql systemd 配置文件存在
        when: 调用 check_mysql_systemd_exists(3306)
        then: 报异常
        """
        with patch.object(Path, "exists") as mock:
            mock.return_value = False
            with self.assertRaises(MySQLSystemdFileNotExists):
                check_mysql_systemd_exists(self.port)


# endregion check_mysql_systemd_exists


# region start_mysql


class StartMySQLTestCase(unittest.TestCase):
    """ """

    port = 3306

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_start_mysql_given_instance_exists(self, mock_assert, mock_exec):
        """
        given: 给定的 MySQL 实例存在
        when: 调用 start_mysql
        then: 执行 systemctl start mysqld-${port} 命令
        """
        mock_assert.return_value = True
        start_mysql(self.port)

        mock_assert.assert_called_once()
        mock_assert.assert_called_once_with(self.port)

        mock_exec.assert_called_once()
        mock_exec.assert_called_once_with("systemctl start mysqld-3306")

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_start_mysql_given_instance_not_exists(self, mock_assert, mock_exec):
        """
        given: 给定的 MySQL 实例不存在
        when: 调用 start_mysql
        then: 执行 systemctl start mysqld-${port} 命令报异常
        """
        mock_assert.side_effect = MySQLSystemdFileNotExists()
        with self.assertRaises(MySQLSystemdFileNotExists):
            start_mysql(self.port)

        mock_assert.assert_called_once()
        mock_assert.assert_called_once_with(self.port)

        mock_exec.assert_not_called()
        # mock_exec.assert_called_once_with("systemctl start mysqld-3306")


# endregion start_mysql


# region stop_mysql
class StopMySQLTestCase(unittest.TestCase):
    """ """

    port = 3306

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_stop_mysql_given_instance_exists(self, mock_assert, mock_exec):
        """
        given: 给定的实例存在
        when: 调用 stop_mysql
        then: 执行 systemctl stop mysqld-${port} 命令
        """
        stop_mysql(self.port)

        mock_assert.assert_called_once()
        mock_assert.assert_called_once_with(self.port)

        mock_exec.assert_called_once()
        mock_exec.assert_called_once_with("systemctl stop mysqld-3306")

    @patch("dbma.components.mysql.install.exe_shell_cmd")
    @patch("dbma.components.mysql.install.assert_mysql_systemd_file_exists")
    def test_stop_mysql_given_instance_not_exists(self, mock_assert, mock_exec):
        """
        given: 给定的实例不存在
        when: 调用 stop_mysql
        then: 报异常
        """
        mock_assert.side_effect = MySQLSystemdFileNotExists()
        with self.assertRaises(MySQLSystemdFileNotExists):
            stop_mysql(self.port)

        mock_assert.assert_called_once()
        mock_assert.assert_called_once_with(self.port)

        mock_exec.assert_not_called()


# endregion stop_mysql
