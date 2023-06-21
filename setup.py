import os
from setuptools import setup


def get_version():
    """
    动态获取 dbm-agent 的版本号
    """

    project_dir_name = os.path.dirname(__file__)
    version_file_path = os.path.join(project_dir_name, "dbma/version.py")
    with open(version_file_path) as version_file_obj:
        content = version_file_obj.read()

    g = {}

    exec(content, g, g)
    return g["VERSION"]


agent_version = get_version()

setup(
    name="dbm-agent",
    version=agent_version,
    description="dbm-agent 数据库管理中心客户端程序",
    author="Neeky",
    author_email="neeky@live.com",
    maintainer="Neeky",
    maintainer_email="neeky@live.com",
    scripts=[
        "bin/dbm-agent",
        "bin/dbma-cli-init",
        "bin/dbma-cli-mysql",
        "bin/dbma-cli-redis",
        "bin/dbm-bt-conn-stack",
    ],
    packages=[
        "dbma",
        "dbma/core",
        "dbma/core/views",
        "dbma/core/agent",
        "dbma/core/threads",
        "dbma/bil",
        "dbma/components",
        "dbma/components/mysql",
        "dbma/components/mysql/views",
        "dbma/components/mysql/backups",
        "dbma/components/mysql/backends",
        "dbma/components/redis",
        "dbma/components/orchestrator",
    ],
    package_data={"dbma": ["static/cnfs/*", "static/sql-scripts/*"]},
    url="https://github.com/Neeky/dbm-agent",
    install_requires=[
        "mysql-connector-python>=8.0.31",
        "redis>=4.5.4",
        "aiohttp>=3.8.1",
        "requests>=2.22.0",
        "Jinja2>=2.10.1",
        "psutil>=5.6.6",
        "distro>=1.4.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
