
import os
import socket
import unittest
import subprocess
import dbma.checkings as checkings
from datetime import datetime


class CheckingsTeestCase(unittest.TestCase):
    """
    """
    @classmethod
    def setUpClass(cls):
        """
        Sets up the class

        Args:
            cls: (todo): write your description
        """
        super().setUpClass()
        # create a socket server
        cls.ip = '127.0.0.1'
        cls.port = 65321
        cls.user = 'unittest'
        cls.now = datetime.now().isoformat()
        cls.t_file = f"/tmp/unittest-{cls.now}"
        try:
            cls.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            cls.sock.bind((cls.ip,cls.port))
            cls.sock.listen(2)
        except Exception :
            pass
        # create a user
        subprocess.run(f"groupadd {cls.user}",shell=True)
        subprocess.run(f"useradd -g {cls.user} {cls.user}",shell=True)

        with open(cls.t_file,'w') as fd:
            fd.write('unittest.')

    @classmethod
    def tearDownClass(cls):
        """
        Closes the subprocessor.

        Args:
            cls: (todo): write your description
        """
        super().tearDownClass()
        if cls.sock and hasattr(cls.sock,'close'):
            cls.sock.close()
        subprocess.run(f"userdel {cls.user}",shell=True)
        os.remove(cls.t_file)

    def test_01_is_port_in_use(self):
        """
        Check if the port is in a port.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(checkings.is_port_in_use(self.ip,self.port))
    
    def test_02_is_user_exists(self):
        """
        Check if the user exists.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(checkings.is_user_exists('unittest'))
    
    def test_03_is_file_exists(self):
        """
        Check if a file exists.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(checkings.is_file_exists(self.t_file))
    
    def test_04_is_group_exists(self):
        """
        Returns true if the group exists.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(checkings.is_group_exists('unittest'))
    
    def test_05_is_directory_exists(self):
        """
        Check if a directory exists.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(checkings.is_directory_exists('/tmp/'))
    
    def test_06_is_an_supported_mysql_version(self):
        """
        Check if the supported supported version is supported.

        Args:
            self: (todo): write your description
        """
        self.assertTrue(checkings.is_an_supported_mysql_version('mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz'))
        self.assertFalse(checkings.is_an_supported_mysql_version('mysql-8.0.16-linux-glibc2.12-x86_64.tar.xz'))
        self.assertFalse(checkings.is_an_supported_mysql_version('mysql-5.7.26-linux-glibc2.12-x86_64.tar.gz'))

    def test_07_is_local_ip(self):
        """
        """
        self.assertTrue(checkings.is_local_ip('127.0.0.1'))
        self.assertFalse(checkings.is_local_ip('127.0.0.1111'))

    def test_08_is_template_file_exists(self):
        """
        检查安装包中是否包涵配置文件模板
        """
        project_dir = os.path.dirname(os.path.dirname(__file__))

        # 查询 mysql-8.0.17 的配置文件版本要在
        cnf_tmpl_file_17 = os.path.join(project_dir,'dbma/static/cnfs/','mysql-8.0.17.cnf.jinja')
        self.assertTrue(os.path.isfile(cnf_tmpl_file_17))
        # 查询 mysql-8.0.18 的配置文件版本要在
        cnf_tmpl_file_18 = os.path.join(project_dir,'dbma/static/cnfs/','mysql-8.0.17.cnf.jinja')
        self.assertTrue(os.path.isfile(cnf_tmpl_file_18))

        # init 专用的配置文件模板存在
        cnf_tmpl_init_only = os.path.join(project_dir,'dbma/static/cnfs/','mysql-8.0-init-only.jinja')
        self.assertTrue(os.path.isfile(cnf_tmpl_init_only))



        
    

    
    
