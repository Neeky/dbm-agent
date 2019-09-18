

import unittest
import dbma.common as common
import dbma.checkings as checkings
from datetime import datetime

class CommonTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        super().setUp()
        self.t_user = 'cttu'
        self.t_group = 'ctt'
        self.now = datetime.now().isoformat()
        self.t_dir = f'/tmp/{self.now}'


    def test_01_create_group(self):
        # 
        self.assertFalse(checkings.is_group_exists(self.t_group))
        common.create_group(self.t_group)
        self.assertTrue(checkings.is_group_exists(self.t_group))

    def test_02_create_user(self):
        self.assertFalse(checkings.is_user_exists(self.t_user))
        common.create_user(self.t_user)
        self.assertTrue(checkings.is_user_exists(self.t_user))
    
    def test_03_create_direcotry(self):
        self.assertFalse(checkings.is_directory_exists(self.t_dir))
        common.create_directory(self.t_dir)
        self.assertTrue(checkings.is_directory_exists(self.t_dir))

    def test_04_delete_user(self):
        self.assertTrue(checkings.is_user_exists(self.t_user))
        common.delete_user(self.t_user)
        self.assertFalse(checkings.is_user_exists(self.t_user))