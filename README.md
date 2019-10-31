## 目录
---
- [dbm-agent](#dbm-agent)
- [依赖](#依赖)
- [安装](#安装)
- [初始化](#初始化)
- [启动](#启动)
- [关闭](#关闭)
- [升级](#升级)
- [卸载](#卸载)
- [参数说明](#参数说明)
- [dbm-agent集成的命令行工具](#dbm-agent集成的命令行工具)
   - [自动化安装卸载MySQL](#自动化安装卸载MySQL)
   - [自动备份](#自动备份)
   - [自动增加Slave](#自动增加Slave)
   - [自动搭建MGR高可用集群](#自动搭建MGR高可用集群)
   - [自动安装mysql-shell](#自动安装mysql-shell)
   - [自动化配置innodb-cluster](#自动化配置innodb-cluster)
   - [自动化配置mysql-router](#自动化配置mysql-router)
   - [自动采集主机监控并上传到服务端(dbm-center)](#自动采集主机监控并上传到服务端)

---

## dbm-agent
  **dbm(DataBase Management center)-agent：MySQL 数据库管理中心客户端程序**

  我们希望 DBA 可以从日常的工作中解放出来，做到只要在 web 界面上点一下“同意”系统就能自动、高效、优质的完成所有的操作；同样对于那些我们认为不合理的需求只要点一个“驳回”系统除了向需求方回一个被驳回的响应之外什么都不会干，安静的像一个美男子；更有意思的事，对于所有能用自动化解决的问题，dbm 绝对不会大半夜打 dba 的电话，出现故障自我解决，完成之后记录一下日志就行。

  ---

  **dbm-agent 的工作原理**

  dbm-agent 是安装在你机器上的一个 python 程序，它可以工作在两个模式
  
  一：守护进程模式，这里它会定时从数据库管理中心(dbm-center)查询要执行的任务，并定时上报一些监控信息到数据库管理中心，这样你只要通过 dbm-center 提供的 web 界面就能完成所有的操作。

  二：命令行模式，这个模式下直接通过 dbm-agent 提供的命令完成操作，相较手工操作这个模式也能极大的提高效率，相对与守护进程模式，这是一种临时的救急的模式。

  ---

  **dbm-agent 在实现上遵守的规范**

  |**规范ID**|**规范内容**|
  |----------|--------|
  |dbm-agent 工作目录位置 | /usr/local/dbm-agent |
  |mysql 配置文件保存的位置 | /etc/my-{port}.cnf |
  |systemd 配置文件保存的位置 | /usr/lib/systemd/system/mysqld-{port}.service |
  |数据目录   | /database/mysql/data/{port} |
  |备份目录   | /backup/mysql/{port} |
  |默认密码   | dbma@0352 |
  |MySQL 安装目录| /usr/local/|
  |MySQL-shell 安装目录| /usr/local/|

  ---

## 依赖
   **1、python-3.6.x 级以上版本** dbm-agent 是用 python-3 语法编写的程序

   **2、centos-7 级以上版本** dbm-agent 在操作系统层面只支持到 centos-7 以上版本的系统(centos8也支持)

   **3、mysql-8.0.17 级以上版本** 个人的精力有限，决定不支持 mysql-8.0.17 以下版本的 MYSQL

   **4、其它依赖** 如果你打算编译安装 python-3 环境，建议在此之前先安装上如下依赖包
   ```bash
   yum -y install gcc gcc-c++ libffi libyaml-devel libffi-devel zlib zlib-devel openssl shadow-utils \
   openssl-devel libyaml sqlite-devel libxml2 libxslt-devel libxml2-devel wget vim mysql-devel 
   ```

   ---

## 安装
   **安装方法一）：源码安装**
   ```bash
   sudo su
   # 安装依赖
   pip3 install jinja2 psutil requests mysql-connector-python==8.0.17 distro==1.4.0

   # 先手工运行一下自动化测试用例，以确保你的平台有被支持
   cd dbm-agent
   bash autotest.sh

   # 输出大致如下
   # ----------------------------------------------------------------------
   # Ran 7 tests in 0.098s
   # 
   # OK

   python3 setup.py build &&  python3 setup.py install

   # 输出大致如下
   #running install_scripts
   #copying build/scripts-3.7/dbm-agent -> /usr/local/python/bin
   #changing mode of /usr/local/python/bin/dbm-agent to 755
   #running install_egg_info
   #Writing /usr/local/python/lib/python3.7/site-packages/dbmc_agent-0.0.0.0-py3.7.egg-info   
   ```
   >目前 dbm-agent 的开发测试环境为 centos-7.6 + python-3.7.3 ；并且以后也不会兼容 centos-7.0 以下的版本，但是 python 会支持到 python3.6.0

   **安装方法二）：pip3 安装**
   ```bash
   # 安装依赖
   pip3 install jinja2 psutil requests mysql-connector-python==8.0.17 distro==1.4.0
   # 安装 dbm-agent
   pip3 install dbm-agent

   Installing collected packages: dbm-agent
     Running setup.py install for dbm-agent ... done
   Successfully installed dbm-agent-0.1.2
   ```
   如果你是在国内，推荐使用腾讯云的源对 pip 安装进行加速，配置也非常简单一行命令搞定
   ```bash
   pip3 config set global.index-url  https://mirrors.aliyun.com/pypi/simple
   ```

   > pip3 是 python3 的一个包管理工具，类似于 centos 中的 yum ，版本号的最后一位是奇数表示它是一个开发版本，偶数表示它是一个稳定版本

   ---

## 初始化
   **要 dbm-agent 能运行起来还要有一些其它的工作要，比如创建 dbma 用户，创建工作目录 /usr/local/dbm-agent 和一些重要的配置文件。作为一个成熟的软件，这一切都是可以自动完成的。**
   ```bash
   # 由于要创建用户和目录，dbm-agent 需要 root 权限
   sudo su
   # init ，通过--dbmc-site 选项指定管理端的访问路径、如果你不与 dbm-center 一起使用也可以不加 --dbmc-site
   dbm-agent --dbmc-site=https://192.168.100.100 init
   #dbm-agent init compeleted .

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

## 启动
   **dbm-agent 默认会自动以守护进程的方式运行**

   **1、** 启动
   ```bash
   dbm-agent start
   Successful start and log file save to '/usr/local/dbm-agent/logs/dbma.log'

   ```
   启动完成之后 dbm-agent 会以守护进程的方式在后台运行，周期性的上报主机的性能指标到服务端(dbm-center)，并从 dbm-center 检查要执行的任务(任务是一个抽象的概念，任何之前需要 DBA 手工执行的操作都可以看成一个任务)
   ```sql
   -- 更多其它方面的监控请查看 dbm-center 这个项目
   mysql> select * from hosts_cputimesmodel order by id  limit 23,17;
   +----+----------------------------+-------+--------+-------+-------+--------+-------+---------+---------+
   | id | create_time                | user  | system | idle  | nice  | iowait | irq   | softirq | host_id |
   +----+----------------------------+-------+--------+-------+-------+--------+-------+---------+---------+
   | 24 | 2019-10-03 18:37:41.849744 | 0.007 |  0.005 | 0.989 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 25 | 2019-10-03 18:38:42.902971 | 0.006 |  0.005 | 0.989 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 26 | 2019-10-03 18:39:35.405399 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 27 | 2019-10-03 18:40:35.487535 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 28 | 2019-10-03 18:41:35.574100 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 29 | 2019-10-03 18:43:44.879151 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 30 | 2019-10-03 18:44:44.988876 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 31 | 2019-10-03 18:45:45.017535 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 32 | 2019-10-03 18:46:45.042812 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 33 | 2019-10-03 18:47:45.086554 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 34 | 2019-10-03 18:48:45.146277 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 35 | 2019-10-03 18:49:45.227072 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 36 | 2019-10-03 18:50:45.263859 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 37 | 2019-10-03 18:51:45.360525 | 0.007 |  0.005 | 0.988 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 38 | 2019-10-03 18:52:45.437180 | 0.007 |  0.005 | 0.989 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   | 39 | 2019-10-03 18:53:45.464134 | 0.007 |  0.005 | 0.989 | 0.000 |  0.000 | 0.000 |   0.000 |       2 |
   +----+----------------------------+-------+--------+-------+-------+--------+-------+---------+---------+
   16 rows in set (0.00 sec)

   -- 
   ```
   **2、** 观察进程的运行状态
   ```bash
   ps -ef | grep dbm                                                         
   dbma       7225      1  0 11:31 ?        00:00:00 /usr/local/python-3.7.3/bin/python3.7 /usr/local/python/bin/dbm-agent start
   root       7229   7167  0 11:32 pts/0    00:00:00 grep --color=auto dbm
   ```
   **3、** dbm-agent 的日志保存在 /usr/local/dbm-agent/logs/dbma.log 文件中
   ```bash
   cat /usr/local/dbm-agent/logs/dbma.log
   2019-08-31 07:57:08,409 - dbm-agent.server - MainThread - INFO - dbm-agent starting
   ```

   ---

## 关闭
   **关闭 dbm-agent 守护进程**
   ```bash
   dbm-agent stop                                                              
   Successful exit
   ```
   ---

## 升级
   **升级 dbm-agent 要分两步走**
   ```
   # 第一步：升级软件
   dbm-agent stop
   pip3 install dbm-agent

   # 第二步：升级配置文件
   dbm-agent upgrade

   2019-09-16 16:47:49,328 INFO going to upgrade dbm-agent
   2019-09-16 16:47:49,329 INFO backup etc/templates
   2019-09-16 16:47:49,329 INFO create new etc/templates
   2019-09-16 16:47:49,333 INFO upgrade complete
   ```
   ---

## 卸载
   **卸载 dbm-agent 要分两步走、第一步：删除 dbm-agent 对应的用户和数据 第二步：卸载 dbm-agent 软件包**
   ```bash
   # uninit 会自动完成相关用户(dbma)和数据(/usr/local/dbm-agent/)的删除
   dbm-agent uninit
   # 卸载 dbm-agent
   pip3 uninstall dbm-agent
   ```

   ---

## 参数说明
   **dbm-agent 支持若干参数，详细内容如下**

   |**参数名** | **意义** | **默认值** |
   |--------------|----------|-----------|
   |-- dbmc-site  | dbm服务端http(s)根路径 | https://192.168.100.100 |
   |-- basedir    | dbm-agent 的安装目标 | /usr/local/dbm-agent/ |
   |-- config-file| dbm-agent 配置文件的位置 | etc/dbma.cnf |
   |-- idc-name   | 主机所属的机房信息         | mysql-idc |
   |-- user       | 运行 dbm-agent 的主机用户 | dbma       |
   |action        | 要执行的操作 {start \| stop} | |

   ---

## dbm-agent集成的命令行工具
   实现生活中，用户对一套完整的数据库管理平台并不强烈，主要是因为他那里的数据库实例个数一个手都数的过来；然后告诉他部署一套管理平台要用的机器
   比现在的数据库都多，他还要个锤子。

   好消息是 dbm-agent 自带了许多开箱即用的命令行工具，做到 0 成本升级生产工具

   --- 

## 自动化安装卸载MySQL
   **1、安装 dbm-agent 并 初始化**
   ```bash
   pip3 install dbm-agent
   dbm-agent init
   ```
   **2、复制 mysql 二进制安装包到 /usr/local/dbm-agent/pkg/ 目录**
   ```bash
   # dbm-agent 只支持 mysql-8.0.17 及以上版本
   cp mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz /usr/local/dbm-agent/pkg
   ```
   **3、自动安装 MySQL 单机(支持单机多实例)**
   ```bash
   -- max_mem 指定实例使用的内存大小
   -- port 指定实例监控的端口端口

   dbma-cli-single-instance install --port=3306


   2019-09-16 16:10:30,951 - dbm-agent - MainThread - INFO - enter install mysql instance logic port=3306
   2019-09-16 16:10:30,951 - dbm-agent.dbma.mysql - MainThread - INFO - install mysql instance with this mysql version mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz port 3306 max_mem 1024 MB
   2019-09-16 16:10:30,951 - dbm-agent.dbma.mysql - MainThread - INFO - check port 3306 is in use or not
   2019-09-16 16:10:30,952 - dbm-agent.dbma.mysql - MainThread - INFO - check config file  /etc/my-3306.cnf 
   2019-09-16 16:10:30,952 - dbm-agent.dbma.mysql - MainThread - INFO - check datadir /database/mysql/data/3306
   2019-09-16 16:10:30,952 - dbm-agent.dbma.mysql - MainThread - INFO - check mysql version mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz
   2019-09-16 16:10:30,967 - dbm-agent.dbma.mysql - MainThread - INFO - create datadir /database/mysql/data/3306
   2019-09-16 16:10:30,967 - dbm-agent.dbma.mysql - MainThread - INFO - unarchive mysql pkg to /usr/local/
   2019-09-16 16:10:30,967 - dbm-agent.dbma.mysql - MainThread - WARNING - /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64 exists mysql may has been installed. skip untar mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz to /usr/local/
   2019-09-16 16:10:30,967 - dbm-agent.dbma.configrender - MainThread - INFO - load template from /usr/local/dbm-agent/etc/templates/
   2019-09-16 16:10:30,967 - dbm-agent.dbma.configrender - MainThread - INFO - template file name mysql-8.0.17.cnf.jinja
   2019-09-16 16:10:30,971 - dbm-agent.dbma.configrender - MainThread - INFO - mysql pkg mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz max memory 1024
   2019-09-16 16:10:30,971 - dbm-agent.dbma.configrender - MainThread - INFO - config cpu options
   2019-09-16 16:10:30,971 - dbm-agent.dbma.configrender - MainThread - INFO - config memory options
   2019-09-16 16:10:30,971 - dbm-agent.dbma.configrender - MainThread - INFO - config disk options
   2019-09-16 16:10:30,971 - dbm-agent.dbma.configrender - MainThread - INFO - going to render config file
   2019-09-16 16:10:30,972 - dbm-agent.dbma.mysql - MainThread - INFO - init database with --initialize-insecure
   2019-09-16 16:10:30,972 - dbm-agent.dbma.mysql - MainThread - WARNING - ['/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld', '--defaults-file=/etc/my-3306.cnf', '--initialize-insecure', '--user=mysql3306', '--init-file=/usr/local/dbm-agent/etc/templates/init-users.sql']
   2019-09-16 16:10:35,772 - dbm-agent.dbma.mysql - MainThread - INFO - config service(systemd) and daemon-reload
   2019-09-16 16:10:35,772 - dbm-agent.dbma.configrender - MainThread - INFO - load template from /usr/local/dbm-agent/etc/templates/
   2019-09-16 16:10:35,772 - dbm-agent.dbma.configrender - MainThread - INFO - template file name mysqld.service.jinja
   2019-09-16 16:10:35,854 - dbm-agent.dbma.mysql - MainThread - INFO - config mysql auto start on boot
   2019-09-16 16:10:35,923 - dbm-agent.dbma.mysql - MainThread - INFO - config path env variable /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/
   2019-09-16 16:10:35,923 - dbm-agent.dbma.mysql - MainThread - INFO - start mysqld-3306 by systemcl start mysqld-3306
   2019-09-16 16:10:35,942 - dbm-agent.dbma.mysql - MainThread - INFO - export so file
   2019-09-16 16:10:35,942 - dbm-agent.dbma.mysql - MainThread - INFO - export header file

   # 检查 mysql 数据为是否正常启动
   ps -ef | grep mysql                                                        
   mysql33+  10284      1  1 16:10 ?        00:00:02 /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/etc/my-3306.cnf  

   # 如果要实现单机多实例只要把端口改一下就行了
   dbma-cli-single-instance install --port=3309   

   2019-09-16 16:13:04,319 - dbm-agent - MainThread - INFO - enter install mysql instance logic port=3309
   2019-09-16 16:13:04,319 - dbm-agent.dbma.mysql - MainThread - INFO - install mysql instance with this mysql version mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz port 3309 max_mem 1024 MB
   2019-09-16 16:13:04,319 - dbm-agent.dbma.mysql - MainThread - INFO - check port 3309 is in use or not
   2019-09-16 16:13:04,320 - dbm-agent.dbma.mysql - MainThread - INFO - check config file  /etc/my-3309.cnf 
   2019-09-16 16:13:04,320 - dbm-agent.dbma.mysql - MainThread - INFO - check datadir /database/mysql/data/3309
   2019-09-16 16:13:04,320 - dbm-agent.dbma.mysql - MainThread - INFO - check mysql version mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz
   2019-09-16 16:13:04,334 - dbm-agent.dbma.mysql - MainThread - INFO - create datadir /database/mysql/data/3309
   2019-09-16 16:13:04,334 - dbm-agent.dbma.mysql - MainThread - INFO - unarchive mysql pkg to /usr/local/
   2019-09-16 16:13:04,335 - dbm-agent.dbma.mysql - MainThread - WARNING - /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64 exists mysql may has been installed. skip untar mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz to /usr/local/
   2019-09-16 16:13:04,335 - dbm-agent.dbma.configrender - MainThread - INFO - load template from /usr/local/dbm-agent/etc/templates/
   2019-09-16 16:13:04,335 - dbm-agent.dbma.configrender - MainThread - INFO - template file name mysql-8.0.17.cnf.jinja
   2019-09-16 16:13:04,338 - dbm-agent.dbma.configrender - MainThread - INFO - mysql pkg mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz max memory 1024
   2019-09-16 16:13:04,338 - dbm-agent.dbma.configrender - MainThread - INFO - config cpu options
   2019-09-16 16:13:04,338 - dbm-agent.dbma.configrender - MainThread - INFO - config memory options
   2019-09-16 16:13:04,338 - dbm-agent.dbma.configrender - MainThread - INFO - config disk options
   2019-09-16 16:13:04,339 - dbm-agent.dbma.configrender - MainThread - INFO - going to render config file
   2019-09-16 16:13:04,339 - dbm-agent.dbma.mysql - MainThread - INFO - init database with --initialize-insecure
   2019-09-16 16:13:04,339 - dbm-agent.dbma.mysql - MainThread - WARNING - ['/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld', '--defaults-file=/etc/my-3309.cnf', '--initialize-insecure', '--user=mysql3309', '--init-file=/usr/local/dbm-agent/etc/templates/init-users.sql']
   2019-09-16 16:13:11,011 - dbm-agent.dbma.mysql - MainThread - INFO - config service(systemd) and daemon-reload
   2019-09-16 16:13:11,011 - dbm-agent.dbma.configrender - MainThread - INFO - load template from /usr/local/dbm-agent/etc/templates/
   2019-09-16 16:13:11,011 - dbm-agent.dbma.configrender - MainThread - INFO - template file name mysqld.service.jinja
   2019-09-16 16:13:11,094 - dbm-agent.dbma.mysql - MainThread - INFO - config mysql auto start on boot
   2019-09-16 16:13:11,178 - dbm-agent.dbma.mysql - MainThread - INFO - config path env variable /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/
   2019-09-16 16:13:11,179 - dbm-agent.dbma.mysql - MainThread - INFO - start mysqld-3309 by systemcl start mysqld-3309
   2019-09-16 16:13:11,195 - dbm-agent.dbma.mysql - MainThread - INFO - export so file
   2019-09-16 16:13:11,196 - dbm-agent.dbma.mysql - MainThread - INFO - export header file

   ps -ef | grep mysql

   mysql33+  10284      1  1 16:10 ?        00:00:02 /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/etc/my-3306.cnf                                                      
   mysql33+  10425      1  7 16:13 ?        00:00:04 /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/etc/my-3309.cnf

   ```
   **4、卸载 MySQL**
   这个操作会删除实例对应的用户、配置文件、数据目录
   ```bash
   dbma-cli-single-instance uninstall --port=3309
   # dbm-agent 有对卸载做安全检查、如果实例还在运行中这个时候卸载会失败

  2019-09-16 16:14:46,533 - dbm-agent - MainThread - INFO - enter uninstall mysql instance logic port=3309
  2019-09-16 16:14:46,534 - dbm-agent.dbma.mysql - MainThread - ERROR - mysql-3309 is runing cant uninstall 'systemctl stop mysqld-3309'

   # 先关闭数据库服务
   systemctl stop mysqld-3309

   dbma-cli-single-instance uninstall --port=3309
   
   2019-09-16 16:15:39,812 - dbm-agent - MainThread - INFO - enter uninstall mysql instance logic port=3309
   2019-09-16 16:15:39,813 - dbm-agent.dbma.mysql - MainThread - INFO - delete user mysql3309
   2019-09-16 16:15:39,829 - dbm-agent.dbma.mysql - MainThread - INFO - remove mysql config file /etc/my-3309.cnf
   2019-09-16 16:15:39,829 - dbm-agent.dbma.mysql - MainThread - INFO - remove systemctl config file /usr/lib/systemd/system/mysqld-3309.service
   2019-09-16 16:15:39,829 - dbm-agent.dbma.mysql - MainThread - INFO - remove datadir /database/mysql/data/3309

   ps -ef | grep mysql                                                        
   mysql33+  10284      1  1 16:10 ?        00:00:03 /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld --defaults-file=/etc/my-3306.cnf 
   
   ```

   ---

## 自动备份
   **现在 dbm-agent 在备份操作上支持 clone-plugin 之后会支持到 mysqlbackup extrabackup mysqldump 等工具**
   ```bash
   dbma-cli-backup-instance --host=127.0.0.1 --port=3306 --user=root --password=dbma@0352 clone
   
   2019-09-19 19:31:04,649 - dbm-agent.dbma.backups - MainThread - INFO - start backup mysql-3306 useing clone-plugin
   2019-09-19 19:31:05,031 - dbm-agent.dbma.backups - MainThread - INFO - backup mysql-3306 complete.

   # 备份文件保存到了 /backup/mysql/{port} 目录下
   ll /backup/mysql/3306
   总用量 0
   drwxr-x--- 5 mysql3306 mysql 168 9月  19 19:31 2019-09-19T19:31:04.649136
   ```
   ---

## 自动增加Slave
   **总的来说这个是一个相对较大的任务、人工完成会非常的繁琐、但是用 dbm-agent 只要两个命令，下面用为实例 172.16.192.100:3306 增加一个新的 slave 172.16.192.110:3306为例**

   **第一步：在 172.16.192.110 主机上安装新实例**
   ```bash
   # 在 172.16.192.110 机器上操作
   dbma-cli-single-instance install --port=3306
   ```
   **第二步：从 172.16.192.100:3306 克隆数据并建立复制关系**
   ```bash
   # 在 172.16.192.110 机器上操作
   dbma-cli-build-slave --host=127.0.0.1 --port=3306 --user=root --password=dbma@0352 --dhost=172.16.192.100 --dport=3306 --cuser=cloneuser --cpassword=dbma@0352  --ruser=repluser --rpassword=dbma@0352 build-slave

   2019-09-22 12:55:08,103 - dbm-agent.dbma.backups - MainThread - INFO - set @@global.clone_valid_donor_list='172.16.192.100:3306';
   2019-09-22 12:55:08,104 - dbm-agent.dbma.backups - MainThread - INFO - clone instance from cloneuser@'172.16.192.100':3306 identified by 'dbma@0352';
   2019-09-22 12:55:10,033 - dbm-agent.dbma.backups - MainThread - INFO - remonte clone complete.
   2019-09-22 12:55:10,034 - dbm-agent.dbma.backups - MainThread - INFO - mysqld-3306 restart complete.
   2019-09-22 12:55:10,034 - dbm-agent.dbma.backups - MainThread - INFO - wait 11 seconds
   2019-09-22 12:55:21,063 - dbm-agent.dbma.backups - MainThread - INFO - change master to master_host='172.16.192.100',master_port=3306,master_user='repluser',master_password='dbma@0352',master_ssl = 1,master_auto_position=1;
   2019-09-22 12:55:21,074 - dbm-agent.dbma.backups - MainThread - INFO - change master complete.
   2019-09-22 12:55:21,080 - dbm-agent.dbma.backups - MainThread - INFO - start slave complete.
   ```
   **第三步：检查**
   ```sql
   mysql -uroot -pdbma@0352 -h127.0.0.1 -P3306
   mysql> show slave status \G
   *************************** 1. row ***************************
                  Slave_IO_State: Waiting for master to send event
                     Master_Host: 172.16.192.100
                     Master_User: repluser
                     Master_Port: 3306
                   Connect_Retry: 60
                 Master_Log_File: mysql-bin.000002
             Read_Master_Log_Pos: 1124
                  Relay_Log_File: sqlstudio002-relay-bin.000002
                   Relay_Log_Pos: 400
           Relay_Master_Log_File: mysql-bin.000002
                Slave_IO_Running: Yes
               Slave_SQL_Running: Yes
    -- 主从正常
   mysql> select * from tempdb.t;                                                                   
   +------+
   | x    |
   +------+
   |  100 |
   |  200 |
   +------+
   2 rows in set (0.00 sec)
   -- 为了测试我专门在 172.16.192.100 上建立了库表，说明一切正常
   ```
   ---


## 自动搭建MGR高可用集群
   **以下面三台机器上搭建 MGR 集群为例**

   |**IP**|**角色**|
   |------|--------|
   |192.168.100.101| primary |
   |192.168.100.102| seconder |
   |192.168.100.103| seconder |

   **搭建 primary 结点**

   dbm-agent 在搭建 MGR 时把会 --members 选项中给定的第一个 IP 设置为 primary 其它的都设置为 seconder，所以 IP 地址出现的次序对结果尤为重要
   ```bash
   # 在 192.168.100.101 上执行
dbma-cli-build-mgr --port=3306 --max-mem=256 --members=192.168.100.101,192.168.100.102,192.168.100.103

2019-09-25 19:29:22,830 - dbm-agent.dbma.mysql - MainThread - INFO - build mgr with members 192.168.100.101,192.168.100.102,192.168.100.103
2019-09-25 19:29:22,830 - dbm-agent.dbma.mysql - MainThread - INFO - check members option is right or not
2019-09-25 19:29:22,830 - dbm-agent.dbma.mysql - MainThread - INFO - mysql group replication use 33061 for communicate
2019-09-25 19:29:22,830 - dbm-agent.dbma.mysql - MainThread - INFO - mgr ip {'192.168.100.101'}
2019-09-25 19:29:22,830 - dbm-agent.dbma.mysql - MainThread - INFO - mysql group replication  local_address use 192.168.100.101:33061
2019-09-25 19:29:22,830 - dbm-agent.dbma.mysql - MainThread - INFO - mysql group replication  group_seeds use  192.168.100.101:33061,192.168.100.102:33061,192.168.100.103:33061
2019-09-25 19:29:22,830 - dbm-agent.dbma.configrender - MainThread - INFO - load template from /usr/local/dbm-agent/etc/templates/
2019-09-25 19:29:22,830 - dbm-agent.dbma.configrender - MainThread - INFO - template file name mysql-8.0.17.cnf.jinja
2019-09-25 19:29:22,852 - dbm-agent.dbma.configrender - MainThread - INFO - mysql pkg mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz max memory 256
2019-09-25 19:29:22,852 - dbm-agent.dbma.mysql - MainThread - INFO - install mysql instance with mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz port 3306 max_mem 256 MB cores = 0
2019-09-25 19:29:22,852 - dbm-agent.dbma.mysql - MainThread - INFO - entry mysql group replication install logic
2019-09-25 19:29:22,852 - dbm-agent.dbma.mysql - MainThread - INFO - check package '/usr/local/dbm-agent/pkg/mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz' is exists
2019-09-25 19:29:22,853 - dbm-agent.dbma.mysql - MainThread - INFO - check port 3306 is in use or not
2019-09-25 19:29:22,853 - dbm-agent.dbma.mysql - MainThread - INFO - check config file  /etc/my-3306.cnf 
2019-09-25 19:29:22,853 - dbm-agent.dbma.mysql - MainThread - INFO - check datadir /database/mysql/data/3306
2019-09-25 19:29:22,853 - dbm-agent.dbma.mysql - MainThread - INFO - check mysql version mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz
2019-09-25 19:29:22,854 - dbm-agent.dbma.mysql - MainThread - INFO - check group_replication_local_address = 192.168.100.101:33061 option is right or not
2019-09-25 19:29:22,855 - dbm-agent.dbma.mysql - MainThread - INFO - check group_replication_group_seeds = 192.168.100.101:33061,192.168.100.102:33061,192.168.100.103:33061 option is right or not
2019-09-25 19:29:22,855 - dbm-agent.dbma.mysql - MainThread - INFO - change hostname to mgr192_168_100_101
2019-09-25 19:29:22,900 - dbm-agent.dbma.mysql - MainThread - INFO - config dns
2019-09-25 19:29:22,902 - dbm-agent.dbma.common - MainThread - INFO - 192.168.100.101 is a local ip force an record
2019-09-25 19:29:22,920 - dbm-agent.dbma.mysql - MainThread - INFO - create datadir /database/mysql/data/3306
2019-09-25 19:29:22,920 - dbm-agent.dbma.mysql - MainThread - INFO - unarchive mysql pkg to /usr/local/
2019-09-25 19:29:22,920 - dbm-agent.dbma.mysql - MainThread - WARNING - /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64 exists mysql may has been installed. skip untar mysql-8.0.17-linux-glibc2.12-x86_64.tar.xz to /usr/local/
2019-09-25 19:29:22,920 - dbm-agent.dbma.configrender - MainThread - INFO - config cpu options
2019-09-25 19:29:22,921 - dbm-agent.dbma.configrender - MainThread - INFO - config memory options
2019-09-25 19:29:22,921 - dbm-agent.dbma.configrender - MainThread - INFO - config disk options
2019-09-25 19:29:22,921 - dbm-agent.dbma.configrender - MainThread - INFO - going to render config file
2019-09-25 19:29:22,921 - dbm-agent.dbma.mysql - MainThread - INFO - init database with --initialize-insecure
2019-09-25 19:29:22,921 - dbm-agent.dbma.mysql - MainThread - WARNING - ['/usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/mysqld', '--defaults-file=/etc/my-3306.cnf', '--initialize-insecure', '--user=mysql3306', '--init-file=/usr/local/dbm-agent/etc/init-users.sql']
2019-09-25 19:29:27,414 - dbm-agent.dbma.mysql - MainThread - INFO - config service(systemd) and daemon-reload
2019-09-25 19:29:27,414 - dbm-agent.dbma.configrender - MainThread - INFO - load template from /usr/local/dbm-agent/etc/templates/
2019-09-25 19:29:27,414 - dbm-agent.dbma.configrender - MainThread - INFO - template file name mysqld.service.jinja
2019-09-25 19:29:27,480 - dbm-agent.dbma.mysql - MainThread - INFO - config mysql auto start on boot
2019-09-25 19:29:27,533 - dbm-agent.dbma.mysql - MainThread - INFO - config path env variable /usr/local/mysql-8.0.17-linux-glibc2.12-x86_64/bin/
2019-09-25 19:29:27,534 - dbm-agent.dbma.mysql - MainThread - INFO - start mysqld-3306 by systemctl start mysqld-3306
2019-09-25 19:29:27,576 - dbm-agent.dbma.mysql - MainThread - INFO - export so file
2019-09-25 19:29:27,576 - dbm-agent.dbma.mysql - MainThread - INFO - export header file
2019-09-25 19:29:27,584 - dbm-agent.dbma.common - MainThread - INFO - wait for 127.0.0.1:3306 avaiable
2019-09-25 19:29:28,586 - dbm-agent.dbma.mysql - MainThread - INFO - sleep 7 secondes wait for mysql protoco avaiable
2019-09-25 19:29:35,590 - dbm-agent.dbma.mysql - MainThread - INFO - this is a primary node prepare bootstrap a group
2019-09-25 19:29:35,608 - dbm-agent.dbma.mysql - MainThread - INFO - change master to master_user='repluser',master_password='dbma@0352' for channel 'group_replication_recovery';
2019-09-25 19:29:35,616 - dbm-agent.dbma.mysql - MainThread - INFO - set @@global.group_replication_bootstrap_group=ON;start group_replication;set @@global.group_replication_bootstrap_group=OFF;
2019-09-25 19:29:35,616 - dbm-agent.dbma.mysql - MainThread - INFO - mysql group replication primary node config complete

mysql -h127.0.0.1 -P3306 -uroot -pdbma@0352 -e"select * from performance_schema.replication_group_members;"
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST        | MEMBER_PORT | MEMBER_STATE | MEMBER_ROLE | MEMBER_VERSION |
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
| group_replication_applier | ba505d15-df87-11e9-9432-000c29f3e728 | mgr192_168_100_101 |        3306 | ONLINE       | PRIMARY     | 8.0.17         |
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+

```
添加第二个结点
```bash
# 在 192.168.100.102 上执行
dbma-cli-build-mgr --port=3306 --max-mem=256 --members=192.168.100.101,192.168.100.102,192.168.100.103
... ...
... ...

mysql -h127.0.0.1 -P3306 -uroot -pdbma@0352 -e"select * from performance_schema.replication_group_members;"
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST        | MEMBER_PORT | MEMBER_STATE | MEMBER_ROLE | MEMBER_VERSION |
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
| group_replication_applier | ba505d15-df87-11e9-9432-000c29f3e728 | mgr192_168_100_101 |        3306 | ONLINE       | PRIMARY     | 8.0.17         |
| group_replication_applier | c47e73dd-df87-11e9-894e-000c290844eb | mgr192_168_100_102 |        3306 | ONLINE       | SECONDARY   | 8.0.17         |
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+

```
添加第三个结点
```bash
# 在 192.168.100.103 上执行
dbma-cli-build-mgr --port=3306 --max-mem=256 --members=192.168.100.101,192.168.100.102,192.168.100.103
... ...
... ...

mysql -h127.0.0.1 -P3306 -uroot -pdbma@0352 -e"select * from performance_schema.replication_group_members;"
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST        | MEMBER_PORT | MEMBER_STATE | MEMBER_ROLE | MEMBER_VERSION |
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
| group_replication_applier | ba505d15-df87-11e9-9432-000c29f3e728 | mgr192_168_100_101 |        3306 | ONLINE       | PRIMARY     | 8.0.17         |
| group_replication_applier | c47e73dd-df87-11e9-894e-000c290844eb | mgr192_168_100_102 |        3306 | ONLINE       | SECONDARY   | 8.0.17         |
| group_replication_applier | e3eba066-df87-11e9-a9d6-000c29d535bc | mgr192_168_100_103 |        3306 | ONLINE       | SECONDARY   | 8.0.17         |
+---------------------------+--------------------------------------+--------------------+-------------+--------------+-------------+----------------+
   ```

**注意事项：**

1、你应该也看出来了，我们在三台主机上执行的命令是相同的，对这个就是为了方便 DBA 无脑操作

2、对于自动搭建 MGR 高可用集群来说，你只要保证防火墙是开放的就行，其它的事 dbm-agent 包圆了

---



## 自动安装mysql-shell
   **dbm-agent-0.2.9 及以上版本支持自动化安装 mysql-shell,并且会在初始化实现的时候就创建 innodbclusteradmin 这个 innodb-cluster 管理用户,也就是说已经完成了对 innodb-cluster 的相关准备**

   **第一步：** 确保 mysql-shell 的安装包已经下载到本地
   ```bash
   ll /usr/local/dbm-agent/pkg/
   总用量 526764
   -rw-r--r--. 1 root root 503854832 10月 31 16:42 mysql-8.0.18-linux-glibc2.12-x86_64.tar.xz
   -rw-r--r--. 1 root root  35547267 10月 31 16:44 mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz
   ```

   **第二步：自动化安装 mysql-shell**
   ```bash
   dbma-cli-mysqlsh --pkg=mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz install
   2019-10-31 16:46:29,781 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.per_checkings - MainThread - INFO - checking mysql-shell version
   2019-10-31 16:46:29,782 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.per_checkings - MainThread - INFO - cheking file /usr/local/dbm-agent/pkg/mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz exists or not
   2019-10-31 16:46:29,782 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.create_mysqlsh_user - MainThread - INFO - mysqlsh user exists skip create it
   2019-10-31 16:46:29,782 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.untar_pkg - MainThread - INFO - prepare untar mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz to /usr/local/
   2019-10-31 16:46:30,710 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.change_owner - MainThread - INFO - change owner to mysqlsh
   2019-10-31 16:46:30,815 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.export_path - MainThread - INFO - export PATH=/usr/local/mysql-shell-8.0.18-linux-glibc2.12-x86-64bit/bin/:$PATH has been exported.
   2019-10-31 16:46:30,815 - dbm-agent.dbma.mysqlops.MySQLShellInstaller.install - MainThread - INFO - mysql-shell-8.0.18-linux-glibc2.12-x86-64bit.tar.gz install compelete
   ```
   
   dbm-agent 会把 mysql-shell 也安装到 /usr/local/ 目录下，并且会自动导出 mysqlsh 这个命令
   ```bash
   which mysqlsh
   /usr/local/mysql-shell-8.0.18-linux-glibc2.12-x86-64bit/bin/mysqlsh
   ```

   ---

## 自动化配置innodb-cluster
   **在完成 mysql-shell 的安装之后，就可以 MGR 的主结点(primary)上配置 innodb-cluster 了**

   dbm-agent 在自动化安装 MGR 和 mysql-shell 的时候就已经为将来配置 innodb-cluster 打下了基础，所以到这一步就非常简单了一行命令解决问题，于是 dbm-agent 就没对这一行命令进行封装

   **1、** 在初始化实例时已经完成了对 innodb-cluster 管理用户的创建于授权
   ```sql
   select user,host from mysql.user where user='innodbclusteradmin';
   +--------------------+------+
   | user               | host |
   +--------------------+------+
   | innodbclusteradmin | %    |
   +--------------------+------+
   1 row in set (0.02 sec)
   ```
   **2、** mysql-shell 在上一个章节已经安装好了

   **3、** dbm-agent 还提供了一个拿来就用的创建 innodb-cluster 的 javascript 脚本，所以你要做的只是在primary结点所有的主机上运行一下如下脚本
   ```bash
   mysqlsh --uri innodbclusteradmin@127.0.0.1:3306 --password=dbma@0352 < /usr/local/dbm-agent/etc/templates/create-innodb-cluster.js 
   WARNING: Using a password on the command line interface can be insecure.
   A new InnoDB cluster will be created based on the existing replication group on instance '127.0.0.1:3306'.
   
   Creating InnoDB cluster 'production' on '127.0.0.1:3306'...
   
   Adding Seed Instance...
   Adding Instance 'mgr192_168_23_200:3306'...
   Adding Instance 'mgr192_168_23_201:3306'...
   Adding Instance 'mgr192_168_23_202:3306'...
   Resetting distributed recovery credentials across the cluster...
   Cluster successfully created based on existing replication group.
   ```

   到这里 innodb cluster 就创建完成了(如果你结合 dbm-center 一起使用只要在 web 界面上点一下，所以的操作都是自动的)

   ---

## 自动化配置mysql-router
   **由于官方推荐 mysql-router 和应用程序安装在同一台主机上，从这个角度来说 mysql-router 已经不是数据库管理系统要操心的事了，所以 dbm-agent 不实现对 mysql-router的安装。不过有一个惊喜要告诉你，就是 mysql-router 已经被官方打包到了 mysql-server ，也就是说你只要安装好了 mysql-server 就那你就已经有了 mysql-router**

   **第一步：** 配置 mysql-router

   ```bash
   # 创建 mysqlrouter 的运行用户
   useradd router

   ## 创建用于保存 mysql-router 配置的目录
   mkdir /usr/local/routers/

   
   # 调用 --bootstrap 让 mysqlrouter 可以根据实例中 innodb-cluster 的信息完成自我配置(router 这个时候会提示你输入密码要注意了)
   # 连接时并不会使用这 root 这里的 root 只是用来给 mysqlrouter 做自动化配置的
   mysqlrouter --bootstrap root@localhost:3306 --directory /usr/local/routers/3306 --conf-use-sockets --user=router

   # Bootstrapping MySQL Router instance at '/usr/local/routers/3306'...
   
   - Checking for old Router accounts
     - No prior Router accounts found
   - Creating mysql account 'mysql_router1_9nyhh5odceex'@'%' for cluster management
   - Storing account in keyring
   - Adjusting permissions of generated files
   - Creating configuration /usr/local/routers/3306/mysqlrouter.conf
   
   # MySQL Router configured for the InnoDB cluster 'production'
   
   After this MySQL Router has been started with the generated configuration
   
       $ mysqlrouter -c /usr/local/routers/3306/mysqlrouter.conf
   
   the cluster 'production' can be reached by connecting to:
   
   ## MySQL Classic protocol
   
   - Read/Write Connections: localhost:6446, /usr/local/routers/3306/mysql.sock
   - Read/Only Connections:  localhost:6447, /usr/local/routers/3306/mysqlro.sock
   
   ## MySQL X protocol
   
   - Read/Write Connections: localhost:64460, /usr/local/routers/3306/mysqlx.sock
   - Read/Only Connections:  localhost:64470, /usr/local/routers/3306/mysqlxro.sock
   ```
   **第二步：** 启动 mysql-router
   ```bash
   cd /usr/local/routers/3306/
   ll
   总用量 16
   drwx------. 2 router router   39 10月 31 17:08 data
   drwx------. 2 router router   29 10月 31 17:08 log
   -rw-------. 1 router router 1477 10月 31 17:08 mysqlrouter.conf
   -rw-------. 1 router router   94 10月 31 17:08 mysqlrouter.key
   drwx------. 2 router router    6 10月 31 17:08 run
   -rwx------. 1 router router  379 10月 31 17:08 start.sh
   -rwx------. 1 router router  179 10月 31 17:08 stop.sh
   
   ./start.sh 
   PID 2949 written to '/usr/local/routers/3306/mysqlrouter.pid'
   logging facility initialized, switching logging to loggers specified in configuration
   ```
   **第三步：** 检查
   ```bash
   netstat -ltpn | grep mysqlrouter
   tcp        0      0 0.0.0.0:64460           0.0.0.0:*               LISTEN      2949/mysqlrouter    
   tcp        0      0 0.0.0.0:6446            0.0.0.0:*               LISTEN      2949/mysqlrouter    
   tcp        0      0 0.0.0.0:6447            0.0.0.0:*               LISTEN      2949/mysqlrouter    
   tcp        0      0 0.0.0.0:64470           0.0.0.0:*               LISTEN      2949/mysqlrouter
   ```

   **第四步：** 对读写功能的检查

   对读的检查
   ```bash
   # 默认 mysqlrouter 的读端口是 6447
   mysql -uappuser -pdbma@0352 -h127.0.0.1 -P6447 -e"select @@server_id"
   +-------------+
   | @@server_id |
   +-------------+
   |         641 |
   +-------------+
   mysql -uappuser -pdbma@0352 -h127.0.0.1 -P6447 -e"select @@server_id"
   +-------------+
   | @@server_id |
   +-------------+
   |         879 |
   +-------------+
   mysql -uappuser -pdbma@0352 -h127.0.0.1 -P6447 -e"select @@server_id"
   +-------------+
   | @@server_id |
   +-------------+
   |         641 |
   +-------------+
   mysql -uappuser -pdbma@0352 -h127.0.0.1 -P6447 -e"select @@server_id"
   +-------------+
   | @@server_id |
   +-------------+
   |         879 |
   +-------------+
   ```
   对写的检查
   ```bash
   # 默认 mysqlrouter 的写端口是 6446
   mysql -uappuser -pdbma@0352 -h127.0.0.1 -P6446 -e"create database tempdb;show databases;select @@server_id;"
   +-------------------------------+
   | Database                      |
   +-------------------------------+
   | information_schema            |
   | mysql                         |
   | mysql_innodb_cluster_metadata |
   | performance_schema            |
   | sys                           |
   | tempdb                        |
   +-------------------------------+
   +-------------+
   | @@server_id |
   +-------------+
   |        1411 |
   +-------------+
   ```
   
   ---



## 自动采集主机监控并上传到服务端
   **dbm-agent 守护进程在后台运行的时候就会周期性的上报主机的监控信息，如果你想手工体验的话 dbm-agent 也有给出命令行接口**
   ```bash
   dbma-cli-pusher all 

   2019-10-03 18:17:03,498 - dbm-agent.dbma.pusher.push_host - MainThread - INFO - using http://172.16.192.1:8080/dbmc/hosts/?pk=-1 Got csrfmiddlewaretoken = RUNN9CL9UzZwUQbfkchmIv8qXQvuHlE5x1bhE8knz4HPMTQni2UVyZUB6oqfZaZr
   2019-10-03 18:17:03,505 - dbm-agent.dbma.pusher.push_host - MainThread - INFO - gather host info = {'host_uuid': 'dde1f082-67fc-436f-a149-90a1fa4612c2', 'agent_version': '0.2.0', 'cpu_cores': 1, 'mem_total_size': 1535696896, 'manger_net_ip': '172.16.192.100', 'csrfmiddlewaretoken': 'RUNN9CL9UzZwUQbfkchmIv8qXQvuHlE5x1bhE8knz4HPMTQni2UVyZUB6oqfZaZr', 'os_version': 'CentOS Linux-7-Core'}
   2019-10-03 18:17:03,506 - dbm-agent.dbma.pusher.push_host - MainThread - INFO - post host info to http://172.16.192.1:8080/dbmc/hosts/
   2019-10-03 18:17:03,584 - dbm-agent.dbma.pusher.push_host - MainThread - INFO - {'code': 201, 'message': '数据库中已经存在 host_uuid = dde1f082-67fc-436f-a149-90a1fa4612c2 ,服务端已经完成了对这条记录的更新'}
   2019-10-03 18:17:03,584 - dbm-agent.dbma.pusher.push_host - MainThread - INFO - push host info complete
   2019-10-03 18:17:03,585 - dbm-agent.dbma.pusher.push_cpu_times - MainThread - INFO - push cpu times info to dbmc
   2019-10-03 18:17:03,585 - dbm-agent.dbma.pusher.push_cpu_times - MainThread - INFO - query http://172.16.192.1:8080/dbmc/hosts/dde1f082-67fc-436f-a149-90a1fa4612c2/cpu-times/?pk=-1 for get csrftoken
   2019-10-03 18:17:03,618 - dbm-agent.dbma.pusher.push_cpu_times - MainThread - INFO - csrftoken = lf89MkihOZDGf2FKo8iYHkDmDhD6ZUn1pj8xIQO40K71OOfz7GMTyBqNfTtk6nCS
   2019-10-03 18:17:03,618 - dbm-agent.dbma.pusher.push_cpu_times - MainThread - INFO - cpu times = {'user': 0.007474045184000431, 'system': 0.005311213926884194, 'idle': 0.9870196488006041, 'nice': 8.409141746175102e-06, 'iowait': 9.92278726048662e-05, 'irq': 0.0, 'softirq': 8.745507416022106e-05, 'host_uuid': 'dde1f082-67fc-436f-a149-90a1fa4612c2', 'csrfmiddlewaretoken': 'lf89MkihOZDGf2FKo8iYHkDmDhD6ZUn1pj8xIQO40K71OOfz7GMTyBqNfTtk6nCS'}
   2019-10-03 18:17:03,696 - dbm-agent.dbma.pusher.push_cpu_times - MainThread - INFO - {'code': 200, 'message': '保存成功', 'data': []}
   2019-10-03 18:17:03,696 - dbm-agent.dbma.pusher.push_cpu_times - MainThread - INFO - push cpu times info completed.
   2019-10-03 18:17:03,697 - dbm-agent.dbma.pusher.push_cpu_frequence - MainThread - INFO - prepare push cpu frequence to dbmc
   2019-10-03 18:17:03,730 - dbm-agent.dbma.pusher.push_cpu_frequence - MainThread - INFO - OrderedDict([('current', 2899.721), ('csrfmiddlewaretoken', '6JN7WBm6Z5aSsim3vrb4kx2fP5qnNT03tT8sJrTaretnj8w4HFPKj9gPLluH2Q8w')])
   2019-10-03 18:17:03,809 - dbm-agent.dbma.pusher.push_cpu_frequence - MainThread - INFO - {'code': 200, 'message': '保存成功', 'data': []}
   2019-10-03 18:17:03,809 - dbm-agent.dbma.pusher.push_net_interfaces - MainThread - INFO - prepase push net interface info
   2019-10-03 18:17:03,841 - dbm-agent.dbma.pusher.push_net_interfaces - MainThread - INFO - using http://172.16.192.1:8080/dbmc/hosts/dde1f082-67fc-436f-a149-90a1fa4612c2/net-interfaces/?pk=-1 for go token
   2019-10-03 18:17:03,841 - dbm-agent.dbma.pusher.push_net_interfaces - MainThread - INFO - csrftoken = gcGwN4bJkXqRD4Jnfh5e91oymaJ2GIk3d690LTBRCSf5KIdjIcv7w8KaoSDg3K1Q
   2019-10-03 18:17:03,842 - dbm-agent.dbma.pusher.push_net_interfaces - MainThread - INFO - nifs = [NetInterface(name='ens33', speed=1000, isup=True, address='172.16.192.100')]
   2019-10-03 18:17:03,920 - dbm-agent.dbma.pusher.push_net_interfaces - MainThread - INFO - {'code': 200, 'message': '数据库中存在对应的网卡信息，更新成功', 'data': []}
   2019-10-03 18:17:03,920 - dbm-agent.dbma.pusher.push_net_interfaces - MainThread - INFO - net-interface push complete
   2019-10-03 18:17:03,921 - dbm-agent.dbma.pusher.push_net_io_counter - MainThread - INFO - prepare push net io counter info
   2019-10-03 18:17:03,921 - dbm-agent.dbma.pusher.push_net_io_counter - MainThread - INFO - query http://172.16.192.1:8080/dbmc/hosts/dde1f082-67fc-436f-a149-90a1fa4612c2/net-io-counters/?pk=-1 for get csrftoken
   2019-10-03 18:17:03,954 - dbm-agent.dbma.pusher.push_net_io_counter - MainThread - INFO - csrftoken = aj0KsWYk7ifp4EG2I0SZrKqy5PgRyRYZDHObjZXeI5n2AiIXjyzXm13I4WP89rmC
   2019-10-03 18:17:03,954 - dbm-agent.dbma.pusher.push_net_io_counter - MainThread - INFO - net io counter = OrderedDict([('bytes_sent', 656208), ('bytes_recv', 1946535), ('csrfmiddlewaretoken', 'aj0KsWYk7ifp4EG2I0SZrKqy5PgRyRYZDHObjZXeI5n2AiIXjyzXm13I4WP89rmC')])
   2019-10-03 18:17:04,035 - dbm-agent.dbma.pusher.push_net_io_counter - MainThread - INFO - {'code': 201, 'message': '新的网络监控数据插入成功', 'data': []}
   2019-10-03 18:17:04,036 - dbm-agent.dbma.pusher.push_memory_distribution - MainThread - INFO - prepare push memory distribution info to dbmc
   2019-10-03 18:17:04,036 - dbm-agent.dbma.pusher.push_memory_distribution - MainThread - INFO - query http://172.16.192.1:8080/dbmc/hosts/dde1f082-67fc-436f-a149-90a1fa4612c2/memory-distributions/?pk=-1 for csrftoken
   2019-10-03 18:17:04,070 - dbm-agent.dbma.pusher.push_memory_distribution - MainThread - INFO - csrftoken  = {csrfmiddlewaretoken}
   2019-10-03 18:17:04,070 - dbm-agent.dbma.pusher.push_memory_distribution - MainThread - INFO - data = {'csrfmiddlewaretoken': 'kL3EL09bXG8IaUgWsNlWp2qgDuJ2mZ2v7HQF7TJcgZPo0JLdjmKUvA5NDAekclBx', 'total': 1535696896, 'available': 1209077760, 'used': 169832448, 'free': 1201819648}
   2019-10-03 18:17:04,151 - dbm-agent.dbma.pusher.push_memory_distribution - MainThread - INFO - {'code': 200, 'message': '数据录入成功', 'data': []}
   2019-10-03 18:17:04,152 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - prepare push disk uasge info to dbmc
   2019-10-03 18:17:04,152 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - query http://172.16.192.1:8080/dbmc/hosts/dde1f082-67fc-436f-a149-90a1fa4612c2/disk-usages/?pk=-1 for csrftoken
   2019-10-03 18:17:04,190 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - csrftoken  = pmJM3v4itTxYdUX6vw7JzkCSEH9tOj5cIfamJuMJlzG8mVK7OWjlinKN45a8ya7f
   2019-10-03 18:17:04,191 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - data = {'csrfmiddlewaretoken': 'pmJM3v4itTxYdUX6vw7JzkCSEH9tOj5cIfamJuMJlzG8mVK7OWjlinKN45a8ya7f', 'mountpoint': '/', 'total': 53660876800, 'used': 5087141888, 'free': 48573734912}
   2019-10-03 18:17:04,270 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - data = {'csrfmiddlewaretoken': 'pmJM3v4itTxYdUX6vw7JzkCSEH9tOj5cIfamJuMJlzG8mVK7OWjlinKN45a8ya7f', 'mountpoint': '/database', 'total': 53660876800, 'used': 5087141888, 'free': 48573734912}
   2019-10-03 18:17:04,346 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - data = {'csrfmiddlewaretoken': 'pmJM3v4itTxYdUX6vw7JzkCSEH9tOj5cIfamJuMJlzG8mVK7OWjlinKN45a8ya7f', 'mountpoint': '/backup', 'total': 53660876800, 'used': 5087141888, 'free': 48573734912}
   2019-10-03 18:17:04,421 - dbm-agent.dbma.pusher.push_disk_usage - MainThread - INFO - push disk usage info complete
   2019-10-03 18:17:04,422 - dbm-agent.dbma.pusher.push_disk_io_counter - MainThread - INFO - prepare push disk io counter to dbmc
   2019-10-03 18:17:04,422 - dbm-agent.dbma.pusher.push_disk_io_counter - MainThread - INFO - query http://172.16.192.1:8080/dbmc/hosts/dde1f082-67fc-436f-a149-90a1fa4612c2/disk-io-counters/?pk=-1 for csrftoken
   2019-10-03 18:17:04,455 - dbm-agent.dbma.pusher.push_disk_io_counter - MainThread - INFO - csrftoken  = 619fGisKvlKQWeh4s23ZT7sl55xbCsedNtEuILTSsHlheeP8QUo7562HXOJBMUuN
   2019-10-03 18:17:04,456 - dbm-agent.dbma.pusher.push_disk_io_counter - MainThread - INFO - data = {'csrfmiddlewaretoken': '619fGisKvlKQWeh4s23ZT7sl55xbCsedNtEuILTSsHlheeP8QUo7562HXOJBMUuN', 'read_count': 10898, 'write_count': 9636, 'read_bytes': 308108288, 'write_bytes': 74499072}
   2019-10-03 18:17:04,534 - dbm-agent.dbma.pusher.push_disk_io_counter - MainThread - INFO - {'code': 200, 'message': '录入成功', 'data': []}
   2019-10-03 18:17:04,534 - dbm-agent.dbma.pusher.push_disk_io_counter - MainThread - INFO - push disk usage info complete
   ```
   ---


