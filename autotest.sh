#!/bin/bash
#自动发现所有的测试用例
pytest --cov --cov-report=html
pytest --cov -v

