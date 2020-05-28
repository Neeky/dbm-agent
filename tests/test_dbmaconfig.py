import logging
import unittest


from dbma.dbmaconfig import ConfigMixin

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s")

class TestConfigMixinTestCase(unittest.TestCase)
