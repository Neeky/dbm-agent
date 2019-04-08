import os
import os.path
import sys
import pwd
import subprocess
import contextlib

@contextlib.contextmanager
def sudo(message="sudo"):
    """提升当前进程的权限到 root 以完成特定的操作，操作完成后再恢复权限
    """
    # 得到当前进程的 euid 
    old_euid = os.geteuid()
    # 提升权限到 root
    os.seteuid(0)
    yield message
    # 恢复到普通权限
    os.seteuid(old_euid)


class OSOperator(object):
    """封装所有的操作系统操作
    """
    @staticmethod
    def is_user_exists(user_name='dbma'):
        """检测给定的用户在当前操作系统中是否存在
        """
        user_exists = True
        try:
            pwd.getpwnam(user_name)
        except KeyError :
            # 如果是 KeyError 的话说明 dbma 用户并不存在
            user_exists = False

        return user_exists

    @staticmethod
    def get_uid(user_name='dbma'):
        """给析给定用户名的 uid 、如果用名不存在就返回 None，不然返回 uid
        """
        if OSOperator.is_user_exists(user_name):
            return None
        else:
            return pwd.getpwnam(user_name).pw_uid

    @staticmethod
    def create_user(user_name,user_id):
        """创建操作系统级别的用户
        """
        with sudo():
            cmd = "useradd -u{0} {1}".format(user_id,user_name)
            subprocess.call(cmd,shell=True)

    @staticmethod
    def drop_user(user_name):
        """删除操作系统级别的用户(存在就删除，不存在就不管了)
        """
        if OSOperator.is_user_exists(user_name):
            with sudo():
                cmd = "userdel -r {0}".format(user_name)
                subprocess.call(cmd,shell=True)

    @staticmethod
    def edit_profile(profile_path='/etc/profile',name='PATH',value='/usr/local/mysql/bin',action='insert'):
        if any((profile_path,name,value,action)):
            raise ValueError("edit_profile function error arguments must not be None or blank")
        
        if not os.path.exists(profile_path):
            raise ValueError("file '{0}' not exists ".format(profile_path))
        
        if not os.path.isfile(profile_path):
            raise ValueError("'{0}' must be a file".format(profile_path))

        if action not in ('insert','delete'):
            raise ValueError("action must be 'insert' or 'delete' ")

        with sudo():
            with open(profile_path) as f1:
                lines = [ line for line in f1]
            export_str = "export PATH={0}:$PATH\n".format(value)
            if action == 'insert':
                # 如果是要插入新的环境亦是，在有的情况下可以跳过插入逻辑
                for line in lines:
                    if export_str == line:
                        break
                else:
                    # 没有进入 break 逻辑说明没有找到，那么要插入
                    if not lines[-1].endswith('\n'):
                        lines[-1] = lines[-1] + '\n' #如果最后一行没有就给它加上换行
                    lines.append(export_str) # 加入新的导出语句

                with open(profile_path,'w') as f2:
                    f2.writelines(lines)     # 写入新的 export 语句
            else:
                # 说明 action == delete
                with open(profile_path) as f1:
                    lines = [line for line in f1 if line != export_str]
                with open(profile_path,'w') as f2:
                    f2.writelines(lines)

    @staticmethod
    def reload_so():
        """从新加载一次 so 文件
        """
        with sudo():
            cmd="ldconfig"
            subprocess.call(cmd,shell=True)

    @staticmethod
    def edit_head_file(source_dir="/usr/local/mysqlmysql-8.0.14-linux-glibc2.12-x86_64/include",target_link_file="/usr/include/mysql-8.0.14-linux-glibc2.12-x86_64",action='insert'):
        """导出 C 语言的 .h 文件
        """
        with sudo():
            if action == 'insert':
                os.symlink(source_dir,target_link_file)
            elif action == 'delete':
                os.remove(target_link_file)






                    
                    
                
            




            
                
            
    
