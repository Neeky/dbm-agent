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
   - [备份](#备份)

---

## dbm-agent
  **dbm(DataBase Management center)-agent：MySQL 数据库管理中心客户端程序**

  **dbm-agent 的要解决什么问题**

  dbm-agent 是一个守护进程、就像一个安装上你 linux 主机上的 DBA、目前希望它能做到 MySQL 数据库的全生命周期管理，主要的功能如下表：
  
  |**功能ID(按在生命周期中出现的时候排序)**|**功能明细**|
  |---------|-----------|
  |1        | MySQL 单一实例安装与自动化参数调优 |
  |2        | MGR 高可用集群安装与自动化参数调优 |
  |3        | 备份计划的制定与自动化执行备份任务  |
  |4        | 自动化安装部署监控客户端          |
  |5        | DDL变更自动化(要在dbmc上提交任务) |
  |6        | 每日数据库性能报表(直接发到开发负责人 cc DBA)|
  |7        | 事态感知实时扩容与自动化性能优化    |
  |8        | 删库资源回收                    |

  我们希望只要用电可以解决的事绝对不动用人力，要只 dbm-agent 能够自动恢复的故障就绝对不要告警，通过监控就能提前预防的问题就绝对不能让它搞出事故。

  **dbm-agent 在实现上遵守的规范**
  |**规范ID**|规范内容|
  |----------|--------|
  |dbm-agent 工作目录位置 | /usr/local/dbm-agent |
  |mysql 配置文件保存的位置 | /etc/my-{port}.cnf |
  |systemd 配置文件保存的位置 | /usr/lib/systemd/system/mysqld-{port}.service |
  |数据目录   | /database/mysql/data/{port} |
  |备份目录   | /backup/mysql/{port} |
  |默认密码   | dbma@0352 |

  ---

  **dbm-agent 可以工作在两种状态**

  **1、守护进程模式** 这个要求与 dbm-center 配合使用，这样 DBA 就可以通过浏览器点点点完成 MySQL 的管理工作了

  **2、命令行脚本模式** 这个是一个比较轻量的使用方法，也就是说用户可以直接通过 dbm-agent 提供的命令完成 MySQL 的管理工作 


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
   pip3 install jinja2 psutil requests mysql-connector-python==8.0.17

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
   pip3 install dbm-agent==0.1.2

   Installing collected packages: dbm-agent
     Running setup.py install for dbm-agent ... done
   Successfully installed dbm-agent-0.1.2
   ```

   > pip3 是 python3 的一个包管理工具，类似于 centos 中的 yum ，版本号的最后一位是奇数表示它是一个开发版本，偶数表示它是一个稳定版本

   ---

## 初始化
   **要 dbm-agent 能运行起来还要有一些其它的工作要，比如创建 dbma 用户，创建工作目录 /usr/local/dbm-agent 和一些重要的配置文件。作为一个成熟的软件，这一切都是可以自动完成的。**
   ```bash
   # 由于要创建用户和目录，dbm-agent 需要 root 权限
   sudo su
   # init ，通过--dbmc-site 选项指定管理端的访问路径
   dbm-agent --dbmc-site=https://192.168.100.100 init
   #dbm-agent init compeleted .

   # 执行完成上面的步骤整个初始化就算完成了，实现上只是创建一些必要的用户，目录，文件 
   # 创建 dbma 用户
   grep dbm /etc/passwd    
   dbma:x:2048:2048::/home/dbma:/bin/bash
   
   # 创建如下目录结构
   tree /usr/local/dbm-agent/
   /usr/local/dbm-agent/
   ├── etc
   │   └── dbma.cnf
   ├── logs
   │   └── dbma.log
   └── pkgs

   # 创建配置文件，日志文件中会在直接运行的时候才长成
   cat /usr/local/dbm-agent/etc/dbma.cnf 
   
   [dbma]
   dbmc_site = https://192.168.100.100
   base_dir = /usr/local/dbm-agent/
   config_file = etc/dbma.cnf
   log_file = logs/dbma.log
   log_level = info
   user_name = dbma
   pid = /tmp/dbm-agent.pid
   ```

   ---

## 启动
   **dbm-agent 默认会自动以守护进程的方式运行**

   **1、** 启动
   ```bash
   dbm-agent start
   Successful start and log file save to '/usr/local/dbm-agent/logs/dbma.log'
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

## 备份
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


