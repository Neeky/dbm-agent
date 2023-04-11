#!/bin/bash


#--------------------------------------------#
# pip3 install pytest pytest-mock pytest-cov |
#--------------------------------------------#


rm -rf ./htmlcov/*
pytest --cov --cov-report=html

# 生成字符报表
pytest --cov -v

