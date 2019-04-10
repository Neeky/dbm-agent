
from distutils.core import setup

setup(name='dbmc-agent',
      version='0.0.0.0',
      description='dbm-agent 数据库管理中心客户端程序',
      author="Neeky",
      author_email="neeky@live.com",
      maintainer='Neeky',
      maintainer_email='neeky@live.com',
      scripts=['bin/dbm-agent'],
      packages=['dbma','dbma.native','dbma.utils'],
      url='https://github.com/Neeky/dbm-agent',
      python_requires='>=3.6.*,',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7']
      )