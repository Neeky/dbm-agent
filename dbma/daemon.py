import os
import sys
import stat
import time
import fcntl
import errno
import signal
import argparse
from datetime import datetime
import atexit


__ALL__ = ['start_daemon', 'stop_daemon']


def auto_clean_pid(fileno, pid_file):
    """
    当程序自动退出时清理 pid 文件
    """
    os.close(fileno)
    os.remove(pid_file)


def signal_handler(sig, _):
    """定义信息处理逻辑
    """
    if sig == signal.SIGINT or sig == signal.SIGTERM:
        # signal.SIGINT == 2
        # signal.SIGTERM == 15
        sys.exit(1)


def write_pid_file(pid, pid_file):
    """创建 pid 文件并向其中写入 pid，成功返回 0 异常返回 1
    """
    # 取得 pid 文件的文件描述符
    pid_desc = os.open(pid_file, os.O_CREAT | os.O_RDWR,
                       stat.S_IRUSR | stat.S_IWUSR)
    try:
        fcntl.lockf(pid_desc, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as err:
        # 排他访问有异常的话，说明已经有一个守护进程在运行了
        print(err)
        return 1
    # 如果能运行到这里说明排他访问是正常的
    # 清空 pid 文件
    os.truncate(pid_desc, 0)
    s_pid = str(pid)
    os.write(pid_desc, s_pid.encode('utf8'))
    atexit.register(auto_clean_pid, pid_desc, pid_file)
    return 0
    # 注意 pid 文件不应该被 close ，因为如果 close 的话其它进程就查询不到是否有进程在用着它了，pid 文件应该是独占的


def start_server(pid_file="/tmp/daemon.pid"):
    """启动服务并把 pid 写入到 pid 文件
    """
    # 注册信号处理函数
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    pid = os.fork()

    # 如果 pid 大于 0 说明这个进程是父进程
    if pid > 0:
        # 等待 5s 这样子进程就应该已经启动了，于是退出父进程
        time.sleep(5)
        sys.exit(0)

    # 如果是父进程它上一个 if 就已经退出了，所以不不会执行到这个，也就是说下面的代码都是子进程的逻辑
    ppid = os.getppid()  # 获取父进程的 id
    pid = os.getpid()   # 获取自己的进程 id

    if write_pid_file(pid, pid_file) != 0:
        # 如果执行到这里说明守护进程已经存在了
        # 那么要退出父进程、退出当前进程
        os.kill(ppid, signal.SIGTERM)
        sys.exit(1)

    # 如果能执行到这里说明当前主机上没有本程序对应的守护进程在运行
    os.setsid()  # 独立成一个新的session,如果不重新设置的会那么session断开之后这个session下的所有进程都会退出。
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    os.kill(ppid, signal.SIGTERM)  # 主动的kill父进程
    # 后台运行不要接收键盘输入
    sys.stdin.close()


def stop_server(pid_file="/tmp/daemon.pid"):
    """退出守护进程并删除 pid 文件,并且退出当前程序
    """
    try:
        with open(pid_file) as pid_file_ojb:
            s_pid = pid_file_ojb.read()
    except IOError as err:
        # pid 文件都不存在所以守护进程也是不存在的，也就没有必要 kill 它了
        sys.exit(0)
    pid = int(s_pid)
    for i in range(100):
        # kill 100 次，如果都失败了就报 kill 不掉
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as err:
            if err.errno == errno.ESRCH:
                print("Successful exit")
                break  # 说明上一次已经 kill 成功了
        time.sleep(0.02)
    else:
        sys.exit(1)
    # 删除 pid 文件
    if os.path.isfile(pid_file):
        # 如果守护进程已经主动清理了，那我们就不清理了
        os.remove(pid_file)
    sys.exit(0)


start_daemon = start_server
stop_daemon = stop_server
