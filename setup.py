
from distutils.core import setup
from dbma import __dbma_version

setup(name='dbm-agent',
      version=__dbma_version,
      description='dbm-agent 数据库管理中心客户端程序',
      author="Neeky",
      author_email="neeky@live.com",
      maintainer='Neeky',
      maintainer_email='neeky@live.com',
      scripts=['bin/dbm-agent','bin/dbma-cli-single-instance','bin/dbma-cli-backup-instance'],
      packages=['dbma'],
      package_data={'dbma':['static/cnfs/*']},
      url='https://github.com/Neeky/dbm-agent',
      install_requires=['Jinja2>=2.10.1','mysql-connector-python>=8.0.17','psutil>=5.6.1','requests>=2.22.0'],
      python_requires='>=3.6.*',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7']
      )