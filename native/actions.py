from .osops import sudo,OSOperator
import subprocess

class AgentInit(object):
    """用于完成 dbma-agent 初始化工作
    """
    def create_user(self,user_name='dbma',user_id='2233'):
        """创建用于运行 dbm-agent 的用户
        """
        OSOperator.create_user(user_name,user_id)

    def drop_user(self,user_name='dbma'):
        """删除指定的用户
        """
        OSOperator.drop_user(user_name)
            

        
