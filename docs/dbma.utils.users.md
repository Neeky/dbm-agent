## 目录
[dbma.utils.users.py模块文档](#dbma.utils.users.py模块文档)
 - [users.is_user_exists函数](#users.is_user_exists函数)
 - [users.is_group_exists函数](#users.is_group_exists函数)
 - [users.get_uid_gid函数](#users.get_uid_gid函数)
 - [users.sudo函数](#users.sudo函数)
---

## dbma.utils.users.py模块文档
   **这个模块的主要目标是封装与操作系统用户相关的功能**

   ---

## users.is_user_exists函数
   **1、** 测试给定的用户是否存在

   **2、** 原型
   ```python
   def is_user_exists(user_name:str) -> bool:
   ```

   ---

## users.is_group_exists函数
   **1、** 测试给定的用户组是否存在

   **2、** 原型
   ```python
   def is_group_exists(group_name:str) -> bool:
   ```

   ---

## users.get_uid_gid函数
   **1、** 返回给定用户的 uid 值
   
   **2、** 原型
   ```python
   def get_uid_gid(user_name:str) -> int:
   ```
---

## users.sudo函数
   **1、** 类似于 linux 上的 sudo 命令，让上下方内的代码以 root 权限运行

   **2、** 原型
   ```python
   @contextlib.contextmanager
   def sudo(message="sudo"):
       """# sudo 上下文
       提升当前进程的权限到 root 以完成特定的操作，操作完成后再恢复权限
       """
       lg = logging.getLogger('dbma').getChild('utils.users')
       lg.warning(message)
       # 得到当前进程的 euid 
       old_euid = os.geteuid()
       # 提升权限到 root
       os.seteuid(0)
       yield message
       # 恢复到普通权限
       os.seteuid(old_euid)
       lg.warning('exits from root mode')
   ```
   可以看到 sudo 是一个上下文管理器，当退出上下文后，root 权限自然就没有了







