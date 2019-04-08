"""
针对参数进行处理
1、命令行参数优先于配置文件
2、支持持久化参数，持久化参数优先与配置文件
"""
import argparse
import json

__version = '0.0.0.1'

def get_config_from_json(config_file_path="./etc/dbma.json"):
    """json 文件中读取配置,失败就返回 None
    """
    with open(config_file_path,'r') as config_file_obj:
        s = config_file_obj.read()
        return json.loads(s)
    return None

def get_config_from_cmd():
    parser = argparse.ArgumentParser('dbmc-agent ' + __version)
    parser.add_argument('--basedir',default='/usr/local/dbm-agent/',help='dbm-agent work dir')
    parser.add_argument('--config-file',default='./etc/dbmc.json',help='dbm-agent config file path')
    parser.add_argument('--log-file',default='./logs/dbma.log',help='dbm-agent log file')
    parser.add_argument('action',default='start',choices=('start','stop','init'),help='actions')
    args = parser.parse_args()
    return args
    




