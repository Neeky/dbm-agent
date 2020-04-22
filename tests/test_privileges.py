import os
import logging
import unittest

from dbma.privileges import sudo, chown
from dbma.usermanage import LinuxUsers as lus

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s")


class TestPrivilegesTestCase(unittest.TestCase):
    """
    """
    user_name = "mysql"
    test_file = "/tmp/test-file.log"

    def test_01_sudo(self):
        """
        """
        with sudo("test sudo"):
            self.assertEqual(os.geteuid(), 0)

    def test_02_chown(self):
        """
        """
        lus.create_user(self.user_name)
        self.assertTrue(lus.is_user_exists(self.user_name))

        with open(self.test_file, 'w') as f:
            f.write("test")
        group_name = self.user_name
        chown(self.test_file, self.user_name, group_name)

        uid = lus.uid(self.user_name)
        fuid = os.stat(self.test_file).st_uid
        self.assertEqual(uid, fuid)

        os.remove(self.test_file)
