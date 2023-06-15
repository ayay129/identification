#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-06-06 15:17
# @Author: Rangers
# @Site: 
# @File: __init__.py.py
from aip import AipOcr,AipImageProcess
from core.parser import YamlParser
import os

yaml_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
# 初始化配置
connect_cfg = YamlParser(config=os.path.join(yaml_dir, "api.yaml")).json

baidu_ocr_env = connect_cfg.get("baidu_ocr")

baidu_client = AipOcr(str(baidu_ocr_env["app_id"]), str(baidu_ocr_env["api_key"]), str(baidu_ocr_env["secret_key"]))
baidu_image_client = AipImageProcess(str(baidu_ocr_env["app_id"]), str(baidu_ocr_env["api_key"]), str(baidu_ocr_env["secret_key"]))

