[toc]

## 概要
dbm-agent 支持两种使用模式，第一种是命令行模式，第二种是 http 接口模式。这个文档同时给出两者的使用方式，以下面这个一主一从的 MySQL 构架为例子。

|**主机**|**端口**|**角色**|**MySQL-版本**|
|--------|-------|--------|------------|
|127.0.0.1| 3306 | master | mysql-8.0.32|
|127.0.0.1| 3308 | slave | mysql-8.0.32|

`因为机器资源有限所以主从两个实例安装在了同一台机器。`

---

## 安装-MySQL-主结点
1. 命令行模式
   ```bash
   dbma-cli-mysql --port=3306 --ibps=128M --pkg=mysql-8.0.32-linux-glibc2.12-x86_64.tar.xz master
   ```
2. 检查
   ```bash
   mysql -uroot -pdbma@0352 -h127.0.0.1 -P3306
   mysql> show processlist;
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   | Id | User            | Host            | db   | Command | Time | State                  | Info             |
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   |  5 | event_scheduler | localhost       | NULL | Daemon  |   51 | Waiting on empty queue | NULL             |
   |  8 | root            | 127.0.0.1:38896 | NULL | Query   |    0 | init                   | show processlist |
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   2 rows in set (0.00 sec)
   
   mysql> select @@version;
   +-----------+
   | @@version |
   +-----------+
   | 8.0.32    |
   +-----------+
   1 row in set (0.00 sec)
   ```
---

## 安装-MySQL-从结点
1. 命令行模式
   ```bash
   dbma-cli-mysql --port=3308 --ibps=128M --pkg=mysql-8.0.32-linux-glibc2.12-x86_64.tar.xz --source=127.0.0.1:3306 replica
   ```
2. 检查
   ```bash
   mysql -uroot -pdbma@0352 -h127.0.0.1 -P3308
   mysql> show processlist;
   +----+-----------------+-----------------+------+---------+------+----------------------------------------------------------+------------------+
   | Id | User            | Host            | db   | Command | Time | State                                                    | Info             |
   +----+-----------------+-----------------+------+---------+------+----------------------------------------------------------+------------------+
   |  5 | event_scheduler | localhost       | NULL | Daemon  |   60 | Waiting on empty queue                                   | NULL             |
   | 10 | system user     | connecting host | NULL | Connect |   57 | Waiting for source to send event                         | NULL             |
   | 11 | system user     |                 | NULL | Query   |   57 | Replica has read all relay log; waiting for more updates | NULL             |
   | 12 | system user     |                 | NULL | Connect |   57 | Waiting for an event from Coordinator                    | NULL             |
   | 13 | system user     |                 | NULL | Connect |   57 | Waiting for an event from Coordinator                    | NULL             |
   | 14 | system user     |                 | NULL | Connect |   57 | Waiting for an event from Coordinator                    | NULL             |
   | 15 | system user     |                 | NULL | Connect |   57 | Waiting for an event from Coordinator                    | NULL             |
   | 16 | root            | 127.0.0.1:46338 | NULL | Query   |    0 | init                                                     | show processlist |
   +----+-----------------+-----------------+------+---------+------+----------------------------------------------------------+------------------+
   8 rows in set (0.00 sec)

   mysql> show slave status \G
   *************************** 1. row ***************************
                  Slave_IO_State: Waiting for source to send event
                     Master_Host: 127.0.0.1
                     Master_User: repl
                     Master_Port: 3306
                   Connect_Retry: 60
                 Master_Log_File: binlog.000002
             Read_Master_Log_Pos: 157
                  Relay_Log_File: relay-bin.000002
                   Relay_Log_Pos: 367
           Relay_Master_Log_File: binlog.000002
                Slave_IO_Running: Yes
               Slave_SQL_Running: Yes
   ```
---

## 卸载-MySQL
1. 卸载
   ```bash
   dbma-cli-mysql --port=3308 uninstall
   ```
---

## 安装-MySQL-主结点-http-模式
1. 安装
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
    --data '{"port":3306, "ibps":"128M", "pkg-name":"mysql-8.0.32-linux-glibc2.12-x86_64.tar.xz", "role":"source"}' \
    http://127.0.0.1:8086/apis/mysqls/install 2>/dev/null | jq
   
   {
     "message": "install mysql 'master|source' complete .",
     "error": "",
     "data": null
   }
   ```
2. 检查
   ```bash
   mysql> show processlist;
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   | Id | User            | Host            | db   | Command | Time | State                  | Info             |
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   |  5 | event_scheduler | localhost       | NULL | Daemon  |  287 | Waiting on empty queue | NULL             |
   |  9 | root            | 127.0.0.1:38640 | NULL | Query   |    0 | init                   | show processlist |
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   2 rows in set (0.00 sec)
   
   mysql> select @@version;
   +-----------+
   | @@version |
   +-----------+
   | 8.0.32    |
   +-----------+
   1 row in set (0.00 sec
   ```

---

## 安装-MySQL-从结点-http-模式
1. 安装
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
    --data '{"port":3308, "ibps":"128M", "pkg-name":"mysql-8.0.32-linux-glibc2.12-x86_64.tar.xz", "role":"replica", "source":"127.0.0.1:3306"}' \
    http://127.0.0.1:8086/apis/mysqls/install 2>/dev/null | jq
   
   {
     "message": "install mysql 'slave|replica' complete .",
     "error": "",
     "data": null
   }
   ```
2. 检查
   ```bash
   mysql> show processlist;
   +----+-----------------+-----------------+------+---------+------+----------------------------------------------------------+------------------+
   | Id | User            | Host            | db   | Command | Time | State                                                    | Info             |
   +----+-----------------+-----------------+------+---------+------+----------------------------------------------------------+------------------+
   |  5 | event_scheduler | localhost       | NULL | Daemon  |   84 | Waiting on empty queue                                   | NULL             |
   | 10 | system user     | connecting host | NULL | Connect |   83 | Waiting for source to send event                         | NULL             |
   | 11 | system user     |                 | NULL | Query   |   82 | Replica has read all relay log; waiting for more updates | NULL             |
   | 12 | system user     |                 | NULL | Connect |   83 | Waiting for an event from Coordinator                    | NULL             |
   | 13 | system user     |                 | NULL | Connect |   83 | Waiting for an event from Coordinator                    | NULL             |
   | 14 | system user     |                 | NULL | Connect |   83 | Waiting for an event from Coordinator                    | NULL             |
   | 15 | system user     |                 | NULL | Connect |   83 | Waiting for an event from Coordinator                    | NULL             |
   | 16 | root            | 127.0.0.1:49698 | NULL | Query   |    0 | init                                                     | show processlist |
   +----+-----------------+-----------------+------+---------+------+----------------------------------------------------------+------------------+
   8 rows in set (0.00 sec)
   
   mysql> show replica status \G
   *************************** 1. row ***************************
                Replica_IO_State: Waiting for source to send event
                     Source_Host: 127.0.0.1
                     Source_User: repl
                     Source_Port: 3306
                   Connect_Retry: 60
                 Source_Log_File: binlog.000002
             Read_Source_Log_Pos: 157
                  Relay_Log_File: relay-bin.000002
                   Relay_Log_Pos: 367
           Relay_Source_Log_File: binlog.000002
              Replica_IO_Running: Yes
             Replica_SQL_Running: Yes
   ```
---

## 卸载-MySQL-http-模式
1. 卸载
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
    --data '{"port":3308}' \
    http://127.0.0.1:8086/apis/mysqls/uninstall 2>/dev/null | jq
   
   {
     "message": "uninstall mysql complete .",
     "error": "",
     "data": null
   }
   ```
---