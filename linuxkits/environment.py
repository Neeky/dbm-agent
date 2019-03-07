"""处理 linux 环境变量相关的所有操作
"""
import os
import sys
import os.path
import logging
import argparse

if __name__ == "__main__":
    import existcode
    import logs
else:
    from . import existcode
    from . import logs

logs.log_config()

__ALL__ = ['edit_path_env',]

def edit_path_env(profile="/etc/profile",value="/usr/local/mysql/bin",action="insert"):
    """
    """
    logger = logging.getLogger('linux-kits').getChild('edit_path_env')
    logger.info("prepare edit '{0}' {1} {2} ".format(profile,action,value))
    if not os.path.exists(profile):
        # 如果要修改的文件不存在就报 existcode.FILE_NOT_EXIST
        logger.error("file '{0}' not exists \n".format(existcode.FILE_NOT_EXIST))
        logger.error("existcode {0} \n".format(existcode.FILE_NOT_EXIST))

    if not os.path.exists(value):
        # 如果要导出的 bin 目录不存在就报
        logger.error("director '{0}' not exists \n".format(existcode.DIRECTOR_NOT_EXIST))
        logger.error("existcode {0} \n".format(existcode.DIRECTOR_NOT_EXIST))

    if not action in ('insert','delete'):
        # 不支持的操作
        logger.error("not support operation '{0}' \n".format(action))
        logger.error("existcode {0} \n".format(existcode.NOT_SUPPORT_OPERATION))
    
    export_str = "export PATH={0}:$PATH\n".format(value.strip())

    # 读取 profile 文件中的所有行
    with open(profile) as f:
        lines = [line for line in f]

    try:
        if action == 'insert':
            # 进行插入环境变量逻辑、如果当前路径已经导出就不要再重复导出了
            if export_str not in lines:
                # insert 逻辑
                if '\n' not in lines[-1]:
                    # 如果当前的 profile 的最后一行没有 换行就给它加上换行
                    lines[-1] = lines[-1] + '\n'
                lines.append(export_str)
                with open(profile,'w') as f:
                    f.truncate(0)
                    f.writelines(lines)
        else:
            # 去看之前导出的 export 语句
            new_lines = [line for line in lines if line != export_str]
            with open(profile,'w') as f:
                f.truncate(0)
                f.writelines(new_lines)
    except Exception as err:
        logger.error("exception occur in 'edit_path_env' function . error detail : {0}".format(err))
    
    logger.info("edit '{0}' success ".format(profile))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--profile',default='/etc/profile',help='profile')
    parser.add_argument('--value',default='/usr/local/mysql/bin/',help='bin path')
    parser.add_argument('--action',default='insert',help='insert | delete')
    args=parser.parse_args()
    logger = logging.getLogger('linux-kits').getChild('edit_path_env')
    logger.info('command args: profile={args.profile} value={args.value} action={args.action}'.format(args=args))
    edit_path_env(args.profile,args.value,args.action)
