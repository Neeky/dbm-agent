# -*- coding: utf8 -*-

"""
实现网络相关的能用功能
"""

import psutil
from socket import AddressFamily


def get_ip_by_card_name(name: str):
    """根据给定的网卡名返回对应的 IP 地址，如果网卡名不存在就返回 None

    Paramater:
    ----------
    name: str
        网卡名

    Return
    ------
        str IP 地址(ipv4)
    """
    eths = psutil.net_if_addrs()
    if not name in eths:
        return None

    # 执行到这里说明网卡名存在
    addres = eths.get(name)
    for addr in addres:
        if addr.family == AddressFamily.AF_INET:
            return addr.address

    raise ValueError("net card {} not bind with any ip .".format(name))
