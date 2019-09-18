#!/bin/bash
#自动发现所有的测试用例
python3 -m unittest discover --start-directory tests ${1}

# docker 镜像打包与运行
# docker build -t 1721900707/dbma:0.0.0.9 .
# docker run --rm -it  1721900707/dbma:0.0.0.9 /bin/bash
