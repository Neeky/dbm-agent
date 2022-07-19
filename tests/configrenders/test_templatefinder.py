# -*- encoding: utf8 -*-


import unittest
from unittest.mock import MagicMock, Mock

import jinja2
from dbma.installsoftwares.configrenders.templatefinders import ZookeeperTemplateFileFinder


class ZookeeperTemplateFileFinderTestCase(unittest.TestCase):
    """
    """
    def test_find_given_template_file_exists_when_call_find_then_return_the_content(self):
        """
        """
        template_finder = ZookeeperTemplateFileFinder()
        self.assertIn("data_dir", template_finder.load())
