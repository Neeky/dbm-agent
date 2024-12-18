#!/usr/bin/evn python3
# -*- coding: utf8 -*-

"""
完成 dbm-agent 的初始化操作
"""

import argparse
from dbmagent.bil.net import get_ip_by_card_name
from dbmagent.core.agent.init import init


def parser_cmd_args():
    """ """
    parser = argparse.ArgumentParser(
        "dbma-cli-init", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--net-card", default=None)
    parser.add_argument("--dbm-center-url-prefix", default="http://127.0.0.1:8080")
    return parser.parse_args()


def main():
    args = parser_cmd_args()
    ip = get_ip_by_card_name(args.net_card)
    print("net-card {}'s ip = {}".format(args.net_card, ip))
    if ip is None:
        print("not find any ip on {}".format(args.net_card))
        return
    print("going to init ...")
    init(args.net_card, args.dbm_center_url_prefix)


if __name__ == "__main__":
    main()
