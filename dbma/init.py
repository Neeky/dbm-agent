"""
用于完成 dbm-agent 的初始化
1、创建 dbmc linux 用户
2、创建 /usr/local/dbm-agent/目录和它的子目录
3、修改 /usr/local/dbm-agent/目录的权限为chomd -R dbma:dbma /usr/local/dbm-agent
"""
import os
import uuid
from dbma.utils import users,directors

def init_dbma(args):
    """
    1、创建用户 dbma
    2、创建目录树 /usr/local/dbm-agent/{etc,logs,pkgs}
    """
    # 创建 dbma 用户
    users.create_user_if_not_exists(user_name=args.user,uid=2048,gid=2048,group_name='dbm')
    # 创建目录
    directors.create_dbm_agent_directorys(args.basedir)
    uid,gid = users.get_uid_gid(args.user)
    os.setegid(gid)
    os.seteuid(uid)
    init_dbma_cnf_config_file(args)


def init_dbma_cnf_config_file(args):
    """
    用于创建一份初始化配置文件
    """
    dbma_cnf = f"""
[dbma]
dbmc_site          = {args.dbmc_site}       #     web 管理端的地址
dbma_uuid          = {uuid.uuid1()}   #     dbmauuid 为每一个dbm-agent 分配一个唯一的 id 用来标识它
log_file           = {args.log_file}
"""
    if not os.path.exists(args.config_file):
        with open(args.config_file,'w') as config_file_obj:
            config_file_obj.write(dbma_cnf)
 


    


    