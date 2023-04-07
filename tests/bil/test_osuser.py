# -*- coding: utf8 -*-

"""
测试 fun.py 模块
"""

import os
import pwd
from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from dbma.bil import osuser
from dbma.bil.osuser import is_root

# region is_root
def test_is_root_given_normal_user_then_return_false(monkeypatch: MonkeyPatch):
    """
    """
    def mock_geteuid():
        print("mock func geteuid -> 1024")
        return 1024
    
    monkeypatch.setattr(os, "geteuid", mock_geteuid)
    x = is_root()
    assert x == False
    
def test_is_root_given_root_user_then_return_true(monkeypatch: MonkeyPatch):
    """
    """
    def mock_geteuid():
        print("mock func geteuid -> 1")
        return 0
    
    monkeypatch.setattr(os, "geteuid", mock_geteuid)
    x = is_root()
    assert x == True

# endregion is_root

# region is_user_exists
def test_is_user_exists_given_user_not_exists_then_return_false(monkeypatch: MonkeyPatch):
    def getpwnam(user:str):
        raise KeyError("name not found: '{}'".format(user))
    
    monkeypatch.setattr(pwd, "getpwnam", getpwnam)
    result = osuser.is_user_exists("not-exists-user")
    assert result == False
    
def test_is_user_exists_given_user_exists_then_return_false(monkeypatch: MonkeyPatch):
    def getpwnam(user:str):
        pass
    
    monkeypatch.setattr(pwd, "getpwnam", getpwnam)
    result = osuser.is_user_exists("not-exists-user")
    assert result == True

def test_is_user_exists_given_error_args_then_return_false(mocker: MockerFixture):
    mocker.patch("pwd.getpwnam")
    osuser.is_user_exists(None)
    pwd.getpwnam.assert_called_once()

    
# endregion is_user_exists

## region is_group_exists

def test_is_group_exists_given_group_not_exists_then_return_false(mocker: MockerFixture):
    import grp
    mocker.patch("grp.getgrnam", return_value="hello world")
    expect = "hello world"
    resutl = grp.getgrnam("j")
    assert resutl == expect
    

## endregion is_group_exists