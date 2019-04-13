
from distutils.core import setup
from dbma import config

setup(name='dbm-agent',
      version=config.__version,
      description='dbm-agent 数据库管理中心客户端程序',
      author="Neeky",
      author_email="neeky@live.com",
      maintainer='Neeky',
      maintainer_email='neeky@live.com',
      scripts=['bin/dbm-agent'],
      packages=['dbma','dbma.native','dbma.utils'],
      package_data={'dbma':['static/cnfs/*']},
      url='https://github.com/Neeky/dbm-agent',
      install_requires=['Jinja2>=2.10.1','mysql-connector-python==8.0.15'],
      python_requires='>=3.6.*',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7']
      )