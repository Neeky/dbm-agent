## 目录
---
- [目录](#目录)
- [dbm-愿景](#dbm-愿景)
- [安装-dbm-agent](#安装-dbm-agent)
- [MySQL-功能列表](#MySQL-功能列表)
- [Redis-功能列表](#Redis-功能列表)
- [关闭-dbm-agent](#关闭-dbm-agent)
- [规范](#规范)
- [源码安装](#源码安装)
- [官方微信公众平台](#官方微信公众平台)


---

## dbm-愿景
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


## 安装-dbm-agent
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

## MySQL-功能列表

MySQL 目前支持的功能列表如下

|**功能名**|**详细文档**|
|---------|-----------
|MySQL单机&主从安装配置| [安装配置-MySQL](./docs/mysql-01-auto-install.md)|
|MySQL备份|[备份-MySQL](./docs/mysql-02-auto-backup.md)|
|MySQL卸载|[卸载-MySQL](./docs/mysql-03-auto-uninstall.md)|
|MySQL清理|[清理-MySQL](./docs/mysql-04-clear-backup-files.md)|
|MySQLMGR| 开发中|
|高可用|开发中|

---

## Redis-功能列表

Redis 目前支持的功能列表如下
|**功能名**|**详细文档**|
|---------|-----------
|Redis-master-安装| [Redis-master-安装](./docs/redis-01-auto-install.md)|
|Redis-replica-安装|[Redis-replica-安装](./docs/redis-02-build-replica.md)|

---


## 关闭-dbm-agent
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

## 单元测试
为了尽可能的减少 BUG ，我们尽全力把单元测试的覆盖率推向 100%，目前来看只达到了 87% 
```bash
# 单元测试用到的依赖
# pip3 install pytest pytest-mock pytest-cov

# 运行单元测试
pytest --cov

... ... ... ... ...
---------- coverage: platform linux, python 3.11.3-final-0 -----------
Name                                             Stmts   Miss  Cover
--------------------------------------------------------------------
dbma/__init__.py                                     0      0   100%
dbma/bil/__init__.py                                 1      0   100%
dbma/bil/cmdexecutor.py                              6      0   100%
dbma/bil/daemon.py                                  66     36    45%
dbma/bil/fs.py                                      56     25    55%
dbma/bil/fun.py                                      4      0   100%
dbma/bil/net.py                                     12      1    92%
dbma/bil/osuser.py                                 139      0   100%
dbma/bil/sudos.py                                   12      0   100%
dbma/components/__init__.py                          0      0   100%
dbma/components/mysql/__init__.py                    0      0   100%
dbma/components/mysql/asserts.py                    24      1    96%
dbma/components/mysql/backends/__init__.py           0      0   100%
dbma/components/mysql/backends/clears.py           119     31    74%
dbma/components/mysql/commons.py                   137     73    47%
dbma/components/mysql/config.py                    387    116    70%
dbma/components/mysql/exceptions.py                 16      0   100%
dbma/components/mysql/install.py                   194     19    90%
dbma/components/orchestrator/__init__.py             0      0   100%
dbma/components/orchestrator/exceptions.py           6      0   100%
dbma/components/orchestrator/install.py             40     22    45%
dbma/core/__init__.py                                0      0   100%
dbma/core/configs.py                                78     14    82%
dbma/core/exception.py                              13      0   100%
dbma/core/messages.py                               13      0   100%
dbma/core/threads/__init__.py                        0      0   100%
dbma/core/threads/backends.py                       31     16    48%
dbma/version.py                                      7      0   100%
--------------------------------------------------------------------
TOTAL                                             2180    361    83%
```
---

## 源码安装
```bash
# 生成 tar.gz 格式的安装包
cd dbm-agent
python3 setup.py sdist

# 执行安装
cd dist
pip3 install ./dbm-agent-8.33.10.tar.gz
```
---

## 官方微信公众平台 

![官方微信公众平台](imgs/mp-wechat.jpg)

---