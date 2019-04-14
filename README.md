# dbm-agent
  **dbm(DataBase Management center)-agent：MySQL 数据库管理中心客户端程序**

  ---

## 安装
   **安装方法一）：源码安装**
   ```bash
   sudo su
   # 安装依赖
   pip3 install jinja2 psutil mysql-connector-python==8.0.15

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
   **要 dbm-agent 能运行起来还要有一些其它的工作要，比如创建 dbma 用户，创建工作目录 /usr/local/dbma-agent 和一些重要的配置文件。作为一个成熟的软件，这一切都是可以自动完成的。**
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
   |-- etc
   |   |-- cnfs
   |   |   |-- 5_7.cnf.jinja
   |   |   |-- 8_0.cnf.jinja
   |   |   `-- mysqld.service.jinja
   |   `-- dbma.cnf
   |-- logs
   `-- pkgs

   # 创建配置文件，日志文件中会在直接运行的时候才长成
   cat /usr/local/dbm-agent/etc/dbmc.cnf 
   
   [dbma]
   dbmc_site          = https://192.168.100.100                # web 管理端的地址
   dbma_uuid          = 87de08f8-5c1f-11e9-a293-0242ac110003   # dbmauuid 为每一个 dbm-agent 分配一个唯一的 id 用来标识它
   log_file           = ./logs/dbma.log   
   ```