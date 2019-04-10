# dbm-agent
  **dbm(DataBase Management center)-agent：MySQL 数据库管理中心客户端程序**

  ---

## 安装
   **安装方法一）：源码安装**
   ```bash
   sudo su

   cd dbm-agent
   # 先手工运行一下自动化测试用例，以确保你的平台有被支持

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
   # init 
   dbm-agent init
   # dbm-agent init compeleted .

   # 创建 dbma 用户
   grep dbm /etc/passwd    
   dbma:x:2048:2048::/home/dbma:/bin/bash
   
   # 创建如下目录结构
   tree /usr/local/dbm-agent/
   /usr/local/dbm-agent/
   |-- etc
   |-- logs
   `-- pkgs
   ```