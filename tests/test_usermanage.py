import unittest
import logging

from dbma.usermanage import LinuxUsers as lus

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s")


class TestLinuxUsersTestCase(unittest.TestCase):

    group_name = "group001"
    user_name = "user001"

    def test_01_is_group_exists(self):
        self.assertFalse(lus.is_user_exists(self.user_name))

    def test_02_is_group_exists(self):
        self.assertFalse(lus.is_group_exists(self.group_name))

    def test_03_create_group(self):
        lus.create_group(self.group_name)
        self.assertTrue(lus.is_group_exists(self.group_name))

    def test_04_create_user(self):
        lus.create_user(self.user_name, self.group_name)
        self.assertTrue(lus.is_user_exists(self.user_name))

    def test_05_drop_user(self):
        self.assertTrue(lus.is_user_exists(self.user_name))
        lus.delete_user(self.user_name)
        self.assertFalse(lus.is_user_exists(self.user_name))
        self.assertTrue(lus.is_group_exists(self.group_name))

    def test_06_drop_group(self):
        self.assertTrue(lus.is_group_exists(self.group_name))
        lus.drop_group(self.group_name)
        self.assertFalse(lus.is_group_exists(self.group_name))

    def test_07_uid(self):
        self.assertEqual(lus.gid('root'), 0)

    def test_08_uid(self):
        self.assertEqual(lus.uid('root'), 0)

    @classmethod
    def tearDownClass(cls):
        lus.drop_user(cls.user_name)
        lus.drop_group(cls.group_name)


if __name__ == "__main__":
    unittest.main()
