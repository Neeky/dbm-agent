from dbma.version import agent_version
import re
import unittest


class VersionTestCase(unittest.TestCase):
    """
    验证 version 模块中的 agent_vesion 格式上是否正确
    """
    @unittest.skip
    def test_01_version(self):
        self.assertIsInstance(agent_version, str)

        m = re.search(r'\d.\d.\d', agent_version)
        self.assertIsNotNone(m)
