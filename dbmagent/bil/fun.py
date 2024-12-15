# -*- coding: utf-8 -*-

"""Python 函数相关的帮助函数

作者: 蒋乐兴|neeky@live.com
时间: 2023-03
"""


import inspect


def fname():
    """返回当前函数的函数名"""
    return inspect.stack()[1][3]
