#!/usr/bin/evn python3
# -*- coding: utf8 -*-

"""
(c) 2019, LeXing Jinag <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
Copyright: (c) 2019, dbm Project
GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""


import argparse
from dbma.core.httpserver import start, stop
from dbma.version import DBM_AGENT_VESION


def parser_cmd_args():
    parser = argparse.ArgumentParser(
        f"dbma-agent {DBM_AGENT_VESION}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "action",
        type=str,
        default="start",
        choices=("start", "stop", "version"),
        help="",
    )
    args = parser.parse_args()
    return args


def main():
    args = parser_cmd_args()
    if args.action == "start":
        start()
    elif args.action == "version":
        print(f"dbma-agent {DBM_AGENT_VESION}")
    elif args.action == "stop":
        stop()


if __name__ == "__main__":
    main()
