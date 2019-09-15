
import socket
import unittest
import subprocess
import dbma.checkings as checkings


class CheckingsTeestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        super().setUp()
        # create a socket server
        self.ip = '127.0.0.1'
        self.port = 65321
        self.user = 'unittest'
        try:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.bind((self.ip,self.port))
            self.sock.listen(2)
        except Exception as err:
            pass
        # create a user
        subprocess.run(f"groupadd {self.user}",shell=True)
        subprocess.run(f"useradd -g {self.user} {self.user}",shell=True)



    def tearDown(self):
        super().tearDown()
        if self.sock and hasattr(self.sock,'close'):
            self.sock.close()
        subprocess.run(f"userdel {self.user}",shell=True)
            
    def test_01_is_port_in_use(self):
        self.assertTrue(checkings.is_port_in_use(self.ip,self.port))
    
    def test_02_is_user_exists(self):
        self.assertTrue(checkings.is_user_exists('unittest'))
