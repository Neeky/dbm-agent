# dbm-agent
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

  我们希望只要用电可以解决的事绝对不动用人力，要只自己能够恢复的故障就绝对不要告警，通过监控就能提前预防的问题就绝对不能让它搞出事故。


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
