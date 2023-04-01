## 目录
---
- [目录](#目录)
- [dbm](#dbm)
- [安装与配置](#安装与配置)
- [检查给定的MySQL是否存在](#检查给定的mysql是否存在)
- [自动化安装MySQL](#自动化安装mysql)
- [自动化卸载MySQL](#自动化卸载mysql)
- [关闭dbm-agent](#关闭dbm-agent)
- [规范](#规范)
- [源码依赖](#源码依赖)
- [官方微信公众平台](#官方微信公众平台)


---

## dbm
  dbm 是一个软件套件，包含有 dbm-center 和 dbm-agent 两大组成部分；其中 dbm-center 可以看成一个 web 站点，DBA 通过它可以查看监控、告警、部署各种 MySQL|Redis 环境。
  dbm-agent 是 dbm-center 的助手，负责环境的部署、监控的采集与上报、数据库的备份与监控。总的来讲接活的 dbm-center 真正干活的是 dbm-agent。另外 dbm-agent 也集成了若干命令行工具，这使得它也可以单独使用。
  
  ![dbm](imgs/dbm.png)

  **愿景**

  我们希望 DBA 可以从日常的工作中解放出来，做到只要在 web 界面上点一下“同意”系统就能自动、高效、优质的完成所有的操作；同样对于那些我们认为不合理的需求只要点一个“驳回”系统除了向需求方回一个被驳回的响应之外什么都不会干，安静的像一个美男子；更有意思的事，对于所有能用自动化解决的问题，dbm 绝对不会大半夜打 dba 的电话，出现故障自动解决，完成之后记录一下日志就行。

  **工作原理**

  dbm-agent 是安装在你机器上的一个 python 程序，它可以工作在两个模式
  
  一：**守护进程模式** 这个模下我们可以先 dbm-agent 发送 http 请求来要求它完成相应的动作，另外后台线程也会定时上报一些监控信息到管理中心。

  二：**命令行模式** dbm-agent 除了以 http 方式来暴露功能外，还提供了相应的命令工具，真正做来最小化依赖拿来就用。

  ---


## 安装与配置
   **1. 安装 dbm-agent**
   ```bash
   pip3 install dbm-agent
   ```
   如果你是在国内，推荐使用腾讯云的源对 pip 安装进行加速，配置也非常简单一行命令搞定
   ```bash
   pip3 config set global.index-url  https://mirrors.cloud.tencent.com/pypi/simple
   ```
   ---
   **2. 初始化**
   ```bash
   sudo su

   dbma-cli-init --net-card=eth0 --dbm-center-url-prefix=https://127.0.0.1

   # 检查有没有 init 成功
   tree /usr/local/dbm-agent/
   /usr/local/dbm-agent/
   ├── etc
   │   ├── dbm-agent.json
   │   └── templates
   │       ├── mysql-8.0.30.cnf.jinja
   │       ├── mysql-8.0.31.cnf.jinja
   │       ├── mysql-8.0-init-only.jinja
   │       ├── mysqld.service.jinja
   ├── logs
   └── pkgs
       └── mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz
   ```
   **3. 启动** 不执行启动的话就用不了 http 接口，只能使用命令行工具。
   ```bash
   dbm-agent start
   ```
   **4. 检查** dbm-agent 进程在不在
   ```bash
   ps -ef | grep dbm-agent
   dbma        3520       1  0 16:02 ?        00:00:00 /usr/local/python/bin/python3.11 /usr/local/python/bin/dbm-agent start
   root        3556    3273  0 16:02 pts/4    00:00:00 grep --color=auto dbm-agent
   ```
   **5. 检查** http 服务是否正常
   ```bash
   curl http://127.0.0.1:8086/apis/dbm-agent 2>/dev/null | jq
   {
     "name": "dbm-agent",
     "version": "8.31.9"
   }
   ```
   ---

## 检查给定的MySQL是否存在
   体验一下 dbm-agent 自带的 http 接口的方便，以前我们要确认给定机器上有没有安装在 3306 这个端口上的实例，我们还要上机器。现在我们直接请求一下接口就行了。
   ```bash
   curl http://localhost:8086/apis/mysqls/3306/exists 2>/dev/null | jq

   {
     "message": "",
     "error": null,
     "data": {
       "exists": false,
       "port": 3306
     }
   }
   ```


## 自动化安装MySQL
   假设你已经梳理好了 MySQL 的基本配置
   |**参数**|**值**|**意义**|
   |--------|------|------|
   |port| 3306| MySQL 端口号|
   |ibps| 128M| innodb_buffer_pool_size|
   |pkg-name| mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz | MySQL 安装包的名字|

   >我这里假设你已经把 mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz	下载并保存到了 127.0.0.1:/usr/local/dbm-agent/pkgs/ 目录

   现在就可以通过调用接口的方式来安装 MySQL 数据库了。
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
   --data '{"port":3306, "ibps":"128M", "pkg-name":"mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz"}' \
   http://127.0.0.1:8086/apis/mysqls/install


   {
      "message": "install mysql compelet."
   }
   ```
   检查 mysql 是否完成成功。
   ```bash
   ps -ef | grep mysqld
   mysql33+ 2984464       1  0 21:00 ?        00:00:02 /usr/local/mysql-8.0.31-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/etc/my-3306.cnf
   root     2985758 2962382  0 21:05 pts/44   00:00:00 grep --color=auto mysqld
   ```
   也可以连接上去检查。
   ```bash
   mysql -uroot -pdbma@0352 -h127.0.0.1 -P3306
   mysql: [Warning] Using a password on the command line interface can be insecure.
   Welcome to the MySQL monitor.  Commands end with ; or \g.
   Your MySQL connection id is 10
   Server version: 8.0.31 MySQL Community Server - GPL
   
   Copyright (c) 2000, 2023, Oracle and/or its affiliates.
   
   Oracle is a registered trademark of Oracle Corporation and/or its
   affiliates. Other names may be trademarks of their respective
   owners.
   
   Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
   
   mysql> show processlist;
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   | Id | User            | Host            | db   | Command | Time | State                  | Info             |
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   |  5 | event_scheduler | localhost       | NULL | Daemon  |   50 | Waiting on empty queue | NULL             |
   | 10 | root            | 127.0.0.1:35720 | NULL | Query   |    0 | init                   | show processlist |
   +----+-----------------+-----------------+------+---------+------+------------------------+------------------+
   2 rows in set (0.00 sec)
   ```

   当然直接使用命令行工具也是可以的。
   ```bash
   dbma-cli-single-instance --port=3306 --pkg-name=mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz --ibps=128M master
   ```
   ---


## 自动化卸载MySQL
   调用 http 接口来卸载 MySQL 数据库
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
   --data '{"port":3306}' \
   http://127.0.0.1:8086/apis/mysqls/uninstall 2>/dev/null | jq


   {
     "message": "uninstall mysql complete ."
   }
   ```

   同样也可以使用命令行工具
   ```bash
   dbma-cli-single-instance --port=3306 uninstall
   ```
   ---


## 关闭dbm-agent
   **关闭 dbm-agent 守护进程**
   ```bash
   dbm-agent stop                                                              
   Successful exit
   ```
   ---


## 规范
  **dbm-agent 在实现上遵守的规范**

  |**规范ID**|**规范内容**|
  |----------|--------|
  |dbm-agent 工作目录位置 | /usr/local/dbm-agent |
  |mysql 配置文件保存的位置 | /etc/my-{port}.cnf |
  |systemd 配置文件保存的位置 | /usr/lib/systemd/system/mysqld-{port}.service |
  |数据目录   | /database/mysql/data/{port} |
  |备份目录   | /backup/mysql/{port} |
  |binlog目录| /binlog/mysql/binlog/{port} |
  |默认密码   | dbma@0352 |
  |MySQL 安装目录| /usr/local/|
  |MySQL-shell 安装目录| /usr/local/|

  ---


## 源码依赖
   如果你是用的源码来安装的 Python ，尽可能的安装上这些依赖会对你有帮助。
   ```bash
   yum -y install gcc gcc-c++ libffi libyaml-devel libffi-devel zlib zlib-devel openssl shadow-utils net-tools \
   openssl-devel libyaml sqlite-devel libxml2 libxslt-devel libxml2-devel wget vim mysql-devel libaio
   ```
   Centos-8.x 的话还要多安装一个包
   ```bash
   yum -y install ncurses-compat-libs
   ```
   ---

## 官方微信公众平台 

![官方微信公众平台](imgs/mp-wechat.jpg)

---