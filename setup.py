import os
import re
from setuptools import setup


def get_version():
    """
    提取出 dbma/version.py 中的 agent_version 
    """
    base = os.path.dirname(__file__)
    version_file = os.path.join(base, 'dbma/version.py')
    with open(version_file) as f:
        line = f.readline()

    m = re.search(r'\d*\.\d*\.\d*', line)

    if m:
        return m.group(0)
    else:
        return '0.0.0'


agent_version = get_version()

setup(name='dbm-agent',
      version=agent_version,
      description='dbm-agent 数据库管理中心客户端程序',
      author="Neeky",
      author_email="neeky@live.com",
      maintainer='Neeky',
      maintainer_email='neeky@live.com',
      scripts=['bin/dbm-agent', 'bin/dbma-cli-single-instance', 'bin/dbma-cli-install-mysqlsh',
               'bin/dbma-cli-build-slave', 'bin/dbma-cli-build-mgr', 'bin/dbma-cli-clone-instance',
               'bin/dbm-monitor-gateway', 'bin/dbma-cli-zabbix-agent', 'bin/dbma-cli-mysql-monitor-item',
               'bin/dbma-cli-backup-instance', 'bin/dbma-cli-install-backuptool', 'bin/dbm-backup-proxy'],
      packages=['dbma'],
      package_data={'dbma': ['static/cnfs/*', 'static/sql-scripts/*']},
      url='https://github.com/Neeky/dbm-agent',
      install_requires=['Jinja2>=2.10.1', 'mysql-connector-python>=8.0.18',
                        'psutil>=5.6.6', 'requests>=2.22.0', 'distro>=1.4.0'],
      python_requires='>=3.6.*',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8']
      )
