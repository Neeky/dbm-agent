import requests
from dbma.log import root_loger


class JobPuller(object):
    """
    """
    def __init__(self):
        #self.session = requests.Session()
        pass

    


class BaseState(object):
    """
    所有状态的基类
    每一个状态对应着一个特定的 Job
    """

    def change_state(self):
        raise NotImplementedError("BaseState.change_state 是一个抽象方法请在子类中实现")