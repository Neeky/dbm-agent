# -*- coding: utf8 -*-

"""
测试 fun.py 模块
"""

from pytest_mock import MockerFixture
from dbma.bil.fun import fname

def test_fname(mocker: MockerFixture):
    def hello():
        name = fname()
        return name
    
    name = hello()
    assert name == "hello"
    