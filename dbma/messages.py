"""
定义若干常量
"""
# (c) 2019, LeXing Jiang <neeky@live.com 1721900707@qq.com https://www.sqlpy.com/>
# Copyright: (c) 2019, dbm Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# -- 用户相关 --

# 用户不存在
SYS_USER_NOT_EXISTS = f"system user '{0}' not exists"

# 用户已经存在
SYS_USER_ALREADY_EXISTS = f"system user '{0}' alread exists"

# 当前的时候是多少
CURRENT_DATETIME = f"current datetime is '{0}'"

# 备份集的路径是

BACKUPSETS_DIRECTORY = f"backup sets directory is '{0}' "

# 未实现的方法
NOTIMPLEMENTEDFUNCTION = f"function '{0}' shuld been implemented in sub class"

#
READ_CONFIG_OPTION_FROM_FILE = f"read config opstion from '{0}' "

# 使用 xxx 作为备份工具
USING_XX_AS_BACKUP_TOOL = f"using {0} as backup tools"
GET_BACKUP_TOOL_ECURE_ERROR = f"get backup tool trigger an exception {0}"
DURING_BACKUP_GET_EXCEPTION = f"during backup got this exception {0}"
