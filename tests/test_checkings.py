
import os
import socket
import unittest
import subprocess
import dbma.checkings as checkings
from datetime import datetime


class CheckingsTeestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        super().setUp()
        # create a socket server
        self.ip = '127.0.0.1'
        self.port = 65321
        self.user = 'unittest'
        self.now = datetime.now().isoformat()
        self.t_file = f"/tmp/unittest-{self.now}"
        try:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.bind((self.ip,self.port))
            self.sock.listen(2)
        except Exception as err:
            pass
        # create a user
        subprocess.run(f"groupadd {self.user}",shell=True)
        subprocess.run(f"useradd -g {self.user} {self.user}",shell=True)

        with open(self.t_file,'w') as fd:
            fd.write('unittest.')


    def tearDown(self):
        super().tearDown()
        if self.sock and hasattr(self.sock,'close'):
            self.sock.close()
        subprocess.run(f"userdel {self.user}",shell=True)
        os.remove(self.t_file)

    def test_01_is_port_in_use(self):
        self.assertTrue(checkings.is_port_in_use(self.ip,self.port))
    
    def test_02_is_user_exists(self):
        self.assertTrue(checkings.is_user_exists('unittest'))
    
    def test_03_is_file_exists(self):
        self.assertTrue(checkings.is_file_exists(self.t_file))
    
    def test_04_is_group_exists(self):
        self.assertTrue(checkings.is_group_exists('unittest'))
    
    def test_05_is_directory_exists(self):
        self.assertTrue(checkings.is_directory_exists('/tmp/'))
    
    def test_06_is_an_supported_mysql_version(self):
        self.assertTrue(checkings.is_an_supported_mysql_version('mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz'))
        self.assertFalse(checkings.is_an_supported_mysql_version('mysql-8.0.16-linux-glibc2.12-x86_64.tar.xz'))
        self.assertFalse(checkings.is_an_supported_mysql_version('mysql-5.7.26-linux-glibc2.12-x86_64.tar.gz'))
    

    
    
