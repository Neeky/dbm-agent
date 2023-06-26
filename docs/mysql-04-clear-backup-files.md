## 清理动作是自动的
当你对一个实例调用 uninstall 之后，它的 datadir 会被 rename 成如下的形式
```bash
/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128
```
我们称上面这个目录为“清理目录”，默认情况下我们会保留清理目录 3 天，3 天之后会进入过期状态；后台有专门的线程去清理过期目录。
```
[2023-06-21 14:16:15,149 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 115 line]  ~  starts clear_instance .
[2023-06-21 14:16:15,150 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 116 line]  ~  task.path = '/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128/#innodb_redo'  is_expire = 'True' 
[2023-06-21 14:17:17,177 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 132 line]  ~  deal-with file '/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128/#innodb_redo/#ib_redo3_tmp' 
[2023-06-21 14:17:18,177 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 143 line]  ~  file '/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128/#innodb_redo/#ib_redo3_tmp' truncated 
[2023-06-21 14:17:19,177 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 140 line]  ~  file '/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128/#innodb_redo/#ib_redo3_tmp' removed 
[2023-06-21 14:17:19,178 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 157 line]  ~  sub directorys not exists, rm current directory '/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128/#innodb_redo' 
[2023-06-21 14:17:19,179 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 162 line]  ~  ends clear_instance .
[2023-06-21 14:17:19,179 INFO] - [backends_2] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/backends/clears.py 157 line]  ~  sub directorys not exists, rm current directory '/database/mysql/data/3308-backup-2023-05-29T20-23-32-472128'
```
后台的清理是温和的，也就是说对于大于 16MB 的文件一次截断 16MB，对于小于 16MB 的文件才会直接删除。

---