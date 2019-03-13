import unittest
import pwd
import os
from native.osops import sudo,OSOperator
from native.actions import AgentInit

class AgentInitTestCase(unittest.TestCase):
    """针对 AgentInit 的相关功能进行测试
    """
    def setUp(self):
        agent_initor = AgentInit()
        self.agent_initor = agent_initor

    def tearDown(self):
        """
        """
        if OSOperator.is_user_exists('dbma'):
            self.agent_initor.drop_user('dbma')

    
    def test_create_user(self):
        """
        """
        self.agent_initor.create_user('dbma',2233)
        self.assertEqual(pwd.getpwnam('dbma').pw_uid,2233)

    def test_drop_user(self):
        """
        """
        self.agent_initor.drop_user('dbma')
        self.assertEqual(OSOperator.is_user_exists('dbma'),False)


            
    
