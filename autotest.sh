#!/bin/bash
#自动发现所有的测试用例
# 生成 html 报表
pytest --cov --cov-report=html

# 生成字符报表
pytest --cov -v

