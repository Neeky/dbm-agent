# -*- coding: utf8 -*-

"""测试 bil.net 模块
"""

from socket import AddressFamily
from collections import namedtuple
from pytest_mock import MockerFixture
from dbma.bil import net

NetCard = namedtuple("NetCard", "family address")


eths = {
    "lo": [NetCard(AddressFamily.AF_INET, "127.0.0.1")],
    "eth0": [NetCard(AddressFamily.AF_INET, "192.168.1.100")],
}


def test_get_ip_by_card_name_give_card_name_exists_then_retun_is_ip(
    mocker: MockerFixture,
):
    """ """
    expect = "192.168.1.100"
    mocker.patch("psutil.net_if_addrs", return_value=eths)
    ip = net.get_ip_by_card_name("eth0")
    assert ip == expect


def test_get_ip_by_card_name_give_card_name_not_exists_then_raise_value_error(
    mocker: MockerFixture,
):
    card_name = "eth8848"
    expect = None
    mocker.patch("psutil.net_if_addrs", return_value=eths)

    ip = net.get_ip_by_card_name(card_name)
    assert ip == expect
