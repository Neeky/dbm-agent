## 卸载
当要求 dbm-agent 支持卸载 MySQL 服务的时候，它会把关闭服务、备份 binlog 目录、备份 datadir 目录，现在用一个例子给大家介绍一下卸载操作。

1、卸载前我们测试机器上有 3308、3309 两个 master 。
```bash

ps -ef | grep mysql
mysql33+     802       1  0 Jun15 ?        00:16:19 /usr/local/mysql-8.0.33-linux-glibc2.28-x86_64/bin/mysqld --defaults-file=/etc/my-3309.cnf
mysql33+  712456       1  0 Jun17 ?        00:10:14 /usr/local/mysql-8.0.33-linux-glibc2.28-x86_64/bin/mysqld --defaults-file=/etc/my-3308.cnf

ll /database/mysql/data/
drwxr-xr-x 7 mysql3308 mysql 4096 Jun 17 23:26 3308
drwxr-xr-x 7 mysql3309 mysql 4096 Jun 15 22:36 3309
```

2、执行卸载操作,卸载对于 dbm-agent 来说也是一行命令解决
```bash
dbma-cli-mysql --port=3309 uninstall

[2023-06-21 17:37:01,420 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 598 line]  ~  starts uninstall_mysql .
[2023-06-21 17:37:01,420 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 267 line]  ~  starts stop_mysql .
[2023-06-21 17:37:01,420 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 275 line]  ~  excute cmd 'systemctl stop mysqld-3309' .
[2023-06-21 17:37:02,345 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 280 line]  ~  ends stop_mysql .
[2023-06-21 17:37:02,345 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 200 line]  ~  starts disable_systemd_for_mysql .
[2023-06-21 17:37:02,346 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 208 line]  ~  excute cmd 'systemctl disable mysqld-3309' .
[2023-06-21 17:37:02,503 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 214 line]  ~  ends disable_systemd_for_mysql .
[2023-06-21 17:37:02,504 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 375 line]  ~  starts backup_config_file .
[2023-06-21 17:37:02,504 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 387 line]  ~  move '/etc/my-3309.cnf' to '/database/mysql/data/3309/my-3309.cnf-backup-2023-06-21T17-37-02-504613' 
[2023-06-21 17:37:02,505 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 393 line]  ~  ends backup_config_file .
[2023-06-21 17:37:02,506 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 341 line]  ~  starts backup_dirs .
[2023-06-21 17:37:02,506 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 357 line]  ~  ends backup_dirs .
[2023-06-21 17:37:02,507 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/components/mysql/install.py 611 line]  ~  ends uninstall_mysql .
```

3、卸载后的检查
```sql
ps -ef | grep mysql
mysql33+  712456       1  0 Jun17 ?        00:10:14 /usr/local/mysql-8.0.33-linux-glibc2.28-x86_64/bin/mysqld --defaults-file=/etc/my-3308.cnf

ll /database/mysql/data/
drwxr-xr-x 7 mysql3308 mysql 4096 Jun 17 23:26 3308
drwxr-xr-x 7 mysql3309 mysql 4096 Jun 21 17:37 3309-backup-2023-06-21T17-37-02-506331
```
默认情况下生成的 backup 文件 `3309-backup-2023-06-21T17-37-02-506331`， dbm-agent 会为你保留 3 天，3 天过后后台线程会去慢慢的清理它(一次最多清理 16MB)。

---

4、这个功能也支持 http 接口
```bash
curl  --request POST --header "Content-type:application/json;charset=utf-8" \
 --data '{"port":3309}' \
 http://127.0.0.1:8086/apis/mysqls/uninstall 2>/dev/null | jq

{
  "message": "uninstall mysql complete .",
  "error": "",
  "data": null
}
```
---