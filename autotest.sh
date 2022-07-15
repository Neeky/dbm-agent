#!/bin/bash
#自动发现所有的测试用例
python3 -m unittest discover --start-directory tests/bil ${1}
python3 -m unittest discover --start-directory tests/installsoftwares ${1}
python3 -m unittest discover --start-directory tests/configrenders ${1}
# docker 镜像打包与运行
# docker build -t 1721900707/dbma:0.0.1.0 . && docker run --rm -it  1721900707/dbma:0.0.1.0 /bin/bash 

