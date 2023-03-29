## 目录
---
- [目录](#目录)
- [dbm-agent](#dbm-agent)
- [依赖](#依赖)
- [安装](#安装)
- [初始化](#初始化)
- [自动化安装MySQL](#自动化安装MySQL)
- [自动化卸载MySQL](#自动化卸载MySQL)


---

官方微信公众平台 

![官方微信公众平台](imgs/mp-wechat.jpg)

---

## dbm-agent
  dbm 是一个软件套件，包含有 dbm-center 和 dbm-agent 两大组成部分；其中 dbm-center 可以看成一个 web 站点，DBA 通过它可以查看监控、告警、部署各种 MySQL 环境。
  dbm-agent 是 dbm-center 的助手，负责环境的部署、监控的采集与上报、数据库的备份与监控。总的来讲接活的 dbm-center 真正干活的是 dbm-agent。另外 dbm-agent 也集成了若干命令行工具，这使得它也可以单独使用。
  
  ![dbm](imgs/dbm.png)

  ---

  **dbm(DataBase Management center)-agent：MySQL|Redis 数据库管理中心客户端程序**

  我们希望 DBA 可以从日常的工作中解放出来，做到只要在 web 界面上点一下“同意”系统就能自动、高效、优质的完成所有的操作；同样对于那些我们认为不合理的需求只要点一个“驳回”系统除了向需求方回一个被驳回的响应之外什么都不会干，安静的像一个美男子；更有意思的事，对于所有能用自动化解决的问题，dbm 绝对不会大半夜打 dba 的电话，出现故障自动解决，完成之后记录一下日志就行。

  ---

  **dbm-agent 的工作原理**

  dbm-agent 是安装在你机器上的一个 python 程序，它可以工作在两个模式
  
  一：守护进程模式，这个模式下它会定时从数据库管理中心(dbm-center)查询要执行的任务，并定时上报一些监控信息到管理中心；管理中心会用这些数据来做预测分析，问题早发现(自动发现)，早解决(自动解决)，另外管理中心还会用这个来生成报表，一天只要看一眼你对你所管理的数据库便了然于胸。还有另一些情况你可能会打开管理中心的 web 界面，那就是审批了，其它时间喝咖啡去吧！！！

  二：命令行模式，这个模式下直接执行 dbm-agent 提供的命令完成操作，相较手工操作这个模式也能极大的提高效率，相对与守护进程模式，它不是 low 了一级别。

  ---

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

## 依赖
   **1、python-3.8.x 及以上版本** dbm-agent 是用 python-3 语法编写的程序

   **2、centos-7 及以上版本** dbm-agent 在操作系统层面只支持到 centos-7 以上版本的系统(centos8也支持)

   **3、mysql-8.0.31 及以上版本** 个人的精力有限，决定不支持 mysql-8.0.17 以下版本的 MYSQL

   **4、其它依赖** 如果你打算编译安装 python-3 环境，建议在此之前先安装上如下依赖包
   ```bash
   yum -y install gcc gcc-c++ libffi libyaml-devel libffi-devel zlib zlib-devel openssl shadow-utils net-tools \
   openssl-devel libyaml sqlite-devel libxml2 libxslt-devel libxml2-devel wget vim mysql-devel libaio
   ```
   Centos-8.x 的话还要多安装一个包
   ```bash
   yum -y install ncurses-compat-libs
   ```

   ---

## 安装
   **安装方法：pip3 安装**
   ```bash
   # 安装 dbm-agent
   pip3 install dbm-agent

   Installing collected packages: dbm-agent
     Running setup.py install for dbm-agent ... done
   Successfully installed dbm-agent-0.4.2
   ```
   如果你是在国内，推荐使用腾讯云的源对 pip 安装进行加速，配置也非常简单一行命令搞定
   ```bash
   pip3 config set global.index-url  https://mirrors.cloud.tencent.com/pypi/simple
   ```

   > pip3 是 python3 的一个包管理工具，类似于 centos 中的 yum ，另外 dbm-agent 版本号的最后一位是奇数表示它是一个开发版本，偶数表示它是一个稳定版本

   ---

## 初始化
   **要 dbm-agent 能运行起来还要有一些其它的工作要，比如创建 dbma 用户，创建工作目录 /usr/local/dbm-agent 和一些重要的配置文件。作为一个成熟的软件，这一切都是可以自动完成的。**
   ```bash
   # 由于要创建用户和目录，dbm-agent 需要 root 权限
   sudo su
   # init ，通过--dbm-center-url-prefix 选项指定管理端的访问路径、如果你不与 dbm-center 一起使用也可以不加 --dbm-center-url-prefix
   dbma-cli-init --net-card=eth0 --dbm-center-url-prefix=https://127.0.0.1
   net-card eth0's ip = 10.206.0.15
   going to init ...
   [2023-03-29 23:37:02,478 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 23 line]  ~  start install dbm-agent .
   [2023-03-29 23:37:02,478 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 32 line]  ~  prepare create user dbma .
   [2023-03-29 23:37:02,479 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 35 line]  ~  create user dbma done .
   [2023-03-29 23:37:02,479 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 38 line]  ~  prepare create directions .
   [2023-03-29 23:37:02,479 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 46 line]  ~  create directions done .
   [2023-03-29 23:37:02,479 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 49 line]  ~  prepare copy template files .
   [2023-03-29 23:37:02,482 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 55 line]  ~  copy template files done .
   [2023-03-29 23:37:02,485 INFO] - [MainThread] - [/usr/local/python/lib/python3.11/site-packages/dbma/core/agent/init.py 67 line]  ~  install dbm-agent done . 
    dbm-agent start 
    to start dbm-agent service .
   
   # 执行完成上面的步骤整个初始化就算完成了，实现上只是创建一些必要的用户，目录，文件 
   # 初始化会创建 dbm 用户

   grep dbm /etc/passwd    
   dbma:x:2048:2048::/home/dbma:/bin/bash
   
   # 初始化会创建 /usr/local/dbm-agent/ 目录
   tree /usr/local/dbm-agent/

   ├── etc
   │   ├── dbma.cnf          # dbm-agent 的配置文件
   │   ├── init-users.sql    # 在初始化数据库里将使用这个文件中的用户名和密码来创建用户
   │   └── templates
   │       ├── 5_7.cnf.jinja # 未启用
   │       ├── 8_0.cnf.jinja # 未启用
   │       ├── create-innodb-cluster.js
   │       ├── init-users.sql.jinja
   │       ├── mysql-8.0.17.cnf.jinja    # mysql-8.0.17 版本对应的配置文件模板
   │       ├── mysql-8.0.18.cnf.jinja    # mysql-8.0.18 版本对应的配置文件模板
   │       ├── mysql-8.0-init-only.jinja # 只有初始化时才用到的配置文件
   │       └── mysqld.service.jinja      # mysql systemd 配置文件模板
   ├── logs    # dbm-agent 的日志文件保存目录(只要有守护进程模式下才会向这时写日志)
   └── pkg
       ├── mysql-8.0.18-linux-glibc2.12-x86_64.tar.xz          # 各个软件的安装包(要自己下载并保存到这里，dbm-agent不会自动下载它)
       └── mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz # 各个软件的安装包(要自己下载并保存到这里，dbm-agent不会自动下载它)
   ```
   ---


## 启动 dbm-agent
   ```bash
   dbm-agent start

   log file '/tmp/dbm-agent.log' .
   ======== Running on http://0.0.0.0:8086 ========
   ```
   检查 dbm-agent 是否安装成功(调用一下 dbm-agent 提供的接口，如果能正常返回那就是说明安装成功了)
   ```
   curl http://127.0.0.1:8086/apis/dbm-agent 2>/dev/null | jq 
   {
     "name": "dbm-agent",
     "version": "8.31.8"
   }
   ```

   --- 

## 自动化安装MySQL
   假设你要安装的 MySQL 端口监听在 3306， innodb_buffer_pool_size 设置为 128M， MySQL 版本取 mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz 。
   你可以通过调用接口来安装 MySQL ，当然我更加推荐你通过 dbm-center 提供的 web 页面来做这个事，如果你只是想上手 dbm-center 的话就直接来吧。
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
   --data '{"port":3306, "ibps":"128M", "pkg-name":"mysql-8.0.31-linux-glibc2.12-x86_64.tar.xz"}' \
   http://127.0.0.1:8086/apis/mysqls/install


   {"message": "install mysql compelet."}
   ```
   检查 mysql 是否完成成功
   ```bash
   ps -ef | grep mysqld
   mysql33+ 2984464       1  0 21:00 ?        00:00:02 /usr/local/mysql-8.0.31-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/etc/my-3306.cnf
   root     2985758 2962382  0 21:05 pts/44   00:00:00 grep --color=auto mysqld
   ```

   ---


## 自动化卸载MySQL
   当然卸载也可以通过接口来完成
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" \
   --data '{"port":3306}' \
   http://127.0.0.1:8086/apis/mysqls/uninstall 2>/dev/null | jq


   {
     "message": "uninstall mysql complete ."
   }
   ```
   ---




## 关闭 dbm-agent
   **关闭 dbm-agent 守护进程**
   ```bash
   dbm-agent stop                                                              
   Successful exit
   ```
   ---
